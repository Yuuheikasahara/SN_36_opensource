"""
Test action generator component
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.action_generator import ActionGenerator
from src.config import Settings


class TestActionGenerator:
    """Test action generation functionality"""
    
    @pytest.fixture
    def generator(self, mock_settings):
        """Create action generator instance"""
        with patch('src.action_generator.LLMClient') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.generate = AsyncMock(return_value="click #login-btn")
            mock_llm_class.return_value = mock_llm
            return ActionGenerator(mock_settings)
    
    async def test_generate_action_basic(self, generator):
        """Test basic action generation"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "click #login-button"
            
            action = await generator.generate_action(
                prompt="Click the login button",
                optimized_html="<html><body><button id='login-button'>Login</button></body></html>",
                step_index=0,
                history=[],
                url="https://example.com"
            )
            
            assert action == "click #login-button"
            assert mock_gen.called
            
            # Verify prompt contains task and HTML
            prompt = mock_gen.call_args[0][0]
            assert "Click the login button" in prompt
            assert "login-button" in prompt
    
    async def test_generate_action_with_history(self, generator, sample_history):
        """Test action generation with history context"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "type #username testuser"
            
            action = await generator.generate_action(
                prompt="Login with username testuser",
                optimized_html="<html><body><input id='username'></body></html>",
                step_index=2,
                history=sample_history,
                url="https://example.com/login"
            )
            
            assert action == "type #username testuser"
            
            # Verify history is included in prompt
            prompt = mock_gen.call_args[0][0]
            assert "Previous Actions" in prompt
            assert "navigate https://example.com" in prompt or "Step 1" in prompt
            assert "click #login-btn" in prompt or "Step 2" in prompt
    
    async def test_generate_action_formats_history(self, generator):
        """Test that history is properly formatted"""
        history = [
            {"action": "navigate https://example.com", "result": "Page loaded"},
            {"action": "click #button", "result": "Button clicked"}
        ]
        
        formatted = generator._format_history(history)
        
        assert "Step 1" in formatted
        assert "Step 2" in formatted
        assert "navigate https://example.com" in formatted
        assert "click #button" in formatted
        assert "Page loaded" in formatted
        assert "Button clicked" in formatted
    
    async def test_generate_action_empty_history(self, generator):
        """Test action generation with empty history"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "navigate https://example.com"
            
            action = await generator.generate_action(
                prompt="Navigate to example.com",
                optimized_html="<html><body></body></html>",
                step_index=0,
                history=[],
                url="https://example.com"
            )
            
            assert action == "navigate https://example.com"
            
            # Verify empty history is handled
            prompt = mock_gen.call_args[0][0]
            assert "No previous actions" in prompt or "Previous Actions" in prompt
    
    async def test_generate_action_includes_step_index(self, generator):
        """Test that step index is included in prompt"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "click #next"
            
            await generator.generate_action(
                prompt="Complete task",
                optimized_html="<html><body></body></html>",
                step_index=5,
                history=[],
                url="https://example.com"
            )
            
            prompt = mock_gen.call_args[0][0]
            assert "Step: 5" in prompt or "step_index: 5" in prompt or "step 5" in prompt.lower()
    
    async def test_generate_action_strips_result(self, generator):
        """Test that action result is properly stripped"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "   click #button   "
            
            action = await generator.generate_action(
                prompt="Click button",
                optimized_html="<html><body><button id='button'></body></html>",
                step_index=0,
                history=[],
                url="https://example.com"
            )
            
            assert action == "click #button"
            assert not action.startswith(" ")
            assert not action.endswith(" ")
    
    async def test_action_types_in_prompt(self, generator):
        """Test that available action types are mentioned in prompt"""
        with patch.object(generator.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "click #btn"
            
            await generator.generate_action(
                prompt="Test",
                optimized_html="<html><body></body></html>",
                step_index=0,
                history=[],
                url="https://example.com"
            )
            
            prompt = mock_gen.call_args[0][0]
            assert "click" in prompt.lower()
            assert "type" in prompt.lower()
            assert "navigate" in prompt.lower()
            assert "done" in prompt.lower()

