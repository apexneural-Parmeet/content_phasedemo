"""
Telegram Bot service for social media management
Complete feature parity with web frontend - ENHANCED UX WITH BACK BUTTONS
"""
import os
import uuid
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
import httpx
from fastapi import HTTPException
from app.config import settings
from app.services.ai_service import generate_platform_content, regenerate_platform_content
from app.services.facebook_service import post_photo_to_facebook
from app.services.instagram_service import post_photo_to_instagram
from app.services.twitter_service import post_photo_to_twitter
from app.services.reddit_service import post_photo_to_reddit
from app.scheduler.storage import load_scheduled_posts, save_scheduled_posts
from app.scheduler.scheduler import scheduler, execute_scheduled_post
from apscheduler.triggers.date import DateTrigger
from app.services.telegram_auth import telegram_auth, require_login, require_login_callback

# Conversation states
(MENU, GENERATE_TOPIC, GENERATE_TONE, GENERATE_PROVIDER, GENERATE_STYLE, 
 APPROVE_PLATFORMS, CREATE_CAPTION, CREATE_IMAGE, CREATE_PLATFORMS, 
 SCHEDULE_TIME, VIEW_SCHEDULE_DETAIL, LOGIN_ID, LOGIN_PASSWORD, 
 EDIT_CAPTION, EDIT_PLATFORM_SELECT) = range(15)

# User session storage
user_sessions = {}


