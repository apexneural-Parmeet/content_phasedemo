"""
Twitter posting service
"""
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential
from app.clients.twitter import get_twitter_v1_client, get_twitter_v2_client


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def post_photo_to_twitter(image_path: str, caption: str) -> dict:
    """
    Post a photo with caption to Twitter using v1.1 upload + v2 create_tweet
    
    Args:
        image_path: Path to the image file
        caption: Tweet text (max 280 characters)
        
    Returns:
        dict: Response with tweet ID
    """
    api_v1 = get_twitter_v1_client()
    if api_v1 is None:
        raise HTTPException(status_code=500, detail="Twitter v1.1 client not configured for media upload")

    client_v2 = get_twitter_v2_client()
    if client_v2 is None:
        raise HTTPException(status_code=500, detail="Twitter v2 client not configured for create_tweet")

    try:
        # Upload media using v1.1 API
        media = api_v1.media_upload(filename=image_path)
        media_id = media.media_id_string
        
        # Create tweet with media using v2 API
        text = (caption or "")[:280]
        resp = client_v2.create_tweet(text=text, media_ids=[media_id])
        
        tweet_id = None
        if resp and hasattr(resp, "data") and resp.data:
            tweet_id = str(resp.data.get("id"))
        
        return {"id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post photo to Twitter: {str(e)}")


async def post_text_to_twitter(caption: str) -> dict:
    """
    Post a text-only tweet (no media) using Twitter API v2
    
    Args:
        caption: Tweet text (max 280 characters)
        
    Returns:
        dict: Response with tweet ID
    """
    client_v2 = get_twitter_v2_client()
    if client_v2 is None:
        raise HTTPException(status_code=500, detail="Twitter credentials not configured for v2")

    try:
        text = (caption or "")[:280]
        resp = client_v2.create_tweet(text=text)
        
        tweet_id = None
        if resp and hasattr(resp, "data") and resp.data:
            tweet_id = str(resp.data.get("id"))
        
        return {"id": tweet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post text to Twitter (v2): {str(e)}")

