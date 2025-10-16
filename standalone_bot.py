#!/usr/bin/env python3
"""
Standalone Telegram Bot for Social Hub
Fully self-contained with integrated scheduler - NO backend needed!
"""
import asyncio
import sys
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.telegram_bot_service import telegram_bot
from app.scheduler.scheduler import init_scheduler, restore_scheduled_jobs
from app.config import settings

# Shutdown flag
shutdown_event = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global shutdown_event
    if shutdown_event:
        shutdown_event.set()


async def main():
    """Main entry point for the standalone Telegram bot"""
    global shutdown_event
    
    print("=" * 70)
    print("🤖 Social Hub Telegram Bot (Standalone Mode)")
    print("=" * 70)
    print()
    
    # Validate configuration
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print()
        print("Please add your Telegram bot token to the .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print()
        return
    
    if not settings.OPENAI_API_KEY:
        print("⚠️  WARNING: OPENAI_API_KEY not found - AI features will be limited")
    
    print("✅ Configuration validated")
    print()
    
    # Initialize scheduler (NEW - makes it standalone!)
    print("📅 Initializing scheduler...")
    try:
        init_scheduler()
        print("✅ Scheduler started successfully")
    except Exception as e:
        print(f"❌ Failed to start scheduler: {e}")
        return
    
    # Restore scheduled jobs from storage
    print("🔄 Restoring scheduled posts...")
    try:
        restore_scheduled_jobs()
        print("✅ Scheduled jobs restored")
    except Exception as e:
        print(f"⚠️  Warning: Could not restore jobs: {e}")
    
    print()
    print("-" * 70)
    print("📱 Starting Telegram bot polling...")
    print("-" * 70)
    print()
    print("✨ Bot is now running!")
    print("   • AI content generation enabled")
    print("   • Scheduling enabled")
    print("   • All platforms ready")
    print()
    print("💡 Send /start to your bot in Telegram to begin")
    print()
    print("Press Ctrl+C to stop the bot")
    print("-" * 70)
    print()
    
    shutdown_event = asyncio.Event()
    
    try:
        # Start the bot (runs indefinitely)
        bot_task = asyncio.create_task(telegram_bot.start_bot())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        # Stop the bot gracefully
        print("\n🛑 Shutdown initiated...")
        bot_task.cancel()
        
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        
    except KeyboardInterrupt:
        print("\n\n👋 Keyboard interrupt received...")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("🧹 Stopping bot gracefully...")
        try:
            await telegram_bot.stop_bot()
        except:
            pass
        
        # Shutdown scheduler
        try:
            from app.scheduler.scheduler import scheduler
            if scheduler.running:
                scheduler.shutdown(wait=False)
                print("✅ Scheduler stopped")
        except:
            pass
        
        print("✅ Shutdown complete")
        print()


if __name__ == "__main__":
    print()
    print("🚀 Standalone Telegram Bot - No Backend Required!")
    print()
    
    # Suppress asyncio warnings on shutdown
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*")
    warnings.filterwarnings("ignore", message=".*Task was destroyed.*")
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    
    print("✅ Exited cleanly")
    print()

