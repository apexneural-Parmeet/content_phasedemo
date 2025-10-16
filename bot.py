#!/usr/bin/env python3
"""
Standalone Telegram Bot for Social Hub
Run independently from the FastAPI server
"""
import asyncio
import sys
import signal
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.telegram_bot_service import telegram_bot
from app.config import settings

# Shutdown flag
shutdown_event = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown_event
    if shutdown_event:
        shutdown_event.set()

async def main():
    """Main entry point for the Telegram bot"""
    global shutdown_event
    
    print("=" * 60)
    print("🤖 Social Hub Telegram Bot")
    print("=" * 60)
    
    # Check if token is configured
    if not settings.TELEGRAM_BOT_TOKEN:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("Please add your Telegram bot token to the .env file")
        print("Example: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    print(f"✅ Bot token configured")
    print(f"🔗 Backend API: http://localhost:{settings.PORT}")
    print("📱 Starting bot polling...")
    print("-" * 60)
    
    shutdown_event = asyncio.Event()
    
    try:
        # Start the bot (runs indefinitely)
        bot_task = asyncio.create_task(telegram_bot.start_bot())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        # Stop the bot
        print("\n🛑 Shutdown initiated...")
        bot_task.cancel()
        
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
        
    except KeyboardInterrupt:
        print("\n\n👋 Keyboard interrupt...")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("🧹 Stopping bot gracefully...")
        try:
            await telegram_bot.stop_bot()
        except:
            pass
        print("✅ Shutdown complete")


if __name__ == "__main__":
    print("\n💡 TIP: Make sure the backend server is running first!")
    print("   Run: python run.py\n")
    
    # Suppress asyncio warnings on shutdown
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*")
    warnings.filterwarnings("ignore", message=".*Task was destroyed.*")
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
    except Exception:
        pass
    
    print("✅ Exited cleanly")

