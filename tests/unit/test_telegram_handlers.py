"""
Unit tests for Telegram bot handlers
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.telegram.states import MENU, GENERATE_TOPIC, LOGIN_ID, LOGIN_PASSWORD


class TestStartCommand:
    """Test /start command handler"""
    
    @pytest.mark.asyncio
    async def test_start_not_logged_in(self, mock_update, mock_context):
        """Test /start when user is not logged in"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = False
            
            result = await bot.start_command(mock_update, mock_context)
            
            # Should ask to login
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "login" in call_args.lower()
    
    @pytest.mark.asyncio
    async def test_start_logged_in(self, mock_update, mock_context):
        """Test /start when user is logged in"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = True
            
            result = await bot.start_command(mock_update, mock_context)
            
            # Should show main menu
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert result == MENU


class TestMenuHandlers:
    """Test menu navigation handlers"""
    
    @pytest.mark.asyncio
    async def test_menu_generate_selection(self, mock_callback_query, mock_context):
        """Test selecting 'Generate AI Content' from menu"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        mock_callback_query.data = "menu_generate"
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = True
            
            result = await bot.menu_handler(mock_update, mock_context)
            
            # Should ask for topic
            mock_callback_query.edit_message_text.assert_called_once()
            assert result == GENERATE_TOPIC
    
    @pytest.mark.asyncio
    async def test_menu_logout(self, mock_callback_query, mock_context):
        """Test logout from menu"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        mock_callback_query.data = "menu_logout"
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.logout_user = MagicMock()
            
            await bot.logout_handler(mock_update, mock_context)
            
            # Should call logout
            mock_auth.logout_user.assert_called_once()


class TestGenerationFlow:
    """Test AI content generation flow"""
    
    @pytest.mark.asyncio
    async def test_topic_handler(self, mock_update, mock_context):
        """Test topic input handler"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update.message.text = "coffee shop opening"
        mock_update.effective_user.id = 12345
        
        result = await bot.generate_topic_handler(mock_update, mock_context)
        
        # Should save topic and ask for tone
        mock_update.message.reply_text.assert_called_once()
        # Topic should be saved in session
        # State should transition to tone selection
    
    @pytest.mark.asyncio
    async def test_tone_selection(self, mock_callback_query, mock_context):
        """Test tone selection handler"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        mock_callback_query.data = "tone_casual"
        mock_callback_query.from_user.id = 12345
        
        # Set up session with topic
        from app.services.telegram_bot_service import user_sessions
        user_sessions[12345] = {"topic": "test topic"}
        
        result = await bot.generate_tone_handler(mock_update, mock_context)
        
        # Should save tone and ask for provider
        mock_callback_query.answer.assert_called_once()


class TestManualPostCreation:
    """Test manual post creation handlers"""
    
    @pytest.mark.asyncio
    async def test_image_upload(self, sample_image_path):
        """Test image upload for manual post"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update = MagicMock()
        mock_context = MagicMock()
        
        # Mock photo message
        mock_update.message.photo = [MagicMock()]
        mock_update.message.photo[-1].get_file = AsyncMock()
        mock_update.message.photo[-1].get_file.return_value.download_to_drive = AsyncMock()
        mock_update.effective_user.id = 12345
        mock_update.message.reply_text = AsyncMock()
        
        result = await bot.create_image_handler(mock_update, mock_context)
        
        # Should ask for caption
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_caption_input(self, mock_update, mock_context):
        """Test caption input for manual post"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update.message.text = "This is my manual post caption"
        mock_update.effective_user.id = 12345
        
        # Set up session with image path
        from app.services.telegram_bot_service import user_sessions
        user_sessions[12345] = {"manual_image_path": "/tmp/test.png"}
        
        result = await bot.create_caption_handler(mock_update, mock_context)
        
        # Should ask for platform selection
        mock_update.message.reply_text.assert_called_once()


class TestScheduling:
    """Test scheduling functionality"""
    
    @pytest.mark.asyncio
    async def test_quick_schedule_1hour(self, mock_callback_query, mock_context):
        """Test quick schedule option: In 1 Hour"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update = MagicMock()
        mock_update.callback_query = mock_callback_query
        mock_callback_query.data = "quick_1hour"
        mock_callback_query.from_user.id = 12345
        
        # Set up session with required data
        from app.services.telegram_bot_service import user_sessions
        user_sessions[12345] = {
            "image_path": "/tmp/test.png",
            "generated_content": {
                "facebook": "FB post",
                "instagram": "IG post",
                "twitter": "Tweet",
                "reddit": "Reddit post"
            },
            "approved_platforms": ["facebook", "instagram"]
        }
        
        with patch('app.services.telegram_bot_service import scheduler') as mock_scheduler:
            result = await bot.schedule_time_handler(mock_update, mock_context)
            
            # Should schedule the post
            mock_callback_query.edit_message_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_custom_time_valid(self, mock_update, mock_context):
        """Test custom schedule time with valid future date"""
        from app.services.telegram_bot_service import TelegramBotService
        from datetime import datetime, timedelta
        
        bot = TelegramBotService()
        
        # Future date
        future_date = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
        mock_update.message.text = future_date
        mock_update.effective_user.id = 12345
        
        # Set up session
        from app.services.telegram_bot_service import user_sessions
        user_sessions[12345] = {
            "image_path": "/tmp/test.png",
            "generated_content": {"facebook": "test"},
            "approved_platforms": ["facebook"]
        }
        
        with patch('app.services.telegram_bot_service.scheduler') as mock_scheduler:
            result = await bot.schedule_time_handler(mock_update, mock_context)
            
            # Should accept and schedule
            mock_update.message.reply_text.assert_called()
    
    @pytest.mark.asyncio
    async def test_custom_time_past_date(self, mock_update, mock_context):
        """Test custom schedule time with past date"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update.message.text = "2020-01-01 10:00"
        mock_update.effective_user.id = 12345
        
        result = await bot.schedule_time_handler(mock_update, mock_context)
        
        # Should reject with error
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "future" in call_args.lower() or "past" in call_args.lower()

