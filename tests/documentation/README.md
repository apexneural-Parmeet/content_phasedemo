# Telegram Bot Test Suite Documentation

## Overview

This test suite provides comprehensive testing for the Social Hub Telegram Bot, covering authentication, AI content generation, manual post creation, scheduling, and platform integrations.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures and configuration
├── pytest.ini                  # Pytest configuration
├── requirements-test.txt       # Testing dependencies
├── unit/                       # Unit tests
│   ├── test_authentication.py
│   ├── test_ai_generation.py
│   └── test_telegram_handlers.py
├── integration/                # Integration tests
│   └── test_complete_flows.py
└── documentation/              # Test documentation
    ├── README.md              # This file
    ├── TEST_COVERAGE.md       # Coverage report
    └── TESTING_GUIDE.md       # How to run tests
```

## Test Categories

### Unit Tests

**Purpose:** Test individual components in isolation

**Files:**
- `test_authentication.py` - Login, logout, auth decorators
- `test_ai_generation.py` - Content generation, image generation, all tones/styles
- `test_telegram_handlers.py` - Individual bot handlers

**Example:**
```python
def test_verify_login_success():
    auth = TelegramAuth()
    result = auth.verify_login(12345, "testuser", "testpass")
    assert result is True
```

### Integration Tests

**Purpose:** Test complete workflows end-to-end

**Files:**
- `test_complete_flows.py` - Full generation flow, manual post flow, scheduling flow

**Example:**
```python
async def test_full_generation_to_post():
    # Test from topic entry to final post
    bot = TelegramBotService()
    # ... complete workflow ...
```

## Key Features Tested

### ✅ Authentication System
- [x] Login with correct credentials
- [x] Login with wrong credentials
- [x] Already logged in check
- [x] Logout functionality
- [x] Auth decorator protection
- [x] Session persistence

### ✅ AI Content Generation
- [x] DALL-E image generation
- [x] Nano Banana image generation
- [x] All 8 tones (casual, professional, corporate, etc.)
- [x] All 8 image styles (realistic, minimal, anime, etc.)
- [x] Content for all 4 platforms
- [x] Image regeneration
- [x] Content regeneration
- [x] Prompt enhancement

### ✅ Manual Post Creation
- [x] Image upload
- [x] Caption input
- [x] Platform selection
- [x] Immediate posting
- [x] Scheduled posting

### ✅ Scheduling
- [x] Quick schedule options (1 hour, 3 hours, etc.)
- [x] Custom time input
- [x] Past date rejection
- [x] Invalid format handling
- [x] Schedule storage
- [x] View scheduled posts

### ✅ Platform Integration
- [x] Facebook posting
- [x] Instagram posting
- [x] Twitter posting
- [x] Reddit posting
- [x] Platform status check
- [x] Credential validation

### ✅ Error Handling
- [x] Network timeouts
- [x] Invalid API keys
- [x] Corrupted data files
- [x] Rate limits
- [x] Special characters
- [x] Large file uploads

## Test Fixtures

### Mock Objects

**`mock_update`** - Simulates Telegram Update
```python
update.effective_user.id = 12345
update.message.text = "test message"
```

**`mock_context`** - Simulates bot context
```python
context.user_data = {}
context.bot_data = {}
```

**`mock_callback_query`** - Simulates button clicks
```python
query.data = "button_data"
query.answer = AsyncMock()
```

### Test Data

**`test_credentials`** - Mock social media credentials
**`test_auth_data`** - Mock authentication data
**`sample_image_path`** - Temporary test image file

### API Mocks

**`mock_openai_response`** - Mock GPT-4 response
**`mock_dalle_response`** - Mock DALL-E image generation
**`mock_fal_response`** - Mock Fal.ai Nano Banana response

## Running Tests

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed instructions.

### Quick Start

```bash
# Install test dependencies
pip install -r tests/requirements-test.txt

# Run all tests
pytest tests/

# Run specific category
pytest tests/unit/
pytest tests/integration/

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_authentication.py

# Run specific test
pytest tests/unit/test_authentication.py::TestTelegramAuth::test_verify_login_success
```

## Markers

Tests are organized using pytest markers:

```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test
@pytest.mark.asyncio       # Async test
@pytest.mark.slow          # Slow test (>1s)
@pytest.mark.requires_api  # Requires real API keys
```

Run specific markers:
```bash
pytest -m unit             # Only unit tests
pytest -m "not slow"       # Skip slow tests
pytest -m asyncio          # Only async tests
```

## Code Coverage

Current coverage targets:
- **Overall:** 85%+
- **Critical paths:** 95%+ (auth, posting)
- **Handlers:** 80%+
- **Utilities:** 90%+

View coverage report:
```bash
pytest --cov=app --cov-report=html tests/
open htmlcov/index.html
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -r tests/requirements-test.txt
    pytest tests/ --cov=app --cov-report=xml
```

## Mocking Strategy

### External APIs
All external API calls are mocked to:
- ✅ Prevent API quota usage
- ✅ Ensure consistent test results
- ✅ Enable offline testing
- ✅ Speed up test execution

### Database/File Operations
File operations use `tmp_path` fixture for:
- ✅ Isolated test environments
- ✅ Automatic cleanup
- ✅ No side effects

## Best Practices

1. **Isolation:** Each test is independent
2. **Mocking:** Mock external dependencies
3. **Async:** Proper async/await handling
4. **Cleanup:** Automatic cleanup with fixtures
5. **Assertions:** Clear, specific assertions
6. **Documentation:** Docstrings for all tests

## Common Issues

### Issue: "Event loop is closed"
**Solution:** Use `@pytest.mark.asyncio` decorator

### Issue: "Mock not being called"
**Solution:** Ensure correct patch path (where imported, not where defined)

### Issue: "Fixture not found"
**Solution:** Check `conftest.py` and import statements

## Contributing

When adding new features:

1. ✅ Write tests first (TDD)
2. ✅ Aim for 80%+ coverage
3. ✅ Include docstrings
4. ✅ Use appropriate markers
5. ✅ Update documentation

## Test Metrics

Last test run:
- **Total Tests:** ~50+
- **Passed:** To be determined
- **Failed:** To be determined
- **Coverage:** To be determined
- **Duration:** To be determined

Run `pytest --collect-only` to see all available tests.

## Support

For issues or questions:
1. Check [TESTING_GUIDE.md](./TESTING_GUIDE.md)
2. Review test examples in `tests/unit/`
3. Check pytest documentation
4. Review mock/fixture usage in `conftest.py`

---

**Last Updated:** October 15, 2025  
**Version:** 1.0  
**Status:** ✅ Ready for Testing

