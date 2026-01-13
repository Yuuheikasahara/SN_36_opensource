from typing import Optional
from src.config import Settings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class LLMClient:
    """Unified LLM client using LangChain supporting multiple providers"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.html_optimization_llm = self._create_llm(
            model=settings.html_optimization_model,
            temperature=settings.html_optimization_temperature,
            max_tokens=settings.html_optimization_max_tokens
        )
        self.action_generation_llm = self._create_llm(
            model=settings.action_generation_model,
            temperature=settings.action_generation_temperature,
            max_tokens=settings.action_generation_max_tokens
        )
    
    def _create_llm(self, model: str, temperature: float, max_tokens: int):
        """Create LangChain LLM instance based on provider"""
        if self.settings.llm_provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError("OpenAI API key is required when using OpenAI provider")
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=self.settings.openai_api_key
            )
        
        elif self.settings.llm_provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError("Anthropic API key is required when using Anthropic provider")
            return ChatAnthropic(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                anthropic_api_key=self.settings.anthropic_api_key
            )
        
        elif self.settings.llm_provider == "google":
            if not self.settings.google_api_key:
                raise ValueError("Google API key is required when using Google provider")
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=temperature,
                max_output_tokens=max_tokens,
                google_api_key=self.settings.google_api_key
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.settings.llm_provider}")
    
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.3,
        max_tokens: int = 1000,
        use_html_optimization_llm: bool = False
    ) -> str:
        """
        Generate text using LangChain LLM.
        
        Args:
            prompt: Input prompt
            model: Model name (for compatibility, but uses pre-configured LLM)
            temperature: Sampling temperature (for compatibility)
            max_tokens: Maximum tokens (for compatibility)
            use_html_optimization_llm: If True, use HTML optimization LLM, else use action generation LLM
            
        Returns:
            Generated text
        """
        llm = self.html_optimization_llm if use_html_optimization_llm else self.action_generation_llm
        
        # Use LangChain's async invoke
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        
        return response.content
