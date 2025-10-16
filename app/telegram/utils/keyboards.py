"""
Reusable keyboard builders for Telegram bot
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Main menu keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
        [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
        [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
        [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")],
        [InlineKeyboardButton("🚪 Logout", callback_data="menu_logout")]
    ])


def get_back_to_menu_keyboard():
    """Simple back to menu button"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
    ])


def get_tone_selection_keyboard():
    """Tone selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Casual", callback_data="tone_casual"),
         InlineKeyboardButton("Professional", callback_data="tone_professional")],
        [InlineKeyboardButton("Corporate", callback_data="tone_corporate"),
         InlineKeyboardButton("Funny", callback_data="tone_funny")],
        [InlineKeyboardButton("Inspirational", callback_data="tone_inspirational"),
         InlineKeyboardButton("Educational", callback_data="tone_educational")],
        [InlineKeyboardButton("Storytelling", callback_data="tone_storytelling"),
         InlineKeyboardButton("Promotional", callback_data="tone_promotional")],
        [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
    ])


def get_provider_selection_keyboard():
    """Image provider selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="provider_nano-banana")],
        [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="provider_dalle")],
        [InlineKeyboardButton("« Back", callback_data="back_topic")]
    ])


def get_style_selection_keyboard():
    """Image style selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Realistic", callback_data="style_realistic"),
         InlineKeyboardButton("Minimal", callback_data="style_minimal")],
        [InlineKeyboardButton("Anime", callback_data="style_anime"),
         InlineKeyboardButton("2D Art", callback_data="style_2d")],
        [InlineKeyboardButton("Comic Book", callback_data="style_comics"),
         InlineKeyboardButton("Sketch", callback_data="style_sketch")],
        [InlineKeyboardButton("Vintage", callback_data="style_vintage"),
         InlineKeyboardButton("Disney", callback_data="style_disney")],
        [InlineKeyboardButton("« Back", callback_data="back_provider")]
    ])


def get_platform_approval_keyboard(approved_platforms=None, show_edit=True):
    """Platform approval keyboard with optional edit button"""
    if approved_platforms is None:
        approved_platforms = []
    
    keyboard = [
        [InlineKeyboardButton(
            f"{'✅' if 'facebook' in approved_platforms else '▫️'} Facebook", 
            callback_data="plat_approve_facebook"
        ),
         InlineKeyboardButton(
            f"{'✅' if 'instagram' in approved_platforms else '▫️'} Instagram", 
            callback_data="plat_approve_instagram"
        )],
        [InlineKeyboardButton(
            f"{'✅' if 'twitter' in approved_platforms else '▫️'} Twitter", 
            callback_data="plat_approve_twitter"
        ),
         InlineKeyboardButton(
            f"{'✅' if 'reddit' in approved_platforms else '▫️'} Reddit", 
            callback_data="plat_approve_reddit"
        )]
    ]
    
    if show_edit:
        keyboard.append([InlineKeyboardButton("✏️ Edit Caption", callback_data="edit_caption")])
    
    keyboard.extend([
        [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
        [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_manual_platform_keyboard(selected_platforms=None):
    """Manual post platform selection keyboard"""
    if selected_platforms is None:
        selected_platforms = []
    
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{'✅' if 'facebook' in selected_platforms else '▫️'} Facebook", 
            callback_data="manual_plat_facebook"
        ),
         InlineKeyboardButton(
            f"{'✅' if 'instagram' in selected_platforms else '▫️'} Instagram", 
            callback_data="manual_plat_instagram"
        )],
        [InlineKeyboardButton(
            f"{'✅' if 'twitter' in selected_platforms else '▫️'} Twitter", 
            callback_data="manual_plat_twitter"
        ),
         InlineKeyboardButton(
            f"{'✅' if 'reddit' in selected_platforms else '▫️'} Reddit", 
            callback_data="manual_plat_reddit"
        )],
        [InlineKeyboardButton("🚀 Continue", callback_data="manual_plat_done")],
        [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
    ])


def get_quick_schedule_keyboard(prefix=""):
    """Quick schedule time selection keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏰ In 1 Hour", callback_data=f"{prefix}quick_1hour"),
         InlineKeyboardButton("⏰ In 3 Hours", callback_data=f"{prefix}quick_3hours")],
        [InlineKeyboardButton("📅 Tomorrow 9 AM", callback_data=f"{prefix}quick_tomorrow_9am"),
         InlineKeyboardButton("📅 Tomorrow 2 PM", callback_data=f"{prefix}quick_tomorrow_2pm")],
        [InlineKeyboardButton("✏️ Custom Time", callback_data=f"{prefix}custom_time")],
        [InlineKeyboardButton("« Back", callback_data="back_platforms")]
    ])


def get_publish_options_keyboard():
    """Publishing options keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Post Now", callback_data="publish_now")],
        [InlineKeyboardButton("📅 Schedule for Later", callback_data="publish_schedule")],
        [InlineKeyboardButton("« Back", callback_data="back_platforms")]
    ])


def get_manual_publish_options_keyboard():
    """Manual post publishing options keyboard"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Post Now", callback_data="manual_publish_now")],
        [InlineKeyboardButton("📅 Schedule for Later", callback_data="manual_publish_schedule")],
        [InlineKeyboardButton("« Back", callback_data="manual_back_platforms")]
    ])


def get_edit_platform_keyboard():
    """Platform selection for caption editing"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Facebook", callback_data="edit_select_facebook")],
        [InlineKeyboardButton("📷 Instagram", callback_data="edit_select_instagram")],
        [InlineKeyboardButton("🐦 Twitter/X", callback_data="edit_select_twitter")],
        [InlineKeyboardButton("🤖 Reddit", callback_data="edit_select_reddit")],
        [InlineKeyboardButton("« Back", callback_data="edit_back")]
    ])

