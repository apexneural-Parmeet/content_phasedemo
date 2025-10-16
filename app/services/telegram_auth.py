"""
Telegram Bot Authentication Service
Login system with ID and Password
"""
import json
import os
from pathlib import Path
from typing import Dict, Set
from telegram import Update
from telegram.ext import ContextTypes

# File to store login credentials
AUTH_FILE = "data/credentials/telegram_auth.json"

def get_auth_file_path() -> str:
    """Get the full path to auth file"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), AUTH_FILE)

class TelegramAuth:
    """Manages login authentication for the Telegram bot"""
    
    def __init__(self):
        self.login_id: str = ""
        self.login_password: str = ""
        self.logged_in_users: Set[int] = set()  # Telegram user IDs that are logged in
        self.load_credentials()
    
    def load_credentials(self):
        """Load login credentials from file"""
        file_path = get_auth_file_path()
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.login_id = data.get('login_id', '')
                    self.login_password = data.get('login_password', '')
                    self.logged_in_users = set(data.get('logged_in_users', []))
                    
                    if self.login_id and self.login_password:
                        print(f"✅ Login credentials loaded")
                        print(f"✅ Currently logged in users: {len(self.logged_in_users)}")
                    else:
                        print("⚠️  No credentials set. Please configure LOGIN_ID and LOGIN_PASSWORD in .env")
            except Exception as e:
                print(f"Error loading auth file: {e}")
        else:
            print("ℹ️  Creating new auth file...")
            # Try to load from environment variables
            from app.config import settings
            self.login_id = os.getenv('TELEGRAM_LOGIN_ID', 'admin')
            self.login_password = os.getenv('TELEGRAM_LOGIN_PASSWORD', 'admin123')
            self.save_credentials()
            print(f"✅ Default credentials created: ID={self.login_id}")
    
    def save_credentials(self):
        """Save credentials to file"""
        file_path = get_auth_file_path()
        
        try:
            data = {
                'login_id': self.login_id,
                'login_password': self.login_password,
                'logged_in_users': list(self.logged_in_users)
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving auth file: {e}")
    
    def verify_login(self, user_id: int, login_id: str, password: str) -> bool:
        """Verify login credentials"""
        if login_id == self.login_id and password == self.login_password:
            self.logged_in_users.add(user_id)
            self.save_credentials()
            return True
        return False
    
    def is_logged_in(self, user_id: int) -> bool:
        """Check if a user is logged in"""
        return user_id in self.logged_in_users
    
    def logout_user(self, user_id: int):
        """Logout a user"""
        if user_id in self.logged_in_users:
            self.logged_in_users.remove(user_id)
            self.save_credentials()
    
    def get_logged_in_count(self) -> int:
        """Get count of logged in users"""
        return len(self.logged_in_users)


# Global instance
telegram_auth = TelegramAuth()


# Decorator for protected commands
def require_login(func):
    """Decorator to require login for a handler"""
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not telegram_auth.is_logged_in(user.id):
            # Send login prompt
            await update.message.reply_text(
                "🔒 *Please Login First*\n\n"
                "You need to login to use this bot.\n\n"
                "Use /login to authenticate.",
                parse_mode='Markdown'
            )
            return
        
        # User is logged in, proceed with the handler
        return await func(self, update, context)
    
    return wrapper


def require_login_callback(func):
    """Decorator to require login for callback handlers"""
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not telegram_auth.is_logged_in(user.id):
            query = update.callback_query
            await query.answer("❌ Please login first", show_alert=True)
            await query.message.reply_text(
                "🔒 *Please Login First*\n\n"
                "Use /login to authenticate.",
                parse_mode='Markdown'
            )
            return
        
        # User is logged in, proceed with the handler
        return await func(self, update, context)
    
    return wrapper

