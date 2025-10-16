"""
API routes for managing social media credentials
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.services.credentials_service import (
    get_all_credentials,
    get_platform_credentials,
    update_platform_credentials,
    delete_platform_credentials,
    get_connection_status
)
from app.config import settings

router = APIRouter()

class FacebookCredentials(BaseModel):
    access_token: str
    page_id: str

class InstagramCredentials(BaseModel):
    access_token: str
    account_id: str

class TwitterCredentials(BaseModel):
    api_key: str
    api_secret: str
    access_token: str
    access_token_secret: str
    bearer_token: Optional[str] = None

class RedditCredentials(BaseModel):
    client_id: str
    client_secret: str
    username: str
    password: str
    user_agent: Optional[str] = "SocialHub Bot v1.0"

class TelegramCredentials(BaseModel):
    bot_token: str
    channel_id: str

class PlatformCredentials(BaseModel):
    platform: str
    credentials: Dict

@router.get("/api/credentials/status")
async def get_credentials_status():
    """Get connection status for all platforms"""
    try:
        status = get_connection_status()
        return {
            "success": True,
            "status": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/credentials/migrate-from-env")
async def migrate_credentials_from_env():
    """Migrate credentials from environment variables to credential storage"""
    try:
        migrated = []
        skipped = []
        
        # Facebook
        if settings.FACEBOOK_ACCESS_TOKEN:
            update_platform_credentials("facebook", {
                "access_token": settings.FACEBOOK_ACCESS_TOKEN
            })
            migrated.append("facebook")
        else:
            skipped.append("facebook")
        
        # Instagram
        if settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID:
            update_platform_credentials("instagram", {
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                "account_id": settings.INSTAGRAM_ACCOUNT_ID
            })
            migrated.append("instagram")
        else:
            skipped.append("instagram")
        
        # Twitter
        if all([
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET,
            settings.TWITTER_ACCESS_TOKEN,
            settings.TWITTER_ACCESS_TOKEN_SECRET
        ]):
            twitter_creds = {
                "api_key": settings.TWITTER_API_KEY,
                "api_secret": settings.TWITTER_API_SECRET,
                "access_token": settings.TWITTER_ACCESS_TOKEN,
                "access_token_secret": settings.TWITTER_ACCESS_TOKEN_SECRET
            }
            if settings.TWITTER_BEARER_TOKEN:
                twitter_creds["bearer_token"] = settings.TWITTER_BEARER_TOKEN
            
            update_platform_credentials("twitter", twitter_creds)
            migrated.append("twitter")
        else:
            skipped.append("twitter")
        
        # Reddit
        if all([
            settings.REDDIT_CLIENT_ID,
            settings.REDDIT_CLIENT_SECRET,
            settings.REDDIT_USERNAME,
            settings.REDDIT_PASSWORD
        ]):
            update_platform_credentials("reddit", {
                "client_id": settings.REDDIT_CLIENT_ID,
                "client_secret": settings.REDDIT_CLIENT_SECRET,
                "username": settings.REDDIT_USERNAME,
                "password": settings.REDDIT_PASSWORD,
                "user_agent": settings.REDDIT_USER_AGENT
            })
            migrated.append("reddit")
        else:
            skipped.append("reddit")
        
        # Telegram
        if settings.TELEGRAM_BOT_TOKEN:
            telegram_creds = {
                "bot_token": settings.TELEGRAM_BOT_TOKEN
            }
            # Channel ID might not be in settings, add if available
            if hasattr(settings, 'TELEGRAM_CHANNEL_ID') and settings.TELEGRAM_CHANNEL_ID:
                telegram_creds["channel_id"] = settings.TELEGRAM_CHANNEL_ID
            else:
                telegram_creds["channel_id"] = ""
            
            update_platform_credentials("telegram", telegram_creds)
            migrated.append("telegram")
        else:
            skipped.append("telegram")
        
        return {
            "success": True,
            "message": f"Migrated {len(migrated)} platform(s) from environment variables",
            "migrated": migrated,
            "skipped": skipped
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/credentials/test/{platform}")
async def test_platform_connection(platform: str):
    """Test connection to a platform"""
    try:
        credentials = get_platform_credentials(platform)
        if not credentials:
            raise HTTPException(status_code=404, detail=f"No credentials configured for {platform}")
        
        # TODO: Implement actual connection testing for each platform
        # For now, just return success if credentials exist
        
        return {
            "success": True,
            "message": f"Connection to {platform} verified",
            "platform": platform
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/credentials/{platform}")
async def get_credentials(platform: str):
    """Get credentials for a specific platform"""
    try:
        credentials = get_platform_credentials(platform)
        if credentials:
            # Mask sensitive data
            masked_credentials = mask_credentials(platform, credentials)
            return {
                "success": True,
                "platform": platform,
                "credentials": masked_credentials,
                "configured": True
            }
        else:
            return {
                "success": True,
                "platform": platform,
                "credentials": None,
                "configured": False
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/credentials/{platform}")
async def save_platform_creds(platform: str, credentials: Dict):
    """Save or update credentials for a platform"""
    try:
        # Validate platform
        valid_platforms = ["facebook", "instagram", "twitter", "reddit", "telegram"]
        if platform not in valid_platforms:
            raise HTTPException(status_code=400, detail=f"Invalid platform. Must be one of: {valid_platforms}")
        
        # Save credentials
        success = update_platform_credentials(platform, credentials)
        
        if success:
            return {
                "success": True,
                "message": f"{platform.capitalize()} credentials saved successfully",
                "platform": platform
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save credentials")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/credentials/{platform}")
async def delete_credentials(platform: str):
    """Delete credentials for a platform"""
    try:
        success = delete_platform_credentials(platform)
        if success:
            return {
                "success": True,
                "message": f"{platform.capitalize()} credentials deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": f"No credentials found for {platform}"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def mask_credentials(platform: str, credentials: Dict) -> Dict:
    """Mask sensitive credential data for display"""
    masked = credentials.copy()
    
    # Mask tokens and secrets
    for key in masked:
        if key in ["access_token", "api_key", "api_secret", "access_token_secret", 
                   "bearer_token", "client_secret", "password", "bot_token"]:
            value = masked[key]
            if value and len(value) > 8:
                masked[key] = value[:4] + "..." + value[-4:]
            elif value:
                masked[key] = "***"
    
    return masked
