"""
Pytest configuration and fixtures for Telegram bot tests
"""
import pytest
import asyncio
import os
import json
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_CREDENTIALS_FILE = TEST_DATA_DIR / "test_credentials.json"
TEST_AUTH_FILE = TEST_DATA_DIR / "test_auth.json"
TEST_SCHEDULED_FILE = TEST_DATA_DIR / "test_scheduled.json"


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object"""
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_user.first_name = "TestUser"
    update.message.text = "test message"
    update.message.reply_text = AsyncMock()
    update.message.delete = AsyncMock()
    update.callback_query = None
    return update


@pytest.fixture
def mock_context():
    """Create a mock Context object"""
    context = MagicMock()
    context.user_data = {}
    context.bot_data = {}
    return context


@pytest.fixture
def mock_callback_query():
    """Create a mock callback query for button clicks"""
    query = MagicMock()
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    query.message.reply_text = AsyncMock()
    query.from_user.id = 12345
    return query


@pytest.fixture
def test_credentials():
    """Provide test credentials"""
    return {
        "facebook": {"access_token": "test_fb_token"},
        "instagram": {"access_token": "test_ig_token", "account_id": "12345"},
        "twitter": {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "access_token": "test_token",
            "access_token_secret": "test_token_secret"
        },
        "reddit": {
            "client_id": "test_id",
            "client_secret": "test_secret",
            "username": "test_user",
            "password": "test_pass",
            "user_agent": "test_agent"
        }
    }


@pytest.fixture
def test_auth_data():
    """Provide test auth data"""
    return {
        "login_id": "testuser",
        "login_password": "testpass",
        "logged_in_users": []
    }


@pytest.fixture
def test_scheduled_posts():
    """Provide test scheduled posts"""
    return []


@pytest.fixture(autouse=True)
def setup_test_files(tmp_path, test_credentials, test_auth_data, test_scheduled_posts):
    """Setup test data files before each test"""
    # Create test data directory
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Write test files
    cred_file = test_data_dir / "test_credentials.json"
    auth_file = test_data_dir / "test_auth.json"
    sched_file = test_data_dir / "test_scheduled.json"
    
    cred_file.write_text(json.dumps(test_credentials))
    auth_file.write_text(json.dumps(test_auth_data))
    sched_file.write_text(json.dumps(test_scheduled_posts))
    
    yield {
        "credentials": cred_file,
        "auth": auth_file,
        "scheduled": sched_file
    }
    
    # Cleanup after test
    # Files will be automatically cleaned up since using tmp_path


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "facebook": "Test Facebook post content",
                    "instagram": "Test Instagram caption",
                    "twitter": "Test tweet",
                    "reddit": "Test Reddit post"
                })
            }
        }]
    }


@pytest.fixture
def mock_dalle_response():
    """Mock DALL-E image generation response"""
    mock_response = MagicMock()
    mock_response.data = [MagicMock(url="https://example.com/test_image.png")]
    return mock_response


@pytest.fixture
def mock_fal_response():
    """Mock Fal.ai Nano Banana response"""
    return {
        "images": [{"url": "https://example.com/test_nano_image.png"}]
    }


@pytest.fixture
def sample_image_path(tmp_path):
    """Create a sample test image"""
    image_path = tmp_path / "test_image.png"
    # Create a minimal 1x1 pixel PNG
    image_path.write_bytes(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        b'\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00'
        b'\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
        b'\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return str(image_path)

