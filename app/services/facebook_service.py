"""
Facebook posting service
"""
import os
import httpx
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


async def get_facebook_page_id() -> str:
    """
    Get Facebook Page ID from stored credentials or access token
    """
    # Lazy import to avoid circular dependency
    from app.services.credentials_service import get_platform_credentials
    
    # Try to get credentials from storage first
    credentials = get_platform_credentials("facebook")
    access_token = credentials.get("access_token") if credentials else settings.FACEBOOK_ACCESS_TOKEN
    
    if not access_token:
        raise HTTPException(status_code=401, detail="Facebook credentials not configured")
    
    # Fetch page ID from Facebook API using the access token
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.FACEBOOK_GRAPH_URL}/me",
                params={"access_token": access_token}
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]
        except httpx.HTTPError as e:
            print(f"Error fetching page ID: {e}")
            raise HTTPException(status_code=401, detail="Invalid Facebook token")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def post_photo_to_facebook(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Facebook Page
    
    Args:
        image_path: Path to the image file
        caption: Caption text for the post
        
    Returns:
        dict: Response from Facebook API with post ID
    """
    try:
        # Lazy import to avoid circular dependency
        from app.services.credentials_service import get_platform_credentials
        
        # Get credentials from storage first, fallback to env
        credentials = get_platform_credentials("facebook")
        access_token = credentials.get("access_token") if credentials else settings.FACEBOOK_ACCESS_TOKEN
        
        if not access_token:
            raise HTTPException(status_code=401, detail="Facebook access token not configured")
        
        page_id = await get_facebook_page_id()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(image_path, "rb") as image_file:
                files = {
                    "source": (os.path.basename(image_path), image_file, "image/jpeg")
                }
                data = {
                    "message": caption,
                    "access_token": access_token
                }
                
                response = await client.post(
                    f"{settings.FACEBOOK_GRAPH_URL}/{page_id}/photos",
                    files=files,
                    data=data
                )
                response.raise_for_status()
                result = response.json()
                
                # Add post URL
                post_id = result.get("id") or result.get("post_id")
                if post_id:
                    result["url"] = f"https://www.facebook.com/{page_id}/posts/{post_id}"
                
                return result
                
    except httpx.HTTPError as e:
        print(f"Error posting to Facebook: {e}")
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json() if e.response.text else str(e)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to post to Facebook: {error_detail}"
            )
        raise HTTPException(status_code=500, detail=f"Failed to post to Facebook: {str(e)}")

