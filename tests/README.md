# Test Suite for WebAgent

This test suite simulates the IWA (Infinite WebArena) benchmark behavior to test the webagent.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and test configuration
├── test_act_endpoint.py     # Tests for FastAPI /act endpoint
├── test_html_optimizer.py   # Tests for HTML optimization
├── test_action_generator.py # Tests for action generation
├── test_llm_client.py       # Tests for LLM client
└── test_integration_iwa.py  # Integration tests simulating IWA scenarios
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_act_endpoint.py
```

### Run with verbose output:
```bash
pytest -v
```

### Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

### 1. Unit Tests
- **test_html_optimizer.py**: Tests HTML optimization logic
- **test_action_generator.py**: Tests action generation logic
- **test_llm_client.py**: Tests LLM client functionality

### 2. API Tests
- **test_act_endpoint.py**: Tests the FastAPI `/act` endpoint
  - Basic endpoint functionality
  - Request validation
  - Error handling
  - Multi-step task flows

### 3. Integration Tests
- **test_integration_iwa.py**: Full IWA benchmark simulation
  - Complete task flows (login, search, etc.)
  - Multiple web projects (autocinema, autobook, etc.)
  - Task completion detection
  - Error recovery

## IWA Simulation

The tests simulate how IWA benchmark sends tasks:

1. **Task Request**: IWA sends POST request to `/act` with:
   - `task_id`: Unique task identifier
   - `prompt`: Human-readable task description
   - `start_url`: Current URL
   - `snapshot_html`: Current page HTML
   - `step_index`: Current step number
   - `web_project_id`: Web project identifier (autocinema, autobook, etc.)
   - `history`: Previous actions and results

2. **Agent Response**: Agent returns:
   - `action`: Next action to execute
   - `task_id`: Echoed task ID
   - `step_index`: Echoed step index

3. **Task Flow**: The cycle repeats until:
   - Task is completed (agent returns "done")
   - Maximum steps reached
   - Error occurs

## Example Test Scenarios

### Autocinema Login Flow
Simulates a complete login task:
1. Navigate to login page
2. Enter username
3. Enter password
4. Submit form
5. Task complete

### Autobook Search Flow
Simulates a book search task:
1. Enter search query
2. Click search button
3. View book details

## Mocking

Tests use mocks for:
- LLM API calls (to avoid actual API usage)
- HTML optimization results
- Action generation results

This allows tests to run quickly without requiring API keys or making real API calls.

## Fixtures

Common fixtures in `conftest.py`:
- `mock_settings`: Mock configuration
- `mock_llm_client`: Mock LLM client
- `sample_html`: Sample HTML for testing
- `sample_task_data`: Sample IWA task data
- `sample_history`: Sample action history

## Notes

- All async tests use `pytest-asyncio`
- Tests use `TestClient` from FastAPI for API testing
- LLM responses are mocked to ensure deterministic tests
- Integration tests simulate realistic IWA benchmark scenarios

