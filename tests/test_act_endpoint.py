"""
Test the /act endpoint simulating IWA benchmark behavior
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from main import app
from src.html_optimizer import HTMLOptimizer
from src.action_generator import ActionGenerator
from src.config import Settings


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_settings():
    """Mock settings"""
    settings = Settings(
        llm_provider="openai",
        openai_api_key="test-key"
    )
    return settings


class TestActEndpoint:
    """Test the /act endpoint that receives tasks from IWA"""
    
    @patch('main.html_optimizer')
    @patch('main.action_generator')
    async def test_act_endpoint_success(self, mock_action_gen, mock_html_opt, client, sample_task_data):
        """Test successful /act endpoint call simulating IWA"""
        # Mock the HTML optimizer
        mock_html_opt.optimize = AsyncMock(return_value="<html><body><button id='login-btn'>Login</button></body></html>")
        
        # Mock the action generator
        mock_action_gen.generate_action = AsyncMock(return_value="click #login-btn")
        
        # Send request as IWA would
        response = client.post("/act", json=sample_task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "click #login-btn"
        assert data["task_id"] == "task_123"
        assert data["step_index"] == 0
        
        # Verify methods were called
        mock_html_opt.optimize.assert_called_once()
        mock_action_gen.generate_action.assert_called_once()
    
    def test_act_endpoint_with_history(self, client):
        """Test /act endpoint with action history (simulating multi-step IWA task)"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            mock_opt.return_value = "<html><body><input id='username'></body></html>"
            mock_gen.return_value = "type #username testuser"
            
            task_data = {
                "task_id": "task_456",
                "prompt": "Login with username testuser",
                "start_url": "https://example.com/login",
                "snapshot_html": "<html><body><input id='username'></body></html>",
                "step_index": 1,
                "web_project_id": "project_1",
                "history": [
                    {"action": "click #login-btn", "result": "Login form opened"}
                ]
            }
            
            response = client.post("/act", json=task_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["action"] == "type #username testuser"
            assert data["task_id"] == "task_456"
            assert data["step_index"] == 1
            
            # Verify history was passed to action generator
            call_args = mock_gen.call_args
            assert call_args[1]["history"] == task_data["history"]
    
    def test_act_endpoint_error_handling(self, client, sample_task_data):
        """Test error handling in /act endpoint"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt:
            mock_opt.side_effect = Exception("LLM API error")
            
            response = client.post("/act", json=sample_task_data)
            
            assert response.status_code == 500
            assert "Error processing action" in response.json()["detail"]
    
    def test_act_endpoint_validation(self, client):
        """Test request validation"""
        # Missing required field
        invalid_data = {
            "task_id": "task_123",
            "prompt": "Test task"
            # Missing other required fields
        }
        
        response = client.post("/act", json=invalid_data)
        assert response.status_code == 422  # Validation error


class TestIWASimulation:
    """Simulate full IWA benchmark task flow"""
    
    def test_iwa_task_flow_complete(self, client):
        """Simulate a complete IWA task from start to finish"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            # Step 1: Initial navigation
            mock_opt.return_value = "<html><body><a href='/login'>Login</a></body></html>"
            mock_gen.return_value = "navigate https://example.com/login"
            
            step1_data = {
                "task_id": "iwa_task_001",
                "prompt": "Navigate to the login page",
                "start_url": "https://example.com",
                "snapshot_html": "<html><body><a href='/login'>Login</a></body></html>",
                "step_index": 0,
                "web_project_id": "autocinema",
                "history": []
            }
            
            response1 = client.post("/act", json=step1_data)
            assert response1.status_code == 200
            assert response1.json()["action"] == "navigate https://example.com/login"
            
            # Step 2: Fill username
            mock_opt.return_value = "<html><body><input id='username'><input id='password'></body></html>"
            mock_gen.return_value = "type #username myuser"
            
            step2_data = {
                "task_id": "iwa_task_001",
                "prompt": "Navigate to the login page",
                "start_url": "https://example.com/login",
                "snapshot_html": "<html><body><input id='username'><input id='password'></body></html>",
                "step_index": 1,
                "web_project_id": "autocinema",
                "history": [
                    {"action": "navigate https://example.com/login", "result": "Login page loaded"}
                ]
            }
            
            response2 = client.post("/act", json=step2_data)
            assert response2.status_code == 200
            assert response2.json()["action"] == "type #username myuser"
            
            # Step 3: Fill password and submit
            mock_gen.return_value = "type #password mypass"
            
            step3_data = {
                "task_id": "iwa_task_001",
                "prompt": "Navigate to the login page",
                "start_url": "https://example.com/login",
                "snapshot_html": "<html><body><input id='username' value='myuser'><input id='password'></body></html>",
                "step_index": 2,
                "web_project_id": "autocinema",
                "history": [
                    {"action": "navigate https://example.com/login", "result": "Login page loaded"},
                    {"action": "type #username myuser", "result": "Username entered"}
                ]
            }
            
            response3 = client.post("/act", json=step3_data)
            assert response3.status_code == 200
            assert response3.json()["action"] == "type #password mypass"
            
            # Step 4: Submit form
            mock_gen.return_value = "submit #login-form"
            
            step4_data = {
                "task_id": "iwa_task_001",
                "prompt": "Navigate to the login page",
                "start_url": "https://example.com/login",
                "snapshot_html": "<html><body><form id='login-form'><input id='username' value='myuser'><input id='password' value='mypass'><button type='submit'>Login</button></form></body></html>",
                "step_index": 3,
                "web_project_id": "autocinema",
                "history": [
                    {"action": "navigate https://example.com/login", "result": "Login page loaded"},
                    {"action": "type #username myuser", "result": "Username entered"},
                    {"action": "type #password mypass", "result": "Password entered"}
                ]
            }
            
            response4 = client.post("/act", json=step4_data)
            assert response4.status_code == 200
            assert response4.json()["action"] == "submit #login-form"
            
            # Step 5: Task complete
            mock_gen.return_value = "done"
            
            step5_data = {
                "task_id": "iwa_task_001",
                "prompt": "Navigate to the login page",
                "start_url": "https://example.com/dashboard",
                "snapshot_html": "<html><body><h1>Welcome to Dashboard</h1></body></html>",
                "step_index": 4,
                "web_project_id": "autocinema",
                "history": [
                    {"action": "navigate https://example.com/login", "result": "Login page loaded"},
                    {"action": "type #username myuser", "result": "Username entered"},
                    {"action": "type #password mypass", "result": "Password entered"},
                    {"action": "submit #login-form", "result": "Logged in successfully"}
                ]
            }
            
            response5 = client.post("/act", json=step5_data)
            assert response5.status_code == 200
            assert response5.json()["action"] == "done"
    
    def test_iwa_max_steps_simulation(self, client):
        """Simulate IWA task reaching max steps"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            mock_opt.return_value = "<html><body><div>Content</div></body></html>"
            mock_gen.return_value = "click #next-button"
            
            # Simulate high step index (approaching max steps)
            task_data = {
                "task_id": "iwa_task_002",
                "prompt": "Complete a complex task",
                "start_url": "https://example.com",
                "snapshot_html": "<html><body><div>Content</div></body></html>",
                "step_index": 49,  # Near max steps
                "web_project_id": "autobook",
                "history": [{"action": f"action_{i}", "result": "result"} for i in range(49)]
            }
            
            response = client.post("/act", json=task_data)
            assert response.status_code == 200
            assert response.json()["step_index"] == 49

