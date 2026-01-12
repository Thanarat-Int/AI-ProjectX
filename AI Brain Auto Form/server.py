import time
import json
import os
import threading
from bot import FormBot
from learning_core import BRAIN_CORE

# Load Config
def load_config():
    if not os.path.exists("config.json"):
        print("❌ Config file not found! Please run the UI once to generate config.")
        return None
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Console Logger
def console_log(msg):
    # Add timestamp
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")

def run_server():
    print("🚀 AI Brain Server Mode (Headless) Initialized...")
    
    config = load_config()
    if not config: return

    url = config.get("url", "")
    if not url:
        print("❌ No URL found in config.json")
        return

    loops = int(config.get("loops", 5))
    
    print(f"🎯 Target: {url}")
    print(f"🔄 Loops: {loops}")
    print("------------------------------------------------")

    # Run Bot (Force Headless=True for Server)
    # Note: We pass thread_id=99 for Server Process
    bot = FormBot(url, loops, console_log, headless=True, thread_id=99)
    
    # Optional: Mock UI Callback if needed (or just ignore)
    # bot.on_persona_change = lambda tid, p: print(f"👤 Switched to: {p['name']}")
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 Server Stopped by User")
    except Exception as e:
        print(f"❌ Server Error: {e}")
    finally:
        print("🏁 Server Process Finished")

if __name__ == "__main__":
    run_server()
