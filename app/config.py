"""
Configuration management for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import cloudinary

# Load environment variables
load_dotenv()

class Settings:
    """Application settings and configuration"""
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", 8000))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    
    # Directories
    UPLOAD_DIR: Path = Path("uploads")
    SCHEDULED_POSTS_FILE: Path = Path("data/storage/scheduled_posts.json")
    
    # File Constraints
    ALLOWED_EXTENSIONS: set = {"image/jpeg", "image/jpg", "image/png", "image/gif"}
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Facebook Configuration
    FACEBOOK_ACCESS_TOKEN: str = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    FACEBOOK_PAGE_ID: str = os.getenv("FACEBOOK_PAGE_ID")
    FACEBOOK_API_VERSION: str = "v18.0"
    
    @property
    def FACEBOOK_GRAPH_URL(self) -> str:
        return f"https://graph.facebook.com/{self.FACEBOOK_API_VERSION}"
    
    # Instagram Configuration
    INSTAGRAM_ACCESS_TOKEN: str = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    INSTAGRAM_ACCOUNT_ID: str = os.getenv("INSTAGRAM_ACCOUNT_ID")
    INSTAGRAM_API_VERSION: str = "v18.0"
    
    @property
    def INSTAGRAM_GRAPH_URL(self) -> str:
        return f"https://graph.facebook.com/{self.INSTAGRAM_API_VERSION}"
    
    # Cloudinary Configuration
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET")
    CLOUDINARY_FOLDER: str = os.getenv("CLOUDINARY_FOLDER", "instagram-uploads")
    
    # Twitter Configuration
    TWITTER_API_KEY: str = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET: str = os.getenv("TWITTER_API_SECRET")
    TWITTER_ACCESS_TOKEN: str = os.getenv("TWITTER_ACCESS_TOKEN")
    TWITTER_ACCESS_TOKEN_SECRET: str = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN")
    
    # Reddit Configuration
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME: str = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD: str = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "SocialMediaManager/1.0")
    REDDIT_SUBREDDIT: str = os.getenv("REDDIT_SUBREDDIT", "test")
    
    # Public URL
    PUBLIC_BASE_URL: str = os.getenv("PUBLIC_BASE_URL")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Fal.ai Configuration
    FAL_KEY: str = os.getenv("FAL_KEY")
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID")

# Create settings instance
settings = Settings()

# Initialize directories
settings.UPLOAD_DIR.mkdir(exist_ok=True)

# Configure Cloudinary if credentials are provided
if all([settings.CLOUDINARY_CLOUD_NAME, settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

