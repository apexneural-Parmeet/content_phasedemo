"""
Service for managing social media platform credentials
"""
import json
import os
from typing import Dict, Optional
from pathlib import Path

# Storage file path
CREDENTIALS_FILE = "data/credentials/user_credentials.json"

def get_credentials_file_path() -> str:
    """Get the full path to credentials file"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), CREDENTIALS_FILE)

def load_credentials() -> Dict:
    """Load all credentials from file"""
    file_path = get_credentials_file_path()
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading credentials: {e}")
            return {}
    return {}

def save_credentials(credentials: Dict) -> bool:
    """Save credentials to file"""
    file_path = get_credentials_file_path()
    try:
        with open(file_path, 'w') as f:
            json.dump(credentials, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False

def get_platform_credentials(platform: str) -> Optional[Dict]:
    """Get credentials for a specific platform"""
    credentials = load_credentials()
    return credentials.get(platform)

def update_platform_credentials(platform: str, platform_credentials: Dict) -> bool:
    """Update credentials for a specific platform"""
    credentials = load_credentials()
    credentials[platform] = platform_credentials
    return save_credentials(credentials)

def delete_platform_credentials(platform: str) -> bool:
    """Delete credentials for a specific platform"""
    credentials = load_credentials()
    if platform in credentials:
        del credentials[platform]
        return save_credentials(credentials)
    return False

def get_all_credentials() -> Dict:
    """Get all stored credentials"""
    return load_credentials()

def get_connection_status() -> Dict:
    """Get connection status for all platforms"""
    credentials = load_credentials()
    status = {}
    
    platforms = ["facebook", "instagram", "twitter", "reddit", "telegram"]
    
    for platform in platforms:
        if platform in credentials:
            creds = credentials[platform]
            # Check if credentials have required fields (basic validation)
            is_configured = False
            
            if platform == "facebook":
                is_configured = bool(creds.get("access_token"))
            elif platform == "instagram":
                is_configured = bool(creds.get("access_token") and creds.get("account_id"))
            elif platform == "twitter":
                is_configured = bool(
                    creds.get("api_key") and 
                    creds.get("api_secret") and 
                    creds.get("access_token") and 
                    creds.get("access_token_secret")
                )
            elif platform == "reddit":
                is_configured = bool(
                    creds.get("client_id") and 
                    creds.get("client_secret") and 
                    creds.get("username") and 
                    creds.get("password")
                )
            elif platform == "telegram":
                is_configured = bool(creds.get("bot_token") and creds.get("channel_id"))
            
            status[platform] = {
                "connected": is_configured,
                "configured": True
            }
        else:
            status[platform] = {
                "connected": False,
                "configured": False
            }
    
    return status