class TelegramBotService:
    """Handles all Telegram bot interactions with smooth back navigation"""
    
    def __init__(self):
        self.application = None
    
    # ==================== COMMAND HANDLERS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command - Check login first"""
        user = update.effective_user
        
        if not telegram_auth.is_logged_in(user.id):
            await update.message.reply_text(
                "👋 *Welcome to Social Hub Bot!*\n\n"
                "🔒 Please login to continue.\n\n"
                "Use /login to authenticate.",
                parse_mode='Markdown'
            )
            return
        
        # User is logged in, show main menu
        keyboard = [
            [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
            [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
            [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
            [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")],
            [InlineKeyboardButton("🚪 Logout", callback_data="menu_logout")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 *Social Hub Bot - Main Menu*\n\n"
            "📱 Features:\n"
            "• AI content generation (Nano Banana or DALL-E)\n"
            "• Manual post creation\n"
            "• Schedule posts\n"
            "• Multi-platform publishing\n\n"
            "What would you like to do?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return MENU
    
    async def login_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /login command"""
        user = update.effective_user
        
        if telegram_auth.is_logged_in(user.id):
            await update.message.reply_text(
                "✅ *Already Logged In*\n\n"
                "You are already logged in.\n"
                "Use /start to access the menu.",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            "🔐 *Login Required*\n\n"
            "Please enter your Login ID:",
            parse_mode='Markdown'
        )
        return LOGIN_ID
    
    async def login_id_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle login ID input"""
        user = update.effective_user
        login_id = update.message.text.strip()
        context.user_data['login_id'] = login_id
        
        print(f"🔐 Login ID received from user {user.id}: {login_id}")
        
        await update.message.reply_text(
            "🔑 *Password Required*\n\n"
            "Please enter your password:",
            parse_mode='Markdown'
        )
        return LOGIN_PASSWORD
    
    async def login_password_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle password input and verify login"""
        user = update.effective_user
        password = update.message.text.strip()
        login_id = context.user_data.get('login_id', '')
        
        print(f"🔑 Password received from user {user.id}")
        print(f"   Login ID: {login_id}")
        print(f"   Attempting verification...")
        
        # Delete the password message for security
        try:
            await update.message.delete()
        except:
            pass
        
        if telegram_auth.verify_login(user.id, login_id, password):
            print(f"✅ Login successful for user {user.id}")
            await update.message.reply_text(
                "✅ *Login Successful!*\n\n"
                f"Welcome, {user.first_name}!\n\n"
                "Use /start to access the menu.",
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ConversationHandler.END
        else:
            print(f"❌ Login failed for user {user.id}")
            await update.message.reply_text(
                "❌ *Login Failed*\n\n"
                "Invalid Login ID or Password.\n\n"
                "Please try again with /login",
                parse_mode='Markdown'
            )
            context.user_data.clear()
            return ConversationHandler.END
    
    async def logout_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle logout"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        telegram_auth.logout_user(user.id)
        
        await query.edit_message_text(
            "🚪 *Logged Out*\n\n"
            "You have been logged out successfully.\n\n"
            "Use /login to login again.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    
    # ==================== MENU HANDLERS ====================
    
    @require_login_callback
    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle main menu selections"""
        query = update.callback_query
        
        # Answer callback to prevent timeout (ignore if expired)
        try:
            await query.answer()
        except:
            pass
        
        # Handle logout
        if query.data == "menu_logout":
            return await self.logout_handler(update, context)
        
        if query.data == "menu_generate":
            # Add back button to topic input
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "🤖 *AI Content Generator*\n\n"
                "Enter your topic or idea:\n\n"
                "_Examples:_\n"
                "• Product launch announcement\n"
                "• Coffee morning vibes\n"
                "• Weekend sale event\n"
                "• Team achievement celebration",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return GENERATE_TOPIC
        
        elif query.data == "menu_create":
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📝 *Create Manual Post*\n\n"
                "Step 1: Send me your image\n\n"
                "You can send a photo or upload an image file.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return CREATE_IMAGE
        
        elif query.data == "menu_schedule":
            posts = load_scheduled_posts()
            
            if not posts:
                keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(
                    "📅 *No Scheduled Posts*\n\n"
                    "Use the menu to create your first post!",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return MENU
            
            # Sort ALL posts by scheduled time
            scheduled = sorted(
                [p for p in posts if p.get('status') != 'posted'],
                key=lambda x: x.get('scheduled_time', '')
            )
            posted = sorted(
                [p for p in posts if p.get('status') == 'posted'],
                key=lambda x: x.get('posted_at', x.get('scheduled_time', '')),
                reverse=True
            )
            
            # Platform shortforms
            plat_short = {
                'facebook': 'FB', 'instagram': 'IG',
                'twitter': 'X', 'reddit': 'RD'
            }
            
            now = datetime.now()
            message = "📅 *SCHEDULE OVERVIEW*\n\n"
            
            # UPCOMING POSTS
            if scheduled:
                message += f"⏰ *UPCOMING* ({len(scheduled)})\n"
                message += "━━━━━━━━━━━━━━━\n"
                
                for idx, post in enumerate(scheduled, 1):
                    post_time = datetime.fromisoformat(post['scheduled_time'])
                    
                    # Date & Time
                    date_str = post_time.strftime('%b %d')
                    time_str = post_time.strftime('%H:%M')
                    
                    # Time until
                    time_until = post_time - now
                    hours = int(time_until.total_seconds() // 3600)
                    if hours < 1:
                        mins = int(time_until.total_seconds() // 60)
                        countdown = f"{mins}m"
                    elif hours < 24:
                        countdown = f"{hours}h"
                    else:
                        days = hours // 24
                        countdown = f"{days}d"
                    
                    # Platforms
                    platforms = [plat_short.get(p, p.upper()[:2]) for p, v in post['platforms'].items() if v]
                    plat_str = "+".join(platforms)
                    
                    # Caption
                    caption = post['caption'][:30] + '...' if len(post['caption']) > 30 else post['caption']
                    
                    message += f"\n*{idx}.* 📅 {date_str} | ⏰ {time_str}\n"
                    message += f"📱 {plat_str}\n"
                    message += f"🔵 Status: *NOT POSTED* (in {countdown})\n"
                    message += f"💬 _{caption}_\n"
            
            # POSTED
            if posted:
                message += f"\n\n✅ *POSTED* ({len(posted)})\n"
                message += "━━━━━━━━━━━━━━━\n"
                
                for idx, post in enumerate(posted, 1):
                    posted_time = datetime.fromisoformat(post.get('posted_at', post['scheduled_time']))
                    
                    # Date & Time
                    date_str = posted_time.strftime('%b %d')
                    time_str = posted_time.strftime('%H:%M')
                    
                    # Platforms
                    platforms = [plat_short.get(p, p.upper()[:2]) for p, v in post['platforms'].items() if v]
                    plat_str = "+".join(platforms)
                    
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
                    caption = post['caption'][:30] + '...' if len(post['caption']) > 30 else post['caption']
                    
                    message += f"\n*{idx}.* 📅 {date_str} | ⏰ {time_str}\n"
                    message += f"📱 {plat_str}\n"
                    message += f"{status_icon} Status: *{status_text}*\n"
                    message += f"💬 _{caption}_\n"
            
            # Summary
            message += f"\n📊 {len(scheduled)} upcoming • {len(posted)} completed"
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="menu_schedule")],
                [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Try to edit message, ignore if unchanged
            try:
                await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            except Exception as e:
                # Message unchanged or other minor error - ignore
                if "not modified" not in str(e):
                    print(f"⚠️  Schedule view update error: {e}")
            
            return MENU
        
        elif query.data == "menu_status":
            message = "📊 *Platform Connection Status*\n\n"
            
            # Check each platform
            platforms_check = {
                "Facebook": settings.FACEBOOK_ACCESS_TOKEN,
                "Instagram": settings.INSTAGRAM_ACCESS_TOKEN,
                "Twitter": settings.TWITTER_API_KEY,
                "Reddit": settings.REDDIT_CLIENT_ID
            }
            
            for name, token in platforms_check.items():
                icon = "🟢" if token else "🔴"
                status = "Connected" if token else "Not configured"
                message += f"{icon} *{name}*: {status}\n"
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            return MENU
        
        elif query.data == "back_menu":
            # Return to main menu
            keyboard = [
                [InlineKeyboardButton("🤖 Generate AI Content", callback_data="menu_generate")],
                [InlineKeyboardButton("📝 Create Manual Post", callback_data="menu_create")],
                [InlineKeyboardButton("📅 View Scheduled Posts", callback_data="menu_schedule")],
                [InlineKeyboardButton("📊 Platform Status", callback_data="menu_status")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎯 *Social Hub Bot - Main Menu*\n\n"
                "What would you like to do?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return MENU
        
        return MENU
    
    # ==================== AI GENERATION FLOW ====================
    
    @require_login
    async def generate_topic_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle topic input for AI generation"""
        user_id = update.effective_user.id
        topic = update.message.text
        
        # Initialize session
        user_sessions[user_id] = {
            "topic": topic,
            "mode": "generate"
        }
        
        # Show tone options with back button
        keyboard = [
            [InlineKeyboardButton("Casual", callback_data="tone_casual"),
             InlineKeyboardButton("Professional", callback_data="tone_professional")],
            [InlineKeyboardButton("Corporate", callback_data="tone_corporate"),
             InlineKeyboardButton("Funny", callback_data="tone_funny")],
            [InlineKeyboardButton("Inspirational", callback_data="tone_inspirational"),
             InlineKeyboardButton("Educational", callback_data="tone_educational")],
            [InlineKeyboardButton("Storytelling", callback_data="tone_storytelling"),
             InlineKeyboardButton("Promotional", callback_data="tone_promotional")],
            [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ Topic: *{topic}*\n\n"
            "Select content tone:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_TONE
    
    async def generate_tone_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle tone selection"""
        query = update.callback_query
        try:
            await query.answer("✅ Tone selected!")
        except:
            pass
        
        user_id = update.effective_user.id
        tone = query.data.replace("tone_", "")
        user_sessions[user_id]["tone"] = tone
        
        # Show image provider options with back button
        keyboard = [
            [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="provider_nano-banana")],
            [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="provider_dalle")],
            [InlineKeyboardButton("« Back", callback_data="back_topic")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Topic: _{user_sessions[user_id]['topic']}_\n"
            f"✅ Tone: *{tone.title()}*\n\n"
            "Select image generator:\n\n"
            "🍌 *Nano Banana* - Ultra-fast, great quality\n"
            "🎨 *DALL-E 3* - Premium quality, slower",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_PROVIDER
    
    async def back_to_topic_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Go back to topic/tone selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Show tone options again
        keyboard = [
            [InlineKeyboardButton("Casual", callback_data="tone_casual"),
             InlineKeyboardButton("Professional", callback_data="tone_professional")],
            [InlineKeyboardButton("Corporate", callback_data="tone_corporate"),
             InlineKeyboardButton("Funny", callback_data="tone_funny")],
            [InlineKeyboardButton("Inspirational", callback_data="tone_inspirational"),
             InlineKeyboardButton("Educational", callback_data="tone_educational")],
            [InlineKeyboardButton("Storytelling", callback_data="tone_storytelling"),
             InlineKeyboardButton("Promotional", callback_data="tone_promotional")],
            [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Topic: *{session.get('topic', '')}*\n\n"
            "Select content tone:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_TONE
    
    async def back_to_provider_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Go back to provider selection"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Show provider options again
        keyboard = [
            [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="provider_nano-banana")],
            [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="provider_dalle")],
            [InlineKeyboardButton("« Back", callback_data="back_topic")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Topic: _{session.get('topic', '')}_\n"
            f"✅ Tone: *{session.get('tone', '').title()}*\n\n"
            "Select image generator:\n\n"
            "🍌 *Nano Banana* - Ultra-fast, great quality\n"
            "🎨 *DALL-E 3* - Premium quality, slower",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_PROVIDER
    
    async def generate_provider_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image provider selection"""
        query = update.callback_query
        provider = query.data.replace("provider_", "")
        provider_name = "Nano Banana ⚡" if provider == "nano-banana" else "DALL-E 3 🎨"
        try:
            await query.answer(f"✅ {provider_name}")
        except:
            pass
        
        user_id = update.effective_user.id
        user_sessions[user_id]["image_provider"] = provider
        
        # Show image style options with back button
        keyboard = [
            [InlineKeyboardButton("Realistic", callback_data="style_realistic"),
             InlineKeyboardButton("Minimal", callback_data="style_minimal")],
            [InlineKeyboardButton("Anime", callback_data="style_anime"),
             InlineKeyboardButton("2D Art", callback_data="style_2d")],
            [InlineKeyboardButton("Comic Book", callback_data="style_comics"),
             InlineKeyboardButton("Sketch", callback_data="style_sketch")],
            [InlineKeyboardButton("Vintage", callback_data="style_vintage"),
             InlineKeyboardButton("Disney", callback_data="style_disney")],
            [InlineKeyboardButton("« Back", callback_data="back_provider")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ Generator: *{provider_name}*\n\n"
            "Select image style:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return GENERATE_STYLE
    
    async def generate_style_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image style selection and trigger generation"""
        query = update.callback_query
        style = query.data.replace("style_", "")
        try:
            await query.answer(f"✅ {style.title()} style!")
        except:
            pass
        
        user_id = update.effective_user.id
        session = user_sessions[user_id]
        session["image_style"] = style
        
        # Get provider name for message
        provider = session.get("image_provider", "dalle")
        provider_name = "Nano Banana ⚡" if provider == "nano-banana" else "DALL-E 3 🎨"
        wait_time = "2-5 sec" if provider == "nano-banana" else "15-20 sec"
        
        # Instant loading feedback
        loading_msg = await query.edit_message_text(
            f"⚡ *Starting generation...*\n\n"
            f"🎯 Topic: {session['topic'][:40]}...\n"
            f"🎭 Tone: {session['tone'].title()}\n"
            f"🖼️ Style: {style.title()}\n"
            f"🤖 Provider: {provider_name}\n\n"
            f"⏱️ Est. time: {wait_time}",
            parse_mode='Markdown'
        )
        
        # Small delay for user to see the summary
        await asyncio.sleep(0.5)
        
        try:
            # Update: Step 1 - Generating content
            await loading_msg.edit_text(
                f"⚡ *Generating...*\n\n"
                f"[▓▓░░░░░░░░] 20%\n"
                f"📝 Creating content...",
                parse_mode='Markdown'
            )
            
            # Generate content using existing service
            result = await generate_platform_content(
                topic=session["topic"],
                tone=session["tone"],
                image_style=session["image_style"],
                generate_image=True,
                use_prompt_enhancer=False,
                image_provider=provider
            )
            
            # Update: Complete
            await loading_msg.edit_text(
                f"✅ *Generation Complete!*\n\n"
                f"[▓▓▓▓▓▓▓▓▓▓] 100%\n"
                f"Sending results...",
                parse_mode='Markdown'
            )
            await asyncio.sleep(0.3)
            
            # Store generated content in session
            session["generated"] = result
            session["approved_platforms"] = []
            session["image_approved"] = False
            
            # Send generated image
            if result["image"]["success"]:
                # Download and send image
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(result["image"]["image_url"])
                    img_path = Path(f"uploads/telegram_temp_{uuid.uuid4().hex[:8]}.png")
                    
                    with open(img_path, "wb") as f:
                        f.write(img_response.content)
                    
                    session["temp_image_path"] = str(img_path)
                    
                    # Send photo with approval buttons
                    keyboard = [
                        [InlineKeyboardButton("✅ Approve Image", callback_data="img_approve"),
                         InlineKeyboardButton("🔄 Regenerate", callback_data="img_regenerate")],
                        [InlineKeyboardButton("« Back to Style", callback_data="back_provider")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    with open(img_path, "rb") as photo:
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=photo,
                            caption="🎨 *AI-Generated Image*\n\nDo you approve this image?",
                            reply_markup=reply_markup,
                            parse_mode='Markdown'
                        )
            
            # Send full content for each platform (separately if needed for long content)
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📝 *Generated Content:*\n\nReview the content for each platform below:",
                parse_mode='Markdown'
            )
            
            # Send each platform's content separately to avoid message length limits
            for platform, data in result["platforms"].items():
                if data["success"]:
                    platform_message = f"*{platform.upper()}:*\n\n{data['content']}"
                    
                    # Telegram has 4096 char limit per message
                    if len(platform_message) > 4000:
                        # Split into chunks if too long
                        chunks = [platform_message[i:i+4000] for i in range(0, len(platform_message), 4000)]
                        for i, chunk in enumerate(chunks):
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=chunk if i == 0 else f"_(continued)_\n{chunk}",
                                parse_mode='Markdown'
                            )
                    else:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=platform_message,
                            parse_mode='Markdown'
                        )
            
            # Platform approval buttons with edit option
            keyboard = [
                [InlineKeyboardButton("✅ Facebook", callback_data="plat_approve_facebook"),
                 InlineKeyboardButton("✅ Instagram", callback_data="plat_approve_instagram")],
                [InlineKeyboardButton("✅ Twitter", callback_data="plat_approve_twitter"),
                 InlineKeyboardButton("✅ Reddit", callback_data="plat_approve_reddit")],
                [InlineKeyboardButton("✏️ Edit Caption", callback_data="edit_caption")],
                [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📱 *Select platforms to approve:*\n(Tap to approve, then Continue)\n\n"
                     "💡 Use 'Edit Caption' to modify content",
                reply_markup=reply_markup
            )
            
            return APPROVE_PLATFORMS
            
        except Exception as e:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"❌ Error generating content:\n{str(e)}\n\nUse /start to try again."
            )
            user_sessions.pop(user_id, None)
            return ConversationHandler.END
    
    async def image_approval_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image approval/rejection/regeneration"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if query.data == "img_approve":
            session["image_approved"] = True
            await query.edit_message_caption(
                caption="✅ *Image Approved!*",
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "img_regenerate":
            # Ask user to select provider again for regeneration
            await query.edit_message_caption(
                caption="🔄 *Regenerate Content & Image*\n\nChoose image generator:",
                parse_mode='Markdown'
            )
            
            # Show provider selection
            keyboard = [
                [InlineKeyboardButton("🍌 Nano Banana (Ultra Fast 2-3s)", callback_data="regen_provider_nano-banana")],
                [InlineKeyboardButton("🎨 DALL-E 3 (Premium 15-20s)", callback_data="regen_provider_dalle")],
                [InlineKeyboardButton("« Cancel", callback_data="img_approve")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="🔄 *Select Image Generator for Regeneration:*\n\n"
                     "🍌 *Nano Banana* - Ultra-fast, great quality\n"
                     "🎨 *DALL-E 3* - Premium quality, slower",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        return APPROVE_PLATFORMS
    
    async def platform_approval_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform selection and publishing options"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Handle provider choice during regeneration
        if query.data.startswith("regen_provider_"):
            provider = query.data.replace("regen_provider_", "")
            session["image_provider"] = provider  # Update provider choice
            
            provider_name = "Nano Banana" if provider == "nano-banana" else "DALL-E 3"
            wait_time = "2-5 seconds" if provider == "nano-banana" else "10-20 seconds"
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"⚡ *Regenerating with {provider_name}...*\n\n_Please wait {wait_time}..._",
                parse_mode='Markdown'
            )
            
            try:
                # Regenerate EVERYTHING (content + image)
                result = await generate_platform_content(
                    topic=session["topic"],
                    tone=session["tone"],
                    image_style=session["image_style"],
                    generate_image=True,
                    use_prompt_enhancer=False,
                    image_provider=provider
                )
                
                # Reset approvals since everything is new
                session["generated"] = result
                session["approved_platforms"] = []
                session["image_approved"] = False
                
                # Delete old temp image
                if "temp_image_path" in session and os.path.exists(session["temp_image_path"]):
                    os.remove(session["temp_image_path"])
                
                # Send new image
                if result["image"]["success"]:
                    async with httpx.AsyncClient() as client:
                        img_response = await client.get(result["image"]["image_url"])
                        img_path = Path(f"uploads/telegram_temp_{uuid.uuid4().hex[:8]}.png")
                        
                        with open(img_path, "wb") as f:
                            f.write(img_response.content)
                        
                        session["temp_image_path"] = str(img_path)
                        
                        keyboard = [
                            [InlineKeyboardButton("✅ Approve Image", callback_data="img_approve"),
                             InlineKeyboardButton("🔄 Regenerate", callback_data="img_regenerate")],
                            [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        with open(img_path, "rb") as photo:
                            await context.bot.send_photo(
                                chat_id=update.effective_chat.id,
                                photo=photo,
                                caption=f"🔄 *Regenerated Image ({provider_name})*\n\nDo you approve this image?",
                                reply_markup=reply_markup,
                                parse_mode='Markdown'
                            )
                
                # Send regenerated content
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="📝 *Regenerated Content:*",
                    parse_mode='Markdown'
                )
                
                for platform, data in result["platforms"].items():
                    if data["success"]:
                        platform_message = f"*{platform.upper()}:*\n\n{data['content']}"
                        
                        if len(platform_message) > 4000:
                            chunks = [platform_message[i:i+4000] for i in range(0, len(platform_message), 4000)]
                            for i, chunk in enumerate(chunks):
                                await context.bot.send_message(
                                    chat_id=update.effective_chat.id,
                                    text=chunk if i == 0 else f"_(continued)_\n{chunk}",
                                    parse_mode='Markdown'
                                )
                        else:
                            await context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=platform_message,
                                parse_mode='Markdown'
                            )
                
                # Platform approval buttons
                keyboard = [
                    [InlineKeyboardButton("✅ Facebook", callback_data="plat_approve_facebook"),
                     InlineKeyboardButton("✅ Instagram", callback_data="plat_approve_instagram")],
                    [InlineKeyboardButton("✅ Twitter", callback_data="plat_approve_twitter"),
                     InlineKeyboardButton("✅ Reddit", callback_data="plat_approve_reddit")],
                    [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                    [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="📱 *Select platforms to approve:*\n(Tap to approve, then Continue)",
                    reply_markup=reply_markup
                )
                
                return APPROVE_PLATFORMS
                
            except Exception as e:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"❌ Regeneration failed:\n{str(e)}\n\nUse /start to try again."
                )
                return ConversationHandler.END
        
        # Handle platform approval toggling
        if query.data.startswith("plat_approve_"):
            platform = query.data.replace("plat_approve_", "")
            
            if platform in session["approved_platforms"]:
                session["approved_platforms"].remove(platform)
                try:
                    await query.answer(f"❌ {platform.title()}", show_alert=False)
                except:
                    pass
            else:
                session["approved_platforms"].append(platform)
                try:
                    await query.answer(f"✅ {platform.title()}", show_alert=False)
                except:
                    pass
            
            # Update button text - instant response
            approved = session["approved_platforms"]
            keyboard = [
                [InlineKeyboardButton(
                    f"{'✅' if 'facebook' in approved else '▫️'} Facebook", 
                    callback_data="plat_approve_facebook"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'instagram' in approved else '▫️'} Instagram", 
                    callback_data="plat_approve_instagram"
                )],
                [InlineKeyboardButton(
                    f"{'✅' if 'twitter' in approved else '▫️'} Twitter", 
                    callback_data="plat_approve_twitter"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'reddit' in approved else '▫️'} Reddit", 
                    callback_data="plat_approve_reddit"
                )],
                [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Faster update with no exceptions
            await query.edit_message_reply_markup(reply_markup=reply_markup)
            
            return APPROVE_PLATFORMS
        
        elif query.data == "edit_caption":
            # Show platform selection for editing
            try:
                await query.answer("✏️ Edit content")
            except:
                pass
            
            keyboard = [
                [InlineKeyboardButton("📘 Facebook", callback_data="edit_select_facebook")],
                [InlineKeyboardButton("📷 Instagram", callback_data="edit_select_instagram")],
                [InlineKeyboardButton("🐦 Twitter/X", callback_data="edit_select_twitter")],
                [InlineKeyboardButton("🤖 Reddit", callback_data="edit_select_reddit")],
                [InlineKeyboardButton("« Back", callback_data="edit_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✏️ *Edit Caption*\n\n"
                     "Select which platform's caption to edit:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return EDIT_PLATFORM_SELECT
        
        elif query.data == "plat_done":
            if not session["approved_platforms"]:
                await query.answer("Please approve at least one platform!", show_alert=True)
                return APPROVE_PLATFORMS
            
            # Show publishing options
            keyboard = [
                [InlineKeyboardButton("🚀 Post Now", callback_data="publish_now")],
                [InlineKeyboardButton("📅 Schedule for Later", callback_data="publish_schedule")],
                [InlineKeyboardButton("« Back", callback_data="back_platforms")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            platforms_str = ", ".join([p.title() for p in session["approved_platforms"]])
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"📱 *Approved Platforms:* {platforms_str}\n\n"
                     "Choose how to publish:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        elif query.data == "publish_now":
            try:
                await query.answer("🚀 Publishing!")
            except:
                pass
            
            platforms_count = len(session["approved_platforms"])
            
            await query.edit_message_text(
                f"🚀 *Publishing to {platforms_count} platform(s)...*\n\n"
                f"Please wait...",
                parse_mode='Markdown'
            )
            
            # Publish to approved platforms
            results = {}
            for idx, platform in enumerate(session["approved_platforms"], 1):
                # Show progress
                await query.edit_message_text(
                    f"🚀 *Publishing...*\n\n"
                    f"[{'▓' * idx}{'░' * (platforms_count - idx)}] {idx}/{platforms_count}\n"
                    f"📤 Posting to {platform.title()}...",
                    parse_mode='Markdown'
                )
                try:
                    image_path = session.get("temp_image_path")
                    content_data = session["generated"]["platforms"][platform]
                    caption = content_data["content"]
                    
                    print(f"🔄 Publishing AI content to {platform}...")
                    
                    # Call platform services with timeout and standardize response
                    if platform == "facebook" and image_path:
                        api_result = await asyncio.wait_for(
                            post_photo_to_facebook(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and ("id" in api_result or "post_id" in api_result):
                            post_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": post_url,
                                "id": api_result.get("id") or api_result.get("post_id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "instagram" and image_path:
                        api_result = await asyncio.wait_for(
                            post_photo_to_instagram(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and "id" in api_result:
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "info": api_result.get("info", f"Media ID: {api_result.get('id')}"),
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "twitter" and image_path:
                        api_result = await asyncio.wait_for(
                            post_photo_to_twitter(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and "id" in api_result:
                            tweet_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": tweet_url,
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "reddit" and image_path:
                        api_result = await asyncio.wait_for(
                            post_photo_to_reddit(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and ("id" in api_result or "url" in api_result):
                            reddit_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": reddit_url,
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    else:
                        results[platform] = {"success": False, "message": "Missing image"}
                    
                    print(f"✅ {platform} result: {results[platform]}")
                        
                except asyncio.TimeoutError:
                    print(f"⏱️ {platform} timeout!")
                    results[platform] = {"success": False, "message": "Request timeout (30s)"}
                except HTTPException as e:
                    print(f"❌ {platform} HTTP error: {e.detail}")
                    results[platform] = {"success": False, "message": e.detail}
                except Exception as e:
                    print(f"❌ {platform} error: {str(e)}")
                    results[platform] = {"success": False, "message": str(e)}
            
            # Send results with clickable links
            message = "📊 *Publishing Results:*\n\n"
            
            for platform, result in results.items():
                # Handle different result formats
                if isinstance(result, dict):
                    success = result.get("success", False)
                    msg = result.get("message", result.get("error", "Unknown error"))
                    post_url = result.get("url", "")
                    post_info = result.get("info", "")
                else:
                    success = False
                    msg = str(result)
                    post_url = ""
                    post_info = ""
                
                icon = "✅" if success else "❌"
                plat_name = platform.upper()
                
                message += f"{icon} *{plat_name}:* {msg}\n"
                
                # Add clickable link if available
                if success and post_url:
                    message += f"   🔗 [View Post]({post_url})\n"
                elif success and post_info:
                    message += f"   📱 {post_info}\n"
                
                message += "\n"
            
            # Clean up temp file
            if "temp_image_path" in session and os.path.exists(session["temp_image_path"]):
                os.remove(session["temp_image_path"])
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            user_sessions.pop(user_id, None)
            return MENU
        
        elif query.data == "publish_schedule":
            # Show current time for reference
            now = datetime.now()
            tomorrow = now + timedelta(days=1)
            
            # Quick schedule buttons
            keyboard = [
                [InlineKeyboardButton("⏰ In 1 Hour", callback_data="quick_1hour"),
                 InlineKeyboardButton("⏰ In 3 Hours", callback_data="quick_3hours")],
                [InlineKeyboardButton("📅 Tomorrow 9 AM", callback_data="quick_tomorrow_9am"),
                 InlineKeyboardButton("📅 Tomorrow 2 PM", callback_data="quick_tomorrow_2pm")],
                [InlineKeyboardButton("✏️ Custom Time", callback_data="custom_time")],
                [InlineKeyboardButton("« Back", callback_data="back_platforms")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📅 *Schedule Post*\n\n"
                f"Current time: `{now.strftime('%Y-%m-%d %H:%M')}`\n\n"
                f"Choose a quick option or enter custom time:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return SCHEDULE_TIME
        
        return APPROVE_PLATFORMS
    
    # ==================== CAPTION EDITING ====================
    
    async def edit_platform_select_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform selection for caption editing"""
        query = update.callback_query
        try:
            await query.answer()
        except:
            pass
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if query.data == "edit_back":
            # Go back to platform approval
            keyboard = [
                [InlineKeyboardButton("✅ Facebook", callback_data="plat_approve_facebook"),
                 InlineKeyboardButton("✅ Instagram", callback_data="plat_approve_instagram")],
                [InlineKeyboardButton("✅ Twitter", callback_data="plat_approve_twitter"),
                 InlineKeyboardButton("✅ Reddit", callback_data="plat_approve_reddit")],
                [InlineKeyboardButton("✏️ Edit Caption", callback_data="edit_caption")],
                [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
                [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📱 *Select platforms to approve:*\n(Tap to approve, then Continue)\n\n"
                "💡 Use 'Edit Caption' to modify content",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return APPROVE_PLATFORMS
        
        # Extract platform from callback
        platform = query.data.replace("edit_select_", "")
        session["editing_platform"] = platform
        
        # Get current caption
        current_caption = session["generated"]["platforms"][platform]["content"]
        
        await query.edit_message_text(
            f"✏️ *Edit {platform.upper()} Caption*\n\n"
            f"*Current caption:*\n{current_caption[:500]}...\n\n"
            f"Send your edited caption below:",
            parse_mode='Markdown'
        )
        
        return EDIT_CAPTION
    
    async def edit_caption_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the edited caption text"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        platform = session.get("editing_platform")
        new_caption = update.message.text
        
        # Update the caption
        if platform and platform in session["generated"]["platforms"]:
            session["generated"]["platforms"][platform]["content"] = new_caption
            
            await update.message.reply_text(
                f"✅ *{platform.upper()} caption updated!*\n\n"
                f"_New caption:_\n{new_caption[:200]}...\n\n"
                f"Would you like to edit another platform?",
                parse_mode='Markdown'
            )
            
            # Show options
            keyboard = [
                [InlineKeyboardButton("✏️ Edit Another", callback_data="edit_caption")],
                [InlineKeyboardButton("✅ Done Editing", callback_data="edit_done")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "Choose an option:",
                reply_markup=reply_markup
            )
            
            return EDIT_PLATFORM_SELECT
        else:
            await update.message.reply_text(
                "❌ Session error. Please use /start to begin again."
            )
            return ConversationHandler.END
    
    async def edit_done_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Finish editing and return to platform approval"""
        query = update.callback_query
        try:
            await query.answer("✅ Editing complete!")
        except:
            pass
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Show updated content for all platforms
        await query.edit_message_text(
            "✅ *Caption editing complete!*\n\n"
            "Updated content sent below.",
            parse_mode='Markdown'
        )
        
        # Send each platform's updated content
        for platform, data in session["generated"]["platforms"].items():
            if data["success"]:
                platform_message = f"*{platform.upper()}:*\n\n{data['content']}"
                
                if len(platform_message) > 4000:
                    chunks = [platform_message[i:i+4000] for i in range(0, len(platform_message), 4000)]
                    for chunk in chunks:
                        await context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=chunk,
                            parse_mode='Markdown'
                        )
                else:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=platform_message,
                        parse_mode='Markdown'
                    )
        
        # Back to platform approval
        keyboard = [
            [InlineKeyboardButton("✅ Facebook", callback_data="plat_approve_facebook"),
             InlineKeyboardButton("✅ Instagram", callback_data="plat_approve_instagram")],
            [InlineKeyboardButton("✅ Twitter", callback_data="plat_approve_twitter"),
             InlineKeyboardButton("✅ Reddit", callback_data="plat_approve_reddit")],
            [InlineKeyboardButton("✏️ Edit Caption", callback_data="edit_caption")],
            [InlineKeyboardButton("🚀 Continue to Publish", callback_data="plat_done")],
            [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="📱 *Select platforms to approve:*\n(Tap to approve, then Continue)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return APPROVE_PLATFORMS
    
    # ==================== MANUAL POST CREATION FLOW ====================
    
    @require_login
    async def create_image_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle image upload for manual post"""
        user_id = update.effective_user.id
        
        # Check if message has a photo
        if not update.message.photo:
            await update.message.reply_text(
                "❌ Please send an image file.\n\n"
                "You can send a photo or upload an image.",
                parse_mode='Markdown'
            )
            return CREATE_IMAGE
        
        # Get the largest photo
        photo = update.message.photo[-1]
        
        # Download the photo
        try:
            file = await photo.get_file()
            
            # Save to uploads directory with absolute path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            filename = f"telegram_manual_{timestamp}_{unique_id}.jpg"
            
            # Get absolute path to uploads directory
            uploads_dir = Path("uploads")
            uploads_dir.mkdir(exist_ok=True)
            filepath = uploads_dir / filename
            
            await file.download_to_drive(str(filepath))
            
            # Verify file was downloaded
            if not filepath.exists():
                raise Exception("Failed to download image")
            
            print(f"✅ Image saved: {filepath}")
            
            # Store in session with absolute path
            user_sessions[user_id] = {
                "mode": "manual",
                "image_path": str(filepath.absolute()),
                "filename": filename
            }
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ *Image Received!*\n\n"
                "Now send me the caption/text for your post:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            return CREATE_CAPTION
            
        except Exception as e:
            await update.message.reply_text(
                f"❌ Error uploading image: {str(e)}\n\n"
                "Please try again.",
                parse_mode='Markdown'
            )
            return CREATE_IMAGE
    
    @require_login
    async def create_caption_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle caption input for manual post"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if not session or session.get("mode") != "manual":
            await update.message.reply_text(
                "❌ Session expired. Please start over with /start",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        caption = update.message.text
        session["caption"] = caption
        
        # Debug: Print session data
        print(f"📝 Caption set for user {user_id}")
        print(f"   Image path: {session.get('image_path')}")
        print(f"   Caption: {caption[:50]}")
        print(f"   Mode: {session.get('mode')}")
        
        # Show platform selection
        keyboard = [
            [InlineKeyboardButton("✅ Facebook", callback_data="manual_plat_facebook"),
             InlineKeyboardButton("✅ Instagram", callback_data="manual_plat_instagram")],
            [InlineKeyboardButton("✅ Twitter", callback_data="manual_plat_twitter"),
             InlineKeyboardButton("✅ Reddit", callback_data="manual_plat_reddit")],
            [InlineKeyboardButton("🚀 Continue", callback_data="manual_plat_done")],
            [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        session["selected_platforms"] = []
        
        await update.message.reply_text(
            f"✅ *Caption Received!*\n\n"
            f"_Preview:_\n{caption[:200]}{'...' if len(caption) > 200 else ''}\n\n"
            "📱 *Select platforms:*\n(Tap to select, then Continue)",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        return CREATE_PLATFORMS
    
    async def create_platforms_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle platform selection for manual post"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        if not session or session.get("mode") != "manual":
            await query.edit_message_text(
                "❌ Session expired. Please start over with /start",
                parse_mode='Markdown'
            )
            return ConversationHandler.END
        
        # Handle platform selection toggle
        if query.data.startswith("manual_plat_"):
            platform = query.data.replace("manual_plat_", "")
            
            if platform == "done":
                # Check if at least one platform selected
                if not session.get("selected_platforms"):
                    await query.answer("Please select at least one platform!", show_alert=True)
                    return CREATE_PLATFORMS
                
                # Show publish options
                platforms_str = ", ".join([p.title() for p in session["selected_platforms"]])
                
                keyboard = [
                    [InlineKeyboardButton("🚀 Post Now", callback_data="manual_publish_now")],
                    [InlineKeyboardButton("📅 Schedule for Later", callback_data="manual_publish_schedule")],
                    [InlineKeyboardButton("« Back", callback_data="manual_back_platforms")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    f"📱 *Selected Platforms:* {platforms_str}\n\n"
                    "Choose how to publish:",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                return CREATE_PLATFORMS
            
            else:
                # Toggle platform selection
                if "selected_platforms" not in session:
                    session["selected_platforms"] = []
                
                if platform in session["selected_platforms"]:
                    session["selected_platforms"].remove(platform)
                    try:
                        await query.answer(f"❌ {platform.title()}", show_alert=False)
                    except:
                        pass
                else:
                    session["selected_platforms"].append(platform)
                    try:
                        await query.answer(f"✅ {platform.title()}", show_alert=False)
                    except:
                        pass
                
                # Update buttons
                selected = session["selected_platforms"]
                keyboard = [
                    [InlineKeyboardButton(
                        f"{'✅' if 'facebook' in selected else '▫️'} Facebook", 
                        callback_data="manual_plat_facebook"
                    ),
                     InlineKeyboardButton(
                        f"{'✅' if 'instagram' in selected else '▫️'} Instagram", 
                        callback_data="manual_plat_instagram"
                    )],
                    [InlineKeyboardButton(
                        f"{'✅' if 'twitter' in selected else '▫️'} Twitter", 
                        callback_data="manual_plat_twitter"
                    ),
                     InlineKeyboardButton(
                        f"{'✅' if 'reddit' in selected else '▫️'} Reddit", 
                        callback_data="manual_plat_reddit"
                    )],
                    [InlineKeyboardButton("🚀 Continue", callback_data="manual_plat_done")],
                    [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Instant button update
                await query.edit_message_reply_markup(reply_markup=reply_markup)
                
                return CREATE_PLATFORMS
        
        # Handle publish options
        elif query.data == "manual_publish_now":
            try:
                await query.answer("🚀 Publishing!")
            except:
                pass
            
            platforms_count = len(session["selected_platforms"])
            
            await query.edit_message_text(
                f"🚀 *Publishing to {platforms_count} platform(s)...*\n\n"
                f"Please wait...",
                parse_mode='Markdown'
            )
            
            # Publish to selected platforms
            results = {}
            image_path = session.get("image_path")
            caption = session.get("caption", "")
            
            # Debug logging
            print(f"📤 Publishing manual post...")
            print(f"   Image path: {image_path}")
            print(f"   Caption: {caption[:50] if caption else 'None'}")
            print(f"   Platforms: {session['selected_platforms']}")
            
            for idx, platform in enumerate(session["selected_platforms"], 1):
                # Show progress
                await query.edit_message_text(
                    f"🚀 *Publishing...*\n\n"
                    f"[{'▓' * idx}{'░' * (platforms_count - idx)}] {idx}/{platforms_count}\n"
                    f"📤 Posting to {platform.title()}...",
                    parse_mode='Markdown'
                )
                try:
                    print(f"🔄 Publishing to {platform}...")
                    
                    # Call platform services with timeout
                    if platform == "facebook":
                        api_result = await asyncio.wait_for(
                            post_photo_to_facebook(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and ("id" in api_result or "post_id" in api_result):
                            post_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": post_url,
                                "id": api_result.get("id") or api_result.get("post_id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "instagram":
                        api_result = await asyncio.wait_for(
                            post_photo_to_instagram(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and "id" in api_result:
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "info": api_result.get("info", f"Media ID: {api_result.get('id')}"),
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "twitter":
                        api_result = await asyncio.wait_for(
                            post_photo_to_twitter(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and "id" in api_result:
                            tweet_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": tweet_url,
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    elif platform == "reddit":
                        api_result = await asyncio.wait_for(
                            post_photo_to_reddit(image_path, caption),
                            timeout=30.0
                        )
                        if api_result and ("id" in api_result or "url" in api_result):
                            reddit_url = api_result.get("url", "")
                            results[platform] = {
                                "success": True, 
                                "message": "Posted successfully!",
                                "url": reddit_url,
                                "id": api_result.get("id")
                            }
                        else:
                            results[platform] = {"success": False, "message": str(api_result)}
                    
                    else:
                        results[platform] = {"success": False, "message": "Platform not supported"}
                    
                    print(f"✅ {platform} result: {results[platform]}")
                        
                except asyncio.TimeoutError:
                    print(f"⏱️ {platform} timeout!")
                    results[platform] = {"success": False, "message": "Request timeout (30s)"}
                except HTTPException as e:
                    print(f"❌ {platform} HTTP error: {e.detail}")
                    results[platform] = {"success": False, "message": e.detail}
                except Exception as e:
                    print(f"❌ {platform} error: {str(e)}")
                    results[platform] = {"success": False, "message": str(e)}
            
            # Send results with clickable links
            message = "📊 *Publishing Results:*\n\n"
            
            for platform, result in results.items():
                # Handle different result formats
                if isinstance(result, dict):
                    success = result.get("success", False)
                    msg = result.get("message", result.get("error", "Unknown error"))
                    post_url = result.get("url", "")
                    post_info = result.get("info", "")
                else:
                    success = False
                    msg = str(result)
                    post_url = ""
                    post_info = ""
                
                icon = "✅" if success else "❌"
                plat_name = platform.upper()
                
                message += f"{icon} *{plat_name}:* {msg}\n"
                
                # Add clickable link if available
                if success and post_url:
                    message += f"   🔗 [View Post]({post_url})\n"
                elif success and post_info:
                    message += f"   📱 {post_info}\n"
                
                message += "\n"
            
            # Clean up temp file
            if session.get("image_path") and os.path.exists(session["image_path"]):
                try:
                    os.remove(session["image_path"])
                except:
                    pass
            
            keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            user_sessions.pop(user_id, None)
            return MENU
        
        elif query.data == "manual_publish_schedule":
            # Show scheduling options
            now = datetime.now()
            
            keyboard = [
                [InlineKeyboardButton("⏰ In 1 Hour", callback_data="quick_1hour"),
                 InlineKeyboardButton("⏰ In 3 Hours", callback_data="quick_3hours")],
                [InlineKeyboardButton("📅 Tomorrow 9 AM", callback_data="quick_tomorrow_9am"),
                 InlineKeyboardButton("📅 Tomorrow 2 PM", callback_data="quick_tomorrow_2pm")],
                [InlineKeyboardButton("✏️ Custom Time", callback_data="custom_time")],
                [InlineKeyboardButton("« Back", callback_data="manual_back_platforms")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📅 *Schedule Post*\n\n"
                f"Current time: `{now.strftime('%Y-%m-%d %H:%M')}`\n\n"
                f"Choose a quick option or enter custom time:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Reuse the SCHEDULE_TIME state and handler
            return SCHEDULE_TIME
        
        elif query.data == "manual_back_platforms":
            # Go back to platform selection
            selected = session.get("selected_platforms", [])
            keyboard = [
                [InlineKeyboardButton(
                    f"{'✅' if 'facebook' in selected else '▫️'} Facebook", 
                    callback_data="manual_plat_facebook"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'instagram' in selected else '▫️'} Instagram", 
                    callback_data="manual_plat_instagram"
                )],
                [InlineKeyboardButton(
                    f"{'✅' if 'twitter' in selected else '▫️'} Twitter", 
                    callback_data="manual_plat_twitter"
                ),
                 InlineKeyboardButton(
                    f"{'✅' if 'reddit' in selected else '▫️'} Reddit", 
                    callback_data="manual_plat_reddit"
                )],
                [InlineKeyboardButton("🚀 Continue", callback_data="manual_plat_done")],
                [InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📱 *Select platforms:*\n(Tap to select, then Continue)",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return CREATE_PLATFORMS
        
        return CREATE_PLATFORMS
    
    async def schedule_time_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle scheduling time input (both callback and message)"""
        user_id = update.effective_user.id
        session = user_sessions.get(user_id, {})
        
        # Check if it's a callback query (quick time button) or text message (custom time)
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            
            now = datetime.now()
            
            # Handle quick time buttons
            if query.data == "quick_1hour":
                scheduled_time = now + timedelta(hours=1)
            elif query.data == "quick_3hours":
                scheduled_time = now + timedelta(hours=3)
            elif query.data == "quick_tomorrow_9am":
                scheduled_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            elif query.data == "quick_tomorrow_2pm":
                scheduled_time = (now + timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
            elif query.data == "custom_time":
                # Ask for custom time
                await query.edit_message_text(
                    "📅 *Enter Custom Time*\n\n"
                    "Send the date and time in this format:\n"
                    "`YYYY-MM-DD HH:MM`\n\n"
                    "*Examples:*\n"
                    f"• `{(now + timedelta(days=1)).strftime('%Y-%m-%d')} 10:30` - Tomorrow 10:30 AM\n"
                    f"• `{(now + timedelta(days=2)).strftime('%Y-%m-%d')} 15:00` - Day after tomorrow 3 PM\n"
                    f"• `{now.strftime('%Y-%m-%d')} {(now + timedelta(hours=2)).strftime('%H:%M')}` - Today in 2 hours\n\n"
                    f"_Current time: {now.strftime('%Y-%m-%d %H:%M')}_",
                    parse_mode='Markdown'
                )
                return SCHEDULE_TIME
            else:
                return SCHEDULE_TIME
            
            # Schedule the post with the selected quick time
            await self._create_scheduled_post(update, session, scheduled_time, user_id, from_callback=True)
            return MENU
        
        else:
            # Handle custom time input from message
            time_str = update.message.text.strip()
            
            try:
                # Try multiple formats
                scheduled_time = None
                formats_to_try = [
                    "%Y-%m-%d %H:%M",
                    "%Y/%m/%d %H:%M",
                    "%d-%m-%Y %H:%M",
                    "%d/%m/%Y %H:%M",
                ]
                
                for fmt in formats_to_try:
                    try:
                        scheduled_time = datetime.strptime(time_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if not scheduled_time:
                    raise ValueError("No valid format matched")
                
                # Check if time is in the future
                now = datetime.now()
                if scheduled_time <= now:
                    time_diff = now - scheduled_time
                    minutes_ago = int(time_diff.total_seconds() / 60)
                    
                    await update.message.reply_text(
                        f"❌ *Time must be in the future!*\n\n"
                        f"🕐 Current time: `{now.strftime('%Y-%m-%d %H:%M')}`\n"
                        f"⏰ Your time: `{scheduled_time.strftime('%Y-%m-%d %H:%M')}`\n"
                        f"📉 That was {minutes_ago} minute(s) ago!\n\n"
                        f"*Suggested times:*\n"
                        f"• `{(now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}` (in 1 hour)\n"
                        f"• `{(now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')}` (in 3 hours)\n"
                        f"• `{(now + timedelta(days=1)).strftime('%Y-%m-%d')} 09:00` (tomorrow 9 AM)",
                        parse_mode='Markdown'
                    )
                    return SCHEDULE_TIME
                
                # Create scheduled post
                await self._create_scheduled_post(update, session, scheduled_time, user_id, from_callback=False)
                return MENU
                
            except ValueError as e:
                now = datetime.now()
                await update.message.reply_text(
                    f"❌ *Could not parse date/time!*\n\n"
                    f"You entered: `{time_str}`\n\n"
                    f"🕐 Current time: `{now.strftime('%Y-%m-%d %H:%M')}`\n\n"
                    f"*Use format:* `YYYY-MM-DD HH:MM`\n\n"
                    f"*Quick suggestions:*\n"
                    f"• `{(now + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M')}` (in 1 hour)\n"
                    f"• `{(now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')}` (in 3 hours)\n"
                    f"• `{(now + timedelta(days=1)).strftime('%Y-%m-%d')} 09:00` (tomorrow 9 AM)\n"
                    f"• `{(now + timedelta(days=1)).strftime('%Y-%m-%d')} 14:00` (tomorrow 2 PM)",
                    parse_mode='Markdown'
                )
                return SCHEDULE_TIME
    
    async def _create_scheduled_post(self, update: Update, session: dict, scheduled_time: datetime, user_id: int, from_callback: bool = False):
        """Helper to create and save scheduled post"""
        # Create scheduled post
        post_id = str(uuid.uuid4())
        
        # Handle both AI generated and manual posts
        if session.get("mode") == "manual":
            # Manual post
            platforms_dict = {p: True for p in session["selected_platforms"]}
            caption = session.get("caption", "")[:100]
            image_path = session.get("image_path", "")
        else:
            # AI generated post
            platforms_dict = {p: True for p in session["approved_platforms"]}
            caption = session["generated"]["platforms"]["facebook"]["content"][:100]
            image_path = session.get("temp_image_path", "")
        
        post_data = {
            "id": post_id,
            "caption": caption,
            "platforms": platforms_dict,
            "scheduled_time": scheduled_time.isoformat(),
            "image_path": image_path,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        
        # Save to storage
        posts = load_scheduled_posts()
        posts.append(post_data)
        save_scheduled_posts(posts)
        
        # Schedule with APScheduler
        scheduler.add_job(
            execute_scheduled_post,
            DateTrigger(run_date=scheduled_time),
            args=[post_id, image_path, caption, platforms_dict],
            id=post_id,
            replace_existing=True
        )
        
        keyboard = [[InlineKeyboardButton("« Back to Menu", callback_data="back_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Calculate time difference
        time_diff = scheduled_time - datetime.now()
        hours = int(time_diff.total_seconds() // 3600)
        minutes = int((time_diff.total_seconds() % 3600) // 60)
        
        time_until = ""
        if hours > 24:
            days = hours // 24
            time_until = f"in {days} day{'s' if days > 1 else ''}"
        elif hours > 0:
            time_until = f"in {hours}h {minutes}m"
        else:
            time_until = f"in {minutes}m"
        
        # Get platform list based on mode
        if session.get("mode") == "manual":
            platforms_list = session.get("selected_platforms", [])
        else:
            platforms_list = session.get("approved_platforms", [])
        
        message_text = (
            f"✅ *Post Scheduled!*\n\n"
            f"📅 Time: `{scheduled_time.strftime('%Y-%m-%d %H:%M')}`\n"
            f"⏰ Will post: {time_until}\n"
            f"📱 Platforms: {', '.join([p.title() for p in platforms_list])}"
        )
        
        if from_callback:
            await update.callback_query.edit_message_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        user_sessions.pop(user_id, None)
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        user_id = update.effective_user.id
        user_sessions.pop(user_id, None)
        
        await update.message.reply_text(
            "❌ Operation cancelled. Use /start to begin again.",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    # ==================== BOT LIFECYCLE ====================
    
    async def start_bot(self):
        """Initialize and start the bot"""
        print("🤖 Initializing Telegram Bot...")
        
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        
        # Login conversation handler
        login_handler = ConversationHandler(
            entry_points=[CommandHandler("login", self.login_command)],
            states={
                LOGIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.login_id_handler)],
                LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.login_password_handler)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)]
        )
        
        # Main conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                MENU: [CallbackQueryHandler(self.menu_handler)],
                GENERATE_TOPIC: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.generate_topic_handler),
                    CallbackQueryHandler(self.menu_handler, pattern="^back_menu$")
                ],
                GENERATE_TONE: [
                    CallbackQueryHandler(self.generate_tone_handler, pattern="^tone_"),
                    CallbackQueryHandler(self.menu_handler, pattern="^back_menu$")
                ],
                GENERATE_PROVIDER: [
                    CallbackQueryHandler(self.generate_provider_handler, pattern="^provider_"),
                    CallbackQueryHandler(self.back_to_topic_handler, pattern="^back_topic$")
                ],
                GENERATE_STYLE: [
                    CallbackQueryHandler(self.generate_style_handler, pattern="^style_"),
                    CallbackQueryHandler(self.back_to_provider_handler, pattern="^back_provider$")
                ],
                APPROVE_PLATFORMS: [
                    CallbackQueryHandler(self.image_approval_handler, pattern="^img_"),
                    CallbackQueryHandler(self.platform_approval_handler),
                ],
                EDIT_PLATFORM_SELECT: [
                    CallbackQueryHandler(self.edit_done_handler, pattern="^edit_done$"),
                    CallbackQueryHandler(self.edit_platform_select_handler, pattern="^edit_select_")
                ],
                EDIT_CAPTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.edit_caption_handler)
                ],
                SCHEDULE_TIME: [
                    CallbackQueryHandler(self.schedule_time_handler),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.schedule_time_handler)
                ],
                CREATE_IMAGE: [
                    MessageHandler(filters.PHOTO, self.create_image_handler),
                    CallbackQueryHandler(self.menu_handler, pattern="^back_menu$")
                ],
                CREATE_CAPTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.create_caption_handler),
                    CallbackQueryHandler(self.menu_handler, pattern="^back_menu$")
                ],
                CREATE_PLATFORMS: [
                    CallbackQueryHandler(self.create_platforms_handler)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel_command)],
            allow_reentry=True
        )
        
        self.application.add_handler(login_handler)
        self.application.add_handler(conv_handler)
        
        print("✅ Telegram Bot ready!")
        print(f"🔐 Login ID: {telegram_auth.login_id}")
        print(f"✅ Currently logged in: {telegram_auth.get_logged_in_count()} user(s)")
        print("🚀 Starting polling...")
        
        # Initialize and start polling (async way)
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Keep running until stopped
        print("✅ Bot is now running! Press Ctrl+C to stop.")
        
        try:
            # Wait indefinitely
            stop_event = asyncio.Event()
            await stop_event.wait()
        except (KeyboardInterrupt, asyncio.CancelledError):
            print("\n🛑 Shutdown signal received...")
    
    async def stop_bot(self):
        """Gracefully stop the bot"""
        if self.application:
            try:
                print("⏹️  Stopping updater...")
                await self.application.updater.stop()
                print("⏹️  Stopping application...")
                await self.application.stop()
                print("⏹️  Shutting down...")
                await self.application.shutdown()
                print("✅ Bot stopped cleanly")
            except Exception as e:
                print(f"⚠️  Shutdown warning: {e}")


# Global instance
telegram_bot = TelegramBotService()
