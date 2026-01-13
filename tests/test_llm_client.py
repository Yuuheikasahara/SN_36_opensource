"""
Test LLM client component
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.llm_client import LLMClient
from src.config import Settings
from langchain_core.messages import HumanMessage


class TestLLMClient:
    """Test LLM client functionality"""
    
    @pytest.fixture
    def openai_settings(self):
        """Settings for OpenAI provider"""
        return Settings(
            llm_provider="openai",
            openai_api_key="test-openai-key",
            html_optimization_model="gpt-4o-mini",
            action_generation_model="gpt-4o"
        )
    
    @pytest.fixture
    def anthropic_settings(self):
        """Settings for Anthropic provider"""
        return Settings(
            llm_provider="anthropic",
            anthropic_api_key="test-anthropic-key",
            html_optimization_model="claude-3-sonnet-20240229",
            action_generation_model="claude-3-opus-20240229"
        )
    
    @pytest.fixture
    def google_settings(self):
        """Settings for Google provider"""
        return Settings(
            llm_provider="google",
            google_api_key="test-google-key",
            html_optimization_model="gemini-pro",
            action_generation_model="gemini-pro"
        )
    
    @patch('src.llm_client.ChatOpenAI')
    def test_create_openai_llm(self, mock_chat_openai, openai_settings):
        """Test OpenAI LLM creation"""
        mock_llm = MagicMock()
        mock_chat_openai.return_value = mock_llm
        
        client = LLMClient(openai_settings)
        
        assert mock_chat_openai.called
        call_kwargs = mock_chat_openai.call_args[1]
        assert call_kwargs["model"] == openai_settings.html_optimization_model
        assert call_kwargs["openai_api_key"] == "test-openai-key"
    
    @patch('src.llm_client.ChatAnthropic')
    def test_create_anthropic_llm(self, mock_chat_anthropic, anthropic_settings):
        """Test Anthropic LLM creation"""
        mock_llm = MagicMock()
        mock_chat_anthropic.return_value = mock_llm
        
        client = LLMClient(anthropic_settings)
        
        assert mock_chat_anthropic.called
        call_kwargs = mock_chat_anthropic.call_args[1]
        assert call_kwargs["model"] == anthropic_settings.html_optimization_model
        assert call_kwargs["anthropic_api_key"] == "test-anthropic-key"
    
    @patch('src.llm_client.ChatGoogleGenerativeAI')
    def test_create_google_llm(self, mock_chat_google, google_settings):
        """Test Google LLM creation"""
        mock_llm = MagicMock()
        mock_chat_google.return_value = mock_llm
        
        client = LLMClient(google_settings)
        
        assert mock_chat_google.called
        call_kwargs = mock_chat_google.call_args[1]
        assert call_kwargs["model"] == google_settings.html_optimization_model
        assert call_kwargs["google_api_key"] == "test-google-key"
    
    def test_missing_api_key_raises_error(self):
        """Test that missing API key raises error"""
        settings = Settings(
            llm_provider="openai",
            openai_api_key=None
        )
        
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            LLMClient(settings)
    
    def test_unsupported_provider_raises_error(self):
        """Test that unsupported provider raises error"""
        settings = Settings(
            llm_provider="unsupported",
            openai_api_key="test-key"
        )
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            LLMClient(settings)
    
    @pytest.mark.asyncio
    async def test_generate_uses_html_optimization_llm(self, openai_settings):
        """Test that generate uses HTML optimization LLM when flag is set"""
        with patch('src.llm_client.ChatOpenAI') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="optimized html"))
            mock_chat.return_value = mock_llm
            
            client = LLMClient(openai_settings)
            
            result = await client.generate(
                prompt="Optimize this HTML",
                model="gpt-4o-mini",
                use_html_optimization_llm=True
            )
            
            assert result == "optimized html"
            assert mock_llm.ainvoke.called
            # Verify HumanMessage was used
            call_args = mock_llm.ainvoke.call_args[0][0]
            assert isinstance(call_args[0], HumanMessage)
            assert call_args[0].content == "Optimize this HTML"
    
    @pytest.mark.asyncio
    async def test_generate_uses_action_generation_llm(self, openai_settings):
        """Test that generate uses action generation LLM by default"""
        with patch('src.llm_client.ChatOpenAI') as mock_chat:
            mock_llm = MagicMock()
            mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="click #button"))
            mock_chat.return_value = mock_llm
            
            client = LLMClient(openai_settings)
            
            result = await client.generate(
                prompt="Generate action",
                model="gpt-4o",
                use_html_optimization_llm=False
            )
            
            assert result == "click #button"
            assert mock_llm.ainvoke.called

