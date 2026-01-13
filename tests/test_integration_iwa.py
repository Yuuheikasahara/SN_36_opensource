"""
Integration tests simulating full IWA benchmark behavior
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from main import app


class TestIWAIntegration:
    """Integration tests that simulate complete IWA benchmark scenarios"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_autocinema_login_flow(self, client):
        """Simulate Autocinema login task flow"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            # Step 1: Navigate to login
            mock_opt.return_value = "<html><body><a href='/login' id='login-link'>Login</a></body></html>"
            mock_gen.return_value = "click #login-link"
            
            step1 = {
                "task_id": "autocinema_001",
                "prompt": "Login to Autocinema with username 'testuser' and password 'testpass'",
                "start_url": "https://autocinema.example.com",
                "snapshot_html": "<html><body><a href='/login' id='login-link'>Login</a></body></html>",
                "step_index": 0,
                "web_project_id": "autocinema",
                "history": []
            }
            
            r1 = client.post("/act", json=step1)
            assert r1.status_code == 200
            assert r1.json()["action"] == "click #login-link"
            
            # Step 2: Fill username
            mock_opt.return_value = "<html><body><form id='login-form'><input id='username'><input id='password'><button type='submit'>Login</button></form></body></html>"
            mock_gen.return_value = "type #username testuser"
            
            step2 = {
                **step1,
                "start_url": "https://autocinema.example.com/login",
                "snapshot_html": "<html><body><form id='login-form'><input id='username'><input id='password'><button type='submit'>Login</button></form></body></html>",
                "step_index": 1,
                "history": [{"action": "click #login-link", "result": "Login page loaded"}]
            }
            
            r2 = client.post("/act", json=step2)
            assert r2.status_code == 200
            assert r2.json()["action"] == "type #username testuser"
            
            # Step 3: Fill password
            mock_gen.return_value = "type #password testpass"
            
            step3 = {
                **step2,
                "snapshot_html": "<html><body><form id='login-form'><input id='username' value='testuser'><input id='password'><button type='submit'>Login</button></form></body></html>",
                "step_index": 2,
                "history": [
                    {"action": "click #login-link", "result": "Login page loaded"},
                    {"action": "type #username testuser", "result": "Username entered"}
                ]
            }
            
            r3 = client.post("/act", json=step3)
            assert r3.status_code == 200
            assert r3.json()["action"] == "type #password testpass"
            
            # Step 4: Submit
            mock_gen.return_value = "submit #login-form"
            
            step4 = {
                **step3,
                "snapshot_html": "<html><body><form id='login-form'><input id='username' value='testuser'><input id='password' value='testpass'><button type='submit'>Login</button></form></body></html>",
                "step_index": 3,
                "history": [
                    {"action": "click #login-link", "result": "Login page loaded"},
                    {"action": "type #username testuser", "result": "Username entered"},
                    {"action": "type #password testpass", "result": "Password entered"}
                ]
            }
            
            r4 = client.post("/act", json=step4)
            assert r4.status_code == 200
            assert r4.json()["action"] == "submit #login-form"
    
    def test_autobook_search_flow(self, client):
        """Simulate Autobook search task flow"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            # Step 1: Navigate to search
            mock_opt.return_value = "<html><body><input id='search-box' placeholder='Search books'><button id='search-btn'>Search</button></body></html>"
            mock_gen.return_value = "type #search-box Python Programming"
            
            step1 = {
                "task_id": "autobook_001",
                "prompt": "Search for 'Python Programming' book",
                "start_url": "https://autobook.example.com",
                "snapshot_html": "<html><body><input id='search-box' placeholder='Search books'><button id='search-btn'>Search</button></body></html>",
                "step_index": 0,
                "web_project_id": "autobook",
                "history": []
            }
            
            r1 = client.post("/act", json=step1)
            assert r1.status_code == 200
            assert "Python Programming" in r1.json()["action"]
            
            # Step 2: Click search button
            mock_opt.return_value = "<html><body><input id='search-box' value='Python Programming'><button id='search-btn'>Search</button></body></html>"
            mock_gen.return_value = "click #search-btn"
            
            step2 = {
                **step1,
                "snapshot_html": "<html><body><input id='search-box' value='Python Programming'><button id='search-btn'>Search</button></body></html>",
                "step_index": 1,
                "history": [{"action": "type #search-box Python Programming", "result": "Search term entered"}]
            }
            
            r2 = client.post("/act", json=step2)
            assert r2.status_code == 200
            assert r2.json()["action"] == "click #search-btn"
            
            # Step 3: View results
            mock_opt.return_value = "<html><body><div class='book-result'><h3>Python Programming</h3><button class='view-details'>View Details</button></div></body></html>"
            mock_gen.return_value = "click .view-details"
            
            step3 = {
                **step2,
                "start_url": "https://autobook.example.com/search?q=Python+Programming",
                "snapshot_html": "<html><body><div class='book-result'><h3>Python Programming</h3><button class='view-details'>View Details</button></div></body></html>",
                "step_index": 2,
                "history": [
                    {"action": "type #search-box Python Programming", "result": "Search term entered"},
                    {"action": "click #search-btn", "result": "Search results loaded"}
                ]
            }
            
            r3 = client.post("/act", json=step3)
            assert r3.status_code == 200
            assert r3.json()["action"] == "click .view-details"
    
    def test_multiple_web_projects(self, client):
        """Test that agent handles different web projects correctly"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            mock_opt.return_value = "<html><body><div>Content</div></body></html>"
            mock_gen.return_value = "click #button"
            
            projects = ["autocinema", "autobook", "shopping", "social"]
            
            for project in projects:
                task = {
                    "task_id": f"{project}_test",
                    "prompt": "Complete task",
                    "start_url": f"https://{project}.example.com",
                    "snapshot_html": "<html><body><div>Content</div></body></html>",
                    "step_index": 0,
                    "web_project_id": project,
                    "history": []
                }
                
                response = client.post("/act", json=task)
                assert response.status_code == 200
                # Response doesn't include web_project_id, only action, task_id, step_index
                assert "action" in response.json()
                assert response.json()["task_id"] == f"{project}_test"
    
    def test_task_completion_detection(self, client):
        """Test that agent can detect task completion"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            mock_opt.return_value = "<html><body><h1>Task Complete</h1></body></html>"
            mock_gen.return_value = "done"
            
            task = {
                "task_id": "complete_task_001",
                "prompt": "Complete a simple task",
                "start_url": "https://example.com",
                "snapshot_html": "<html><body><h1>Task Complete</h1></body></html>",
                "step_index": 5,
                "web_project_id": "test",
                "history": [
                    {"action": "action1", "result": "result1"},
                    {"action": "action2", "result": "result2"}
                ]
            }
            
            response = client.post("/act", json=task)
            assert response.status_code == 200
            assert response.json()["action"] == "done"
    
    def test_error_recovery(self, client):
        """Test that agent can recover from errors"""
        with patch('main.html_optimizer.optimize', new_callable=AsyncMock) as mock_opt, \
             patch('main.action_generator.generate_action', new_callable=AsyncMock) as mock_gen:
            
            # First call fails
            mock_opt.side_effect = [Exception("Temporary error"), "<html><body>Success</body></html>"]
            mock_gen.return_value = "click #retry"
            
            task = {
                "task_id": "error_recovery_001",
                "prompt": "Handle error",
                "start_url": "https://example.com",
                "snapshot_html": "<html><body>Content</body></html>",
                "step_index": 0,
                "web_project_id": "test",
                "history": []
            }
            
            # First attempt fails
            r1 = client.post("/act", json=task)
            assert r1.status_code == 500
            
            # Second attempt succeeds
            r2 = client.post("/act", json=task)
            assert r2.status_code == 200

