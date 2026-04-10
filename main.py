import sys
import os
import threading
import traceback
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# === FORCE LOGS (Render ab koi log nahi chupa payega) ===
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🚀 SCRIPT START HUI...", flush=True)

API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"

# --- 1. DUMMY WEB SERVER (Render ko chup rakhne ke liye) ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is perfectly running on Render!")
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    httpd = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"🌐 Web Server Port {port} par chal gaya hai!", flush=True)
    httpd.serve_forever()

# Server ko alag background raste par bhej diya
threading.Thread(target=run_web_server, daemon=True).start()

# --- 2. TELEGRAM BOT CODE ---
print("⏳ Telegram Bot connect ho raha hai...", flush=True)
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    bot = await client.get_me()
    add_link = f"https://t.me/{bot.username}?startchannel=true&admin=invite_users"
    text = (
        f"👋 Hello {message.from_user.first_name}!\n\n"
        "Main ek **Auto Request Approver Bot** hoon.\n"
        "Main aapke channel ki saari pending join requests ko ek second mein accept kar sakta hoon.\n\n"
        "🚀 **Kaise Use Karein:**\n"
        "1. Neeche diye button par click karein.\n"
        "2. Apna Channel select karein.\n"
        "3. Mujhe **Admin** banayein.\n"
        "4. Channel mein aakar `/acceptall` type karein.\n"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Bot To Channel ➕", url=add_link)]])
    await message.reply_text(text, reply_markup=keyboard)

@app.on_message(filters.command("acceptall") & filters.admin)
async def approve_all_requests(client, message):
    chat_id = message.chat.id
    msg = await message.reply_text("Saari pending requests approve ho rahi hain... thoda wait karein.")
    try:
        await client.approve_all_chat_join_requests(chat_id)
        await msg.edit_text("✅ Sabhi pending requests ko successfully channel members bana diya gaya hai!")
    except Exception as e:
        await msg.edit_text(f"❌ Error aaya: {e}")

# --- BOT KO START KARNE KA SABSE BADIYA TARIKA ---
if __name__ == "__main__":
    try:
        print("🚀 BOT KO START KIYA JA RAHA HAI...", flush=True)
        app.run()
    except Exception as e:
        print("\n" + "="*50, flush=True)
        print(f"❌❌❌ ASLI ERROR YAHAN HAI: {e} ❌❌❌", flush=True)
        traceback.print_exc()
        print("="*50 + "\n", flush=True)
