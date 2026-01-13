"""
Test HTML optimizer component
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.html_optimizer import HTMLOptimizer
from src.config import Settings
from src.llm_client import LLMClient


class TestHTMLOptimizer:
    """Test HTML optimization functionality"""
    
    @pytest.fixture
    def optimizer(self, mock_settings):
        """Create HTML optimizer instance"""
        with patch('src.html_optimizer.LLMClient') as mock_llm_class:
            mock_llm = MagicMock()
            mock_llm.generate = AsyncMock(return_value="<html><body><button id='btn'>Click</button></body></html>")
            mock_llm_class.return_value = mock_llm
            return HTMLOptimizer(mock_settings)
    
    async def test_optimize_removes_scripts_and_styles(self, optimizer, sample_html):
        """Test that HTML optimization removes scripts and styles"""
        with patch.object(optimizer.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "<html><body><button id='login-btn'>Login</button></body></html>"
            
            result = await optimizer.optimize(
                html=sample_html,
                url="https://example.com",
                task_context="Click login button"
            )
            
            # Verify LLM was called with optimization prompt
            assert mock_gen.called
            call_args = mock_gen.call_args
            assert "script" in call_args[0][0].lower() or "style" in call_args[0][0].lower()
            assert sample_html in call_args[0][0]
            
            # Verify result is cleaned
            assert result == "<html><body><button id='login-btn'>Login</button></body></html>"
    
    async def test_optimize_preserves_interactive_elements(self, optimizer):
        """Test that interactive elements are preserved"""
        html_with_interactive = """
        <html>
            <body>
                <button id="submit-btn">Submit</button>
                <input type="text" id="username">
                <a href="/link">Link</a>
                <form id="my-form">
                    <select id="dropdown">
                        <option value="1">Option 1</option>
                    </select>
                </form>
            </body>
        </html>
        """
        
        optimized_result = """
        <html>
            <body>
                <button id="submit-btn">Submit</button>
                <input type="text" id="username">
                <a href="/link">Link</a>
                <form id="my-form">
                    <select id="dropdown">
                        <option value="1">Option 1</option>
                    </select>
                </form>
            </body>
        </html>
        """
        
        with patch.object(optimizer.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = optimized_result
            
            result = await optimizer.optimize(
                html=html_with_interactive,
                url="https://example.com"
            )
            
            # Verify prompt mentions preserving interactive elements
            prompt = mock_gen.call_args[0][0]
            assert "interactive" in prompt.lower() or "button" in prompt.lower()
            assert "input" in prompt.lower() or "form" in prompt.lower()
    
    async def test_optimize_with_task_context(self, optimizer, sample_html):
        """Test optimization with task context for better results"""
        with patch.object(optimizer.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "<html><body><button id='login-btn'>Login</button></body></html>"
            
            await optimizer.optimize(
                html=sample_html,
                url="https://example.com",
                task_context="Click the login button"
            )
            
            # Verify task context is included in prompt
            prompt = mock_gen.call_args[0][0]
            assert "Click the login button" in prompt
            assert "Task Context" in prompt
    
    async def test_optimize_strips_whitespace(self, optimizer):
        """Test that result is properly stripped"""
        with patch.object(optimizer.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "   <html><body>Content</body></html>   "
            
            result = await optimizer.optimize(
                html="<html><body>Content</body></html>",
                url="https://example.com"
            )
            
            # Verify whitespace is stripped
            assert result == "<html><body>Content</body></html>"
            assert not result.startswith(" ")
            assert not result.endswith(" ")
    
    async def test_optimize_preserves_ids_and_classes(self, optimizer):
        """Test that element IDs and classes are preserved"""
        html_with_ids = """
        <html>
            <body>
                <div id="main-container" class="container">
                    <button id="action-btn" class="btn btn-primary" data-action="submit">
                        Click Me
                    </button>
                </div>
            </body>
        </html>
        """
        
        with patch.object(optimizer.llm_client, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = html_with_ids
            
            result = await optimizer.optimize(
                html=html_with_ids,
                url="https://example.com"
            )
            
            # Verify prompt mentions preserving IDs and classes
            prompt = mock_gen.call_args[0][0]
            assert "id" in prompt.lower() or "class" in prompt.lower()
            assert "preserve" in prompt.lower() or "keep" in prompt.lower()

