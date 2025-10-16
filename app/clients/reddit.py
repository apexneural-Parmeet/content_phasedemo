"""
Reddit API client configuration
"""
import praw
from app.config import settings

def get_reddit_client() -> praw.Reddit | None:
    """
    Return authenticated PRAW Reddit client.
    Returns None if credentials are not configured.
    """
    # Lazy import to avoid circular dependency
    from app.services.credentials_service import get_platform_credentials
    
    # Get credentials from storage first, fallback to env
    credentials = get_platform_credentials("reddit")
    
    if credentials:
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        username = credentials.get("username")
        password = credentials.get("password")
        user_agent = credentials.get("user_agent", "SocialHub Bot v1.0")
    else:
        client_id = settings.REDDIT_CLIENT_ID
        client_secret = settings.REDDIT_CLIENT_SECRET
        username = settings.REDDIT_USERNAME
        password = settings.REDDIT_PASSWORD
        user_agent = settings.REDDIT_USER_AGENT
    
    if not all([client_id, client_secret, username, password]):
        return None
    
    try:
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
    except Exception:
        return None

