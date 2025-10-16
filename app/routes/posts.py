"""
Posts API endpoints
"""
import os
import json
import uuid
import aiofiles
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from apscheduler.triggers.date import DateTrigger
from app.config import settings
from app.services.facebook_service import post_photo_to_facebook
from app.services.instagram_service import post_photo_to_instagram
from app.services.twitter_service import post_photo_to_twitter
from app.services.reddit_service import post_photo_to_reddit
from app.scheduler.scheduler import scheduler, execute_scheduled_post
from app.scheduler.storage import load_scheduled_posts, save_scheduled_posts

router = APIRouter(prefix="/api", tags=["posts"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/post")
async def create_post(
    photo: UploadFile = File(...),
    caption: str = Form(""),
    platforms: str = Form(None),
    scheduled_time: str = Form(None)
):
    """
    Post a photo with caption to selected platforms (immediately or scheduled)
    Rate limited: 30 requests per minute (applied at app level)
    """
    # Validate file type
    if photo.content_type not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG, PNG, and GIF are allowed."
        )
    
    # Read file and check size
    contents = await photo.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 10MB."
        )
    
    # Save file temporarily
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{photo.filename}"
    file_path = settings.UPLOAD_DIR / filename
    
    try:
        # Write file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)
        
        print(f"Processing upload: {{'filename': '{filename}', 'caption': '{caption}'}}")
        
        # Parse platforms selection
        selected = {"facebook": True, "instagram": True, "twitter": True, "reddit": True}
        if platforms:
            try:
                selected = json.loads(platforms)
            except Exception:
                selected = {"facebook": True, "instagram": True, "twitter": True, "reddit": True}
        
        # Handle scheduled posts
        if scheduled_time:
            try:
                # Parse the scheduled time
                schedule_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                
                # Create a unique post ID
                post_id = str(uuid.uuid4())
                
                # Save post info
                scheduled_post = {
                    "id": post_id,
                    "caption": caption,
                    "image_path": str(file_path),
                    "platforms": selected,
                    "scheduled_time": scheduled_time,
                    "created_at": datetime.now().isoformat(),
                    "status": "scheduled"  # Track status
                }
                
                posts = load_scheduled_posts()
                posts.append(scheduled_post)
                save_scheduled_posts(posts)
                
                # Schedule the job
                scheduler.add_job(
                    func=execute_scheduled_post,
                    trigger=DateTrigger(run_date=schedule_dt),
                    args=[post_id, str(file_path), caption, selected],
                    id=post_id,
                    replace_existing=True
                )
                
                print(f"📅 Post scheduled for {schedule_dt}")
                
                return {
                    "success": True,
                    "message": f"Post scheduled successfully for {schedule_dt.strftime('%B %d, %Y at %I:%M %p')}",
                    "scheduled": True,
                    "post_id": post_id,
                    "scheduled_time": scheduled_time
                }
                
            except Exception as e:
                # Clean up file if scheduling fails
                if file_path.exists():
                    os.remove(file_path)
                raise HTTPException(status_code=400, detail=f"Failed to schedule post: {str(e)}")

        # Execute immediate posting
        results = {
            "facebook": {"success": False, "error": None},
            "instagram": {"success": False, "error": None},
            "twitter": {"success": False, "error": None},
            "reddit": {"success": False, "error": None}
        }
        
        # Post to Facebook
        if selected.get("facebook"):
            try:
                fb_result = await post_photo_to_facebook(str(file_path), caption)
                results["facebook"] = {
                    "success": True,
                    "postId": fb_result.get("id"),
                    "postLink": f"https://www.facebook.com/{fb_result.get('post_id')}" if fb_result.get('post_id') else None
                }
                print("✅ Posted to Facebook successfully")
            except Exception as fb_error:
                results["facebook"] = {
                    "success": False,
                    "error": str(fb_error)
                }
                print(f"❌ Facebook posting failed: {fb_error}")
        
        # Post to Instagram
        if selected.get("instagram"):
            try:
                ig_result = await post_photo_to_instagram(str(file_path), caption)
                results["instagram"] = {
                    "success": True,
                    "postId": ig_result.get("id")
                }
                print("✅ Posted to Instagram successfully")
            except Exception as ig_error:
                results["instagram"] = {
                    "success": False,
                    "error": str(ig_error)
                }
                print(f"❌ Instagram posting failed: {ig_error}")

        # Post to Twitter
        if selected.get("twitter"):
            try:
                tw_result = await post_photo_to_twitter(str(file_path), caption)
                results["twitter"] = {
                    "success": True,
                    "postId": tw_result.get("id")
                }
                print("✅ Posted photo to Twitter successfully")
            except Exception as tw_error:
                results["twitter"] = {
                    "success": False,
                    "error": str(tw_error)
                }
                print(f"❌ Twitter photo posting failed: {tw_error}")

        # Post to Reddit
        if selected.get("reddit"):
            try:
                rd_result = await post_photo_to_reddit(str(file_path), caption)
                results["reddit"] = {
                    "success": True,
                    "postId": rd_result.get("id"),
                    "postUrl": rd_result.get("url")
                }
                print("✅ Posted photo to Reddit successfully")
            except Exception as rd_error:
                results["reddit"] = {
                    "success": False,
                    "error": str(rd_error)
                }
                print(f"❌ Reddit photo posting failed: {rd_error}")
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Determine overall success
        fb_success = results["facebook"]["success"]
        ig_success = results["instagram"]["success"]
        tw_success = results["twitter"]["success"]
        rd_success = results["reddit"]["success"]
        
        successes = []
        if fb_success: successes.append("Facebook")
        if ig_success: successes.append("Instagram")
        if tw_success: successes.append("Twitter")
        if rd_success: successes.append("Reddit")
        
        if len(successes) == 4:
            message = "🎉 Photo posted successfully to all platforms!"
        elif len(successes) > 0:
            message = f"🎉 Posted to {', '.join(successes)}. Others failed."
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to post to any platform"
            )
        
        return {
            "success": fb_success or ig_success or tw_success or rd_success,
            "message": message,
            "results": results
        }
        
    except HTTPException:
        if file_path.exists():
            os.remove(file_path)
        raise
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        
        print(f"Error in /api/post: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to post: {str(e)}"
        )

