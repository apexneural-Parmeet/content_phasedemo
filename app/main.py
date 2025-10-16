"""
Main FastAPI application
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routes import health, posts, scheduled, ai_content, enhance, credentials
from app.scheduler.scheduler import init_scheduler, restore_scheduled_jobs

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Social Media AI Manager",
    description="Multi-platform social media posting and scheduling with AI content generation",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add global rate limit middleware for file upload endpoints
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Apply rate limiting to posting endpoints
    if request.url.path == "/api/post":
        try:
            await limiter.check_request_limit(request, "30/minute")
        except RateLimitExceeded:
            return _rate_limit_exceeded_handler(request, RateLimitExceeded("30 per 1 minute"))
    response = await call_next(request)
    return response

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(health.router)
app.include_router(posts.router)
app.include_router(scheduled.router)
app.include_router(ai_content.router)
app.include_router(enhance.router)
app.include_router(credentials.router)


@app.on_event("startup")
async def startup_event():
    """
    Initialize scheduler and restore jobs on startup
    """
    print("🚀 Starting Social Media AI Manager...")
    init_scheduler()
    restore_scheduled_jobs()
    
    # Auto-load credentials from environment variables on first startup
    from app.services.credentials_service import get_all_credentials, update_platform_credentials
    existing_creds = get_all_credentials()
    
    if not existing_creds:
        print("📥 Loading credentials from environment variables...")
        migrated = []
        
        # Facebook
        if settings.FACEBOOK_ACCESS_TOKEN:
            update_platform_credentials("facebook", {"access_token": settings.FACEBOOK_ACCESS_TOKEN})
            migrated.append("Facebook")
        
        # Instagram
        if settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID:
            update_platform_credentials("instagram", {
                "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                "account_id": settings.INSTAGRAM_ACCOUNT_ID
            })
            migrated.append("Instagram")
        
        # Twitter
        if all([settings.TWITTER_API_KEY, settings.TWITTER_API_SECRET, 
                settings.TWITTER_ACCESS_TOKEN, settings.TWITTER_ACCESS_TOKEN_SECRET]):
            twitter_creds = {
                "api_key": settings.TWITTER_API_KEY,
                "api_secret": settings.TWITTER_API_SECRET,
                "access_token": settings.TWITTER_ACCESS_TOKEN,
                "access_token_secret": settings.TWITTER_ACCESS_TOKEN_SECRET
            }
            if settings.TWITTER_BEARER_TOKEN:
                twitter_creds["bearer_token"] = settings.TWITTER_BEARER_TOKEN
            update_platform_credentials("twitter", twitter_creds)
            migrated.append("Twitter")
        
        # Reddit
        if all([settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET,
                settings.REDDIT_USERNAME, settings.REDDIT_PASSWORD]):
            update_platform_credentials("reddit", {
                "client_id": settings.REDDIT_CLIENT_ID,
                "client_secret": settings.REDDIT_CLIENT_SECRET,
                "username": settings.REDDIT_USERNAME,
                "password": settings.REDDIT_PASSWORD,
                "user_agent": settings.REDDIT_USER_AGENT
            })
            migrated.append("Reddit")
        
        # Telegram
        if settings.TELEGRAM_BOT_TOKEN:
            telegram_creds = {"bot_token": settings.TELEGRAM_BOT_TOKEN}
            if hasattr(settings, 'TELEGRAM_CHANNEL_ID') and settings.TELEGRAM_CHANNEL_ID:
                telegram_creds["channel_id"] = settings.TELEGRAM_CHANNEL_ID
            else:
                telegram_creds["channel_id"] = ""
            update_platform_credentials("telegram", telegram_creds)
            migrated.append("Telegram")
        
        if migrated:
            print(f"✅ Loaded credentials for: {', '.join(migrated)}")
        else:
            print("ℹ️  No credentials found in environment variables")
    else:
        print("✅ Using existing saved credentials")
    
    print(f"✅ Server is ready on http://localhost:{settings.PORT}")
    print("📱 All platforms configured")
    print("💡 To start Telegram bot, run: python bot.py")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    from app.scheduler.scheduler import scheduler
    
    if scheduler.running:
        scheduler.shutdown()
        print("👋 Scheduler shut down gracefully")

