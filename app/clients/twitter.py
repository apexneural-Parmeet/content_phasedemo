"""
Twitter API client configuration
"""
import tweepy
from app.config import settings

def get_twitter_v1_client() -> tweepy.API | None:
    """
    Return Tweepy API v1.1 client for media upload.
    Returns None if credentials are not configured.
    """
    # Lazy import to avoid circular dependency
    from app.services.credentials_service import get_platform_credentials
    
    # Get credentials from storage first, fallback to env
    credentials = get_platform_credentials("twitter")
    
    if credentials:
        api_key = credentials.get("api_key")
        api_secret = credentials.get("api_secret")
        access_token = credentials.get("access_token")
        access_token_secret = credentials.get("access_token_secret")
    else:
        api_key = settings.TWITTER_API_KEY
        api_secret = settings.TWITTER_API_SECRET
        access_token = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        return None
    
    auth = tweepy.OAuth1UserHandler(
        api_key,
        api_secret,
        access_token,
        access_token_secret
    )
    return tweepy.API(auth)


def get_twitter_v2_client() -> tweepy.Client | None:
    """
    Return Tweepy v2 Client for create_tweet (write operations).
    Returns None if credentials are not configured.
    """
    # Lazy import to avoid circular dependency
    from app.services.credentials_service import get_platform_credentials
    
    # Get credentials from storage first, fallback to env
    credentials = get_platform_credentials("twitter")
    
    if credentials:
        api_key = credentials.get("api_key")
        api_secret = credentials.get("api_secret")
        access_token = credentials.get("access_token")
        access_token_secret = credentials.get("access_token_secret")
    else:
        api_key = settings.TWITTER_API_KEY
        api_secret = settings.TWITTER_API_SECRET
        access_token = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        return None
    
    try:
        return tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
            wait_on_rate_limit=True
        )
    except Exception:
        return None

