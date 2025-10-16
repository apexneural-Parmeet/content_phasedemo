"""
Reddit posting service
"""
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_exponential
from app.clients.reddit import get_reddit_client
from app.config import settings


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def post_photo_to_reddit(image_path: str, caption: str) -> dict:
    """
    Post a photo with title (caption) to Reddit subreddit
    
    Args:
        image_path: Path to the image file
        caption: Post title (max 300 characters)
        
    Returns:
        dict: Response with submission ID and URL
    """
    reddit = get_reddit_client()
    if reddit is None:
        raise HTTPException(status_code=500, detail="Reddit credentials not configured")

    try:
        subreddit = reddit.subreddit(settings.REDDIT_SUBREDDIT)
        title = (caption or "Untitled post")[:300]
        submission = subreddit.submit_image(title=title, image_path=image_path)
        return {"id": submission.id, "url": submission.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to post to Reddit: {str(e)}")

