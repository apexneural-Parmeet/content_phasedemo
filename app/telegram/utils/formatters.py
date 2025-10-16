"""
Message formatting utilities for Telegram bot
"""
from datetime import datetime


def format_platform_shortname(platform: str) -> str:
    """Get platform shortform"""
    shortforms = {
        'facebook': 'FB',
        'instagram': 'IG',
        'twitter': 'X',
        'reddit': 'RD'
    }
    return shortforms.get(platform.lower(), platform.upper()[:2])


def format_platforms_list(platforms: list) -> str:
    """Format list of platforms to shortform string"""
    return "+".join([format_platform_shortname(p) for p in platforms])


def format_countdown(time_until_seconds: float) -> str:
    """Format seconds into human-readable countdown"""
    hours = int(time_until_seconds // 3600)
    minutes = int((time_until_seconds % 3600) // 60)
    
    if hours < 1:
        return f"{minutes}m"
    elif hours < 24:
        return f"{hours}h"
    else:
        days = hours // 24
        return f"{days}d"


def format_publishing_result(platform: str, result: dict) -> str:
    """Format a publishing result with optional link"""
    if not isinstance(result, dict):
        return f"❌ *{platform.upper()}:* {str(result)}"
    
    success = result.get("success", False)
    msg = result.get("message", result.get("error", "Unknown error"))
    post_url = result.get("url", "")
    post_info = result.get("info", "")
    
    icon = "✅" if success else "❌"
    plat_name = platform.upper()
    
    result_text = f"{icon} *{plat_name}:* {msg}\n"
    
    # Add clickable link if available
    if success and post_url:
        result_text += f"   🔗 [View Post]({post_url})\n"
    elif success and post_info:
        result_text += f"   📱 {post_info}\n"
    
    return result_text + "\n"


def truncate_text(text: str, max_length: int = 30) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'


def format_schedule_post(post: dict, index: int, now: datetime) -> str:
    """Format a single scheduled post for display"""
    post_time = datetime.fromisoformat(post['scheduled_time'])
    
    # Date & Time
    date_str = post_time.strftime('%b %d')
    time_str = post_time.strftime('%H:%M')
    
    # Time until
    time_until = post_time - now
    countdown = format_countdown(time_until.total_seconds())
    
    # Platforms
    platforms = [p for p, v in post['platforms'].items() if v]
    plat_str = format_platforms_list(platforms)
    
    # Caption
    caption = truncate_text(post['caption'], 30)
    
    return (
        f"\n*{index}.* 📅 {date_str} | ⏰ {time_str}\n"
        f"📱 {plat_str}\n"
        f"🔵 Status: *NOT POSTED* (in {countdown})\n"
        f"💬 _{caption}_\n"
    )


def format_posted_post(post: dict, index: int) -> str:
    """Format a posted post for display"""
    posted_time = datetime.fromisoformat(post.get('posted_at', post['scheduled_time']))
    
    # Date & Time
    date_str = posted_time.strftime('%b %d')
    time_str = posted_time.strftime('%H:%M')
    
    # Platforms
    platforms = [p for p, v in post['platforms'].items() if v]
    plat_str = format_platforms_list(platforms)
    
    # Success count
    posted_count = post.get('posted_to', len(platforms))
    failed = len(platforms) - posted_count
    
    if failed == 0:
        status_icon = "🟢"
        status_text = f"POSTED TO ALL ({posted_count}/{len(platforms)})"
    else:
        status_icon = "🟡"
        status_text = f"PARTIAL ({posted_count}/{len(platforms)})"
    
    # Caption
    caption = truncate_text(post['caption'], 30)
    
    return (
        f"\n*{index}.* 📅 {date_str} | ⏰ {time_str}\n"
        f"📱 {plat_str}\n"
        f"{status_icon} Status: *{status_text}*\n"
        f"💬 _{caption}_\n"
    )

