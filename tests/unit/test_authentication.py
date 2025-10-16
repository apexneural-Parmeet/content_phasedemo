"""
Unit tests for Telegram bot authentication system
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.telegram_auth import TelegramAuth, require_login


class TestTelegramAuth:
    """Test the TelegramAuth class"""
    
    def test_init_default_credentials(self):
        """Test initialization with default credentials"""
        auth = TelegramAuth()
        assert auth.login_id is not None
        assert auth.login_password is not None
        assert isinstance(auth.logged_in_users, set)
    
    def test_verify_login_success(self):
        """Test successful login verification"""
        auth = TelegramAuth()
        user_id = 12345
        
        # Set test credentials
        auth.login_id = "testuser"
        auth.login_password = "testpass"
        
        result = auth.verify_login(user_id, "testuser", "testpass")
        assert result is True
        assert user_id in auth.logged_in_users
    
    def test_verify_login_wrong_id(self):
        """Test login with wrong ID"""
        auth = TelegramAuth()
        user_id = 12345
        
        auth.login_id = "testuser"
        auth.login_password = "testpass"
        
        result = auth.verify_login(user_id, "wronguser", "testpass")
        assert result is False
        assert user_id not in auth.logged_in_users
    
    def test_verify_login_wrong_password(self):
        """Test login with wrong password"""
        auth = TelegramAuth()
        user_id = 12345
        
        auth.login_id = "testuser"
        auth.login_password = "testpass"
        
        result = auth.verify_login(user_id, "testuser", "wrongpass")
        assert result is False
        assert user_id not in auth.logged_in_users
    
    def test_is_logged_in(self):
        """Test checking if user is logged in"""
        auth = TelegramAuth()
        user_id = 12345
        
        # Initially not logged in
        assert auth.is_logged_in(user_id) is False
        
        # After login
        auth.logged_in_users.add(user_id)
        assert auth.is_logged_in(user_id) is True
    
    def test_logout_user(self):
        """Test user logout"""
        auth = TelegramAuth()
        user_id = 12345
        
        # Login first
        auth.logged_in_users.add(user_id)
        assert auth.is_logged_in(user_id) is True
        
        # Logout
        auth.logout_user(user_id)
        assert auth.is_logged_in(user_id) is False
    
    def test_logout_not_logged_in_user(self):
        """Test logout for user who isn't logged in"""
        auth = TelegramAuth()
        user_id = 12345
        
        # Should not raise error
        auth.logout_user(user_id)
        assert auth.is_logged_in(user_id) is False


class TestAuthDecorators:
    """Test authentication decorators"""
    
    @pytest.mark.asyncio
    async def test_require_login_decorator_not_logged_in(self, mock_update, mock_context):
        """Test require_login decorator when user is not logged in"""
        
        @require_login
        async def protected_handler(self, update, context):
            return "success"
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = False
            
            result = await protected_handler(None, mock_update, mock_context)
            
            # Should have sent "please login" message
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args
            assert "Please Login First" in call_args[0][0] or "login" in call_args[0][0].lower()
    
    @pytest.mark.asyncio
    async def test_require_login_decorator_logged_in(self, mock_update, mock_context):
        """Test require_login decorator when user is logged in"""
        
        @require_login
        async def protected_handler(self, update, context):
            return "success"
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = True
            
            result = await protected_handler(None, mock_update, mock_context)
            
            # Should have executed the handler
            assert result == "success"


@pytest.mark.asyncio
class TestLoginHandlers:
    """Test login-related handlers"""
    
    async def test_login_command_not_logged_in(self, mock_update, mock_context):
        """Test /login command when user is not logged in"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = False
            
            result = await bot.login_command(mock_update, mock_context)
            
            # Should ask for login ID
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "Login ID" in call_args or "login" in call_args.lower()
    
    async def test_login_command_already_logged_in(self, mock_update, mock_context):
        """Test /login command when user is already logged in"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        
        with patch('app.services.telegram_auth.telegram_auth') as mock_auth:
            mock_auth.is_logged_in.return_value = True
            
            result = await bot.login_command(mock_update, mock_context)
            
            # Should say already logged in
            mock_update.message.reply_text.assert_called_once()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "Already Logged In" in call_args or "already" in call_args.lower()
    
    async def test_login_id_handler(self, mock_update, mock_context):
        """Test login ID input handler"""
        from app.services.telegram_bot_service import TelegramBotService
        
        bot = TelegramBotService()
        mock_update.message.text = "testuser"
        
        result = await bot.login_id_handler(mock_update, mock_context)
        
        # Should save ID and ask for password
        assert mock_context.user_data['login_id'] == "testuser"
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "password" in call_args.lower()

