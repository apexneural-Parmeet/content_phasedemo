"""
Health check and token verification endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
from app.config import settings
from app.clients.twitter import get_twitter_v1_client
from app.clients.reddit import get_reddit_client
from app.services.instagram_service import get_instagram_account_info

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "ok", "message": "Server is running"}


@router.get("/verify-token")
async def verify_token():
    """
    Verify all platform token status
    """
    facebook_status = {"valid": False, "pageInfo": None}
    instagram_status = {"valid": False, "pageInfo": None}
    twitter_status = {"valid": False, "pageInfo": None}
    reddit_status = {"valid": False, "pageInfo": None}
    
    async with httpx.AsyncClient() as client:
        # Verify Facebook token
        try:
            fb_response = await client.get(
                f"{settings.FACEBOOK_GRAPH_URL}/me",
                params={"access_token": settings.FACEBOOK_ACCESS_TOKEN}
            )
            fb_response.raise_for_status()
            fb_data = fb_response.json()
            facebook_status = {
                "valid": True,
                "pageInfo": fb_data
            }
        except httpx.HTTPError as e:
            print(f"Facebook token error: {e}")
            facebook_status = {
                "valid": False,
                "error": str(e)
            }
        
        # Verify Instagram configuration
        try:
            ig_account_id, username = await get_instagram_account_info()
            instagram_status = {
                "valid": True,
                "pageInfo": {
                    "id": ig_account_id,
                    "username": username
                }
            }
        except Exception as e:
            print(f"Instagram configuration error: {e}")
            instagram_status = {
                "valid": False,
                "error": str(e)
            }
    
    # Verify Twitter configuration
    try:
        twitter_client = get_twitter_v1_client()
        if twitter_client:
            user = twitter_client.verify_credentials()
            twitter_status = {
                "valid": True,
                "pageInfo": {
                    "id": user.id,
                    "username": user.screen_name
                }
            }
        else:
            twitter_status = {"valid": False, "error": "Credentials not configured"}
    except Exception as e:
        print(f"Twitter configuration error: {e}")
        twitter_status = {
            "valid": False,
            "error": str(e)
        }
    
    # Verify Reddit configuration
    try:
        reddit_client = get_reddit_client()
        if reddit_client:
            user = reddit_client.user.me()
            reddit_status = {
                "valid": True,
                "pageInfo": {
                    "name": user.name,
                    "id": user.id
                }
            }
        else:
            reddit_status = {"valid": False, "error": "Credentials not configured"}
    except Exception as e:
        print(f"Reddit configuration error: {e}")
        reddit_status = {
            "valid": False,
            "error": str(e)
        }
    
    return {
        "facebook": facebook_status,
        "instagram": instagram_status,
        "twitter": twitter_status,
        "reddit": reddit_status
    }


@router.get("/verify-twitter")
async def verify_twitter():
    """
    Verifies Twitter credentials by calling verify_credentials via API v1.1
    """
    api_v1 = get_twitter_v1_client()
    if api_v1 is None:
        return JSONResponse(status_code=400, content={
            "valid": False,
            "error": "Twitter credentials not configured"
        })
    try:
        user = api_v1.verify_credentials()
        if user is None:
            return {"valid": False, "error": "verify_credentials returned None"}
        return {"valid": True, "user": {"id": str(user.id), "name": user.name, "screen_name": user.screen_name}}
    except Exception as e:
        return JSONResponse(status_code=401, content={
            "valid": False,
            "error": str(e)
        })

