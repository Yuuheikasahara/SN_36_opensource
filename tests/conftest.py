import pytest
from unittest.mock import AsyncMock, MagicMock
from src.config import Settings
from src.llm_client import LLMClient


@pytest.fixture
def mock_settings():
    """Create mock settings for testing"""
    return Settings(
        llm_provider="openai",
        openai_api_key="test-key",
        html_optimization_model="gpt-4o-mini",
        action_generation_model="gpt-4o",
        html_optimization_temperature=0.1,
        action_generation_temperature=0.3,
        html_optimization_max_tokens=4000,
        action_generation_max_tokens=500
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response"""
    mock_response = MagicMock()
    mock_response.content = "mock response"
    return mock_response


@pytest.fixture
def mock_llm_client(mock_settings, mock_llm_response):
    """Create a mock LLM client"""
    mock_client = MagicMock(spec=LLMClient)
    mock_client.html_optimization_llm = AsyncMock()
    mock_client.html_optimization_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
    mock_client.action_generation_llm = AsyncMock()
    mock_client.action_generation_llm.ainvoke = AsyncMock(return_value=mock_llm_response)
    mock_client.generate = AsyncMock(return_value="mock response")
    return mock_client


@pytest.fixture
def sample_html():
    """Sample HTML for testing"""
    return """
    <html>
        <head>
            <title>Test Page</title>
            <script>console.log('test');</script>
            <style>body { color: red; }</style>
        </head>
        <body>
            <div id="main">
                <button id="login-btn" class="btn-primary">Login</button>
                <input type="text" id="username" placeholder="Username">
                <a href="/about">About</a>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_optimized_html():
    """Sample optimized HTML"""
    return """
    <html>
        <body>
            <div id="main">
                <button id="login-btn" class="btn-primary">Login</button>
                <input type="text" id="username" placeholder="Username">
                <a href="/about">About</a>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_task_data():
    """Sample task data as IWA would send"""
    return {
        "task_id": "task_123",
        "prompt": "Click on the login button",
        "start_url": "https://example.com",
        "snapshot_html": "<html><body><button id='login-btn'>Login</button></body></html>",
        "step_index": 0,
        "web_project_id": "project_1",
        "history": []
    }


@pytest.fixture
def sample_history():
    """Sample action history"""
    return [
        {"action": "navigate https://example.com", "result": "Page loaded"},
        {"action": "click #login-btn", "result": "Login form opened"}
    ]

