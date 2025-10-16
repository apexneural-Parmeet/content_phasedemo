"""
Centralized session management for Telegram bot
Provides type-safe access to user session data
"""
from typing import Dict, Any, Optional


class SessionManager:
    """Manages user sessions for the Telegram bot"""
    
    def __init__(self):
        self.sessions: Dict[int, Dict[str, Any]] = {}
    
    def get_session(self, user_id: int) -> Dict[str, Any]:
        """Get or create session for user"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {}
        return self.sessions[user_id]
    
    def set(self, user_id: int, key: str, value: Any) -> None:
        """Set a value in user session"""
        session = self.get_session(user_id)
        session[key] = value
    
    def get(self, user_id: int, key: str, default: Any = None) -> Any:
        """Get a value from user session"""
        session = self.get_session(user_id)
        return session.get(key, default)
    
    def delete(self, user_id: int, key: str) -> None:
        """Delete a key from user session"""
        session = self.get_session(user_id)
        if key in session:
            del session[key]
    
    def clear(self, user_id: int) -> None:
        """Clear entire session for user"""
        if user_id in self.sessions:
            self.sessions[user_id] = {}
    
    def has(self, user_id: int, key: str) -> bool:
        """Check if key exists in session"""
        session = self.get_session(user_id)
        return key in session
    
    def update(self, user_id: int, data: Dict[str, Any]) -> None:
        """Update session with multiple key-value pairs"""
        session = self.get_session(user_id)
        session.update(data)
    
    # Convenience methods for common session data
    def get_topic(self, user_id: int) -> Optional[str]:
        """Get the current topic for user"""
        return self.get(user_id, 'topic')
    
    def get_tone(self, user_id: int) -> Optional[str]:
        return self.get(user_id, 'tone')
    
    def get_image_provider(self, user_id: int) -> Optional[str]:
        return self.get(user_id, 'image_provider')
    
    def get_image_style(self, user_id: int) -> Optional[str]:
        return self.get(user_id, 'image_style')
    
    def get_approved_platforms(self, user_id: int) -> list:
        return self.get(user_id, 'approved_platforms', [])
    
    def get_generated_content(self, user_id: int) -> Optional[Dict]:
        return self.get(user_id, 'generated_content')


# Global session manager instance
session_manager = SessionManager()
