"""
Scheduled posts API endpoints
"""
import os
from fastapi import APIRouter, HTTPException
from app.scheduler.storage import load_scheduled_posts, save_scheduled_posts
from app.scheduler.scheduler import scheduler

router = APIRouter(prefix="/api", tags=["scheduled"])


@router.get("/scheduled-posts")
async def get_scheduled_posts():
    """
    Get all scheduled posts
    """
    posts = load_scheduled_posts()
    return {"scheduled_posts": posts}


@router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post(post_id: str):
    """
    Delete a scheduled post
    
    Args:
        post_id: ID of the scheduled post to delete
    """
    try:
        # Remove from scheduler
        try:
            scheduler.remove_job(post_id)
            print(f"✅ Removed job {post_id} from scheduler")
        except Exception as e:
            print(f"Job {post_id} not found in scheduler: {e}")
        
        # Load posts and remove the one with matching ID
        posts = load_scheduled_posts()
        post_to_delete = next((p for p in posts if p["id"] == post_id), None)
        
        if not post_to_delete:
            raise HTTPException(status_code=404, detail="Scheduled post not found")
        
        # Remove image file if it exists
        if os.path.exists(post_to_delete["image_path"]):
            os.remove(post_to_delete["image_path"])
            print(f"✅ Deleted image file: {post_to_delete['image_path']}")
        
        # Remove from posts list
        posts = [p for p in posts if p["id"] != post_id]
        save_scheduled_posts(posts)
        
        print(f"✅ Deleted scheduled post: {post_id}")
        
        return {"success": True, "message": "Scheduled post deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete scheduled post: {str(e)}")

