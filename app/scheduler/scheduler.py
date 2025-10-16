"""
APScheduler configuration and scheduled post execution
"""
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from app.scheduler.storage import load_scheduled_posts, save_scheduled_posts
from app.services.facebook_service import post_photo_to_facebook
from app.services.instagram_service import post_photo_to_instagram
from app.services.twitter_service import post_photo_to_twitter
from app.services.reddit_service import post_photo_to_reddit

# Global scheduler instance
scheduler = BackgroundScheduler()


def init_scheduler():
    """Initialize and start the background scheduler"""
    if not scheduler.running:
        scheduler.start()
        print("✅ Scheduler initialized and started")


def run_async_in_thread(coro):
    """
    Helper function to run async coroutines in the background scheduler thread
    
    Args:
        coro: Async coroutine to execute
    """
    loop = None
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        pass


async def execute_scheduled_post_async(post_id: str, image_path: str, caption: str, platforms: dict):
    """
    Execute a scheduled post (async version)
    
    Args:
        post_id: Unique identifier for the scheduled post
        image_path: Path to the image file
        caption: Post caption
        platforms: Dict of selected platforms
    """
    try:
        print(f"\n{'='*60}")
        print(f"EXECUTING SCHEDULED POST: {post_id}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Caption: {caption[:50]}...")
        print(f"{'='*60}\n")
        
        results = {
            "facebook": {"success": False, "error": None},
            "instagram": {"success": False, "error": None},
            "twitter": {"success": False, "error": None},
            "reddit": {"success": False, "error": None}
        }
        
        success_count = 0
        failed_platforms = []
        
        # Post to selected platforms
        if platforms.get("facebook"):
            try:
                fb_result = await post_photo_to_facebook(image_path, caption)
                results["facebook"] = {"success": True, "postId": fb_result.get("id")}
                success_count += 1
                print("✅ SUCCESS: Posted to Facebook")
            except Exception as e:
                results["facebook"] = {"success": False, "error": str(e)}
                failed_platforms.append("Facebook")
                print(f"❌ FAILED: Facebook - {e}")
        
        if platforms.get("instagram"):
            try:
                ig_result = await post_photo_to_instagram(image_path, caption)
                results["instagram"] = {"success": True, "postId": ig_result.get("id")}
                success_count += 1
                print("✅ SUCCESS: Posted to Instagram")
            except Exception as e:
                results["instagram"] = {"success": False, "error": str(e)}
                failed_platforms.append("Instagram")
                print(f"❌ FAILED: Instagram - {e}")
        
        if platforms.get("twitter"):
            try:
                tw_result = await post_photo_to_twitter(image_path, caption)
                results["twitter"] = {"success": True, "postId": tw_result.get("id")}
                success_count += 1
                print("✅ SUCCESS: Posted to Twitter")
            except Exception as e:
                results["twitter"] = {"success": False, "error": str(e)}
                failed_platforms.append("Twitter")
                print(f"❌ FAILED: Twitter - {e}")
        
        if platforms.get("reddit"):
            try:
                rd_result = await post_photo_to_reddit(image_path, caption)
                results["reddit"] = {"success": True, "postId": rd_result.get("id")}
                success_count += 1
                print("✅ SUCCESS: Posted to Reddit")
            except Exception as e:
                results["reddit"] = {"success": False, "error": str(e)}
                failed_platforms.append("Reddit")
                print(f"❌ FAILED: Reddit - {e}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"SCHEDULED POST EXECUTION SUMMARY")
        print(f"Post ID: {post_id}")
        print(f"Success: {success_count} platforms")
        if failed_platforms:
            print(f"Failed: {', '.join(failed_platforms)}")
        print(f"{'='*60}\n")
        
        # Mark post as posted instead of deleting
        posts = load_scheduled_posts()
        for post in posts:
            if post["id"] == post_id:
                post["status"] = "posted"
                post["posted_at"] = datetime.now().isoformat()
                post["posted_to"] = success_count
                post["failed_platforms"] = failed_platforms
                break
        save_scheduled_posts(posts)
        
        print(f"✅ COMPLETED: Scheduled post {post_id} executed successfully")
        print(f"   Posted to {success_count} platform(s)")
        if failed_platforms:
            print(f"   Failed: {', '.join(failed_platforms)}")
        print(f"   Status updated to 'posted' in calendar")
        print(f"\n")
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR executing scheduled post {post_id}: {e}\n")


def execute_scheduled_post(post_id: str, image_path: str, caption: str, platforms: dict):
    """
    Synchronous wrapper for executing scheduled posts
    
    Args:
        post_id: Unique identifier for the scheduled post
        image_path: Path to the image file
        caption: Post caption
        platforms: Dict of selected platforms
    """
    run_async_in_thread(execute_scheduled_post_async(post_id, image_path, caption, platforms))


def restore_scheduled_jobs():
    """
    Restore scheduled jobs from storage on server startup
    """
    posts = load_scheduled_posts()
    current_time = datetime.now()
    
    for post in posts:
        try:
            schedule_dt = datetime.fromisoformat(post["scheduled_time"].replace('Z', '+00:00'))
            
            # Only reschedule if the time is in the future
            if schedule_dt > current_time:
                scheduler.add_job(
                    func=execute_scheduled_post,
                    trigger=DateTrigger(run_date=schedule_dt),
                    args=[post["id"], post["image_path"], post["caption"], post["platforms"]],
                    id=post["id"],
                    replace_existing=True
                )
                print(f"✅ Restored scheduled post {post['id']} for {schedule_dt}")
            else:
                # Remove expired scheduled posts
                if os.path.exists(post["image_path"]):
                    os.remove(post["image_path"])
                print(f"⚠️ Removed expired scheduled post {post['id']}")
        except Exception as e:
            print(f"❌ Failed to restore scheduled post {post.get('id')}: {e}")
    
    # Clean up expired posts
    posts = [p for p in posts if datetime.fromisoformat(p["scheduled_time"].replace('Z', '+00:00')) > current_time]
    save_scheduled_posts(posts)
    
    print(f"✅ Restored {len(posts)} scheduled posts")

