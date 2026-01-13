from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # LLM API Configuration
    llm_provider: str = "openai"  # Options: "openai", "anthropic", "google"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    
    # Model Configuration
    html_optimization_model: str = "gpt-4o-mini"
    action_generation_model: str = "gpt-4o"
    
    # Temperature settings
    html_optimization_temperature: float = 0.1
    action_generation_temperature: float = 0.3
    
    # Max tokens
    html_optimization_max_tokens: int = 4000
    action_generation_max_tokens: int = 500
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

