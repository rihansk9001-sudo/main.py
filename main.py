import sys
import os
import threading
import traceback
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer

# === PYTHON FIX ===
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

print("🚀 SCRIPT START HUI...", flush=True)

# Aapki API aur Admin Details
API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"
ADMIN_ID = 1484173564  # Aapki Admin ID

# Database (File) functions taaki Render restart hone par channels na udey
DB_FILE = "channels.txt"

def load_channels():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

def save_channel(chat_id):
    channels = load_channels()
    channels.add(str(chat_id))
    with open(DB_FILE, "w") as f:
        f.write("\n".join(channels))


# --- DUMMY WEB SERVER ---
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
    httpd.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()


# --- TELEGRAM BOT SETUP ---
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# 1. Naya /start (Auto-Tick Permissions ke saath)
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    bot = await client.get_me()
    # Yahan 'invite_users' aur 'post_messages' auto-tick honge
    add_link = f"https://t.me/{bot.username}?startchannel=true&admin=invite_users+post_messages"
    
    text = (
        f"👋 Hello {message.from_user.first_name}!\n\n"
        "Main ek **Super Admin Bot** hoon.\n\n"
        "🟢 **Mera Kaam:**\n"
        "1. Nayi Join Requests ko 1 second mein Auto-Accept karna.\n"
        "2. Aapke saare channels mein ek saath Broadcast (Post) karna.\n\n"
        "⚠️ **NOTE:** Telegram ke naye rules ke mutabik main PURANI requests ko ek saath accept nahi kar sakta. Unhe aapko ek baar khud accept karna hoga. Par NAYI requests main aane hi nahi dunga!\n\n"
        "👇 **Neeche wale button se mujhe apne channel mein add karein:**"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Add Bot To Channel ✨", url=add_link)]])
    await message.reply_text(text, reply_markup=keyboard)


# 2. Auto-Save Channel (Jaise hi bot channel mein add hoga, ID save kar lega broadcast ke liye)
@app.on_message(filters.new_chat_members)
async def bot_added(client, message):
    bot = await client.get_me()
    for member in message.new_chat_members:
        if member.id == bot.id:
            save_channel(message.chat.id)


# 3. LIVE AUTO-APPROVE (Ye feature naye members ko automatically instantly add karega!)
@app.on_chat_join_request()
async def auto_approve(client, message):
    try:
        await client.approve_chat_join_request(message.chat.id, message.from_user.id)
        print(f"✅ Naya member add hua: {message.from_user.id}")
    except Exception as e:
        print(f"Auto-Approve Error: {e}")


# 4. BROADCAST FEATURE (Sirf Aapke Liye)
@app.on_message(filters.command(["admin", "broadcast"]) & filters.private)
async def broadcast_message(client, message):
    if message.from_user.id != ADMIN_ID:
        return await message.reply_text("❌ Aap Admin nahi hain.")
    
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Galti! Kisi message ya post ko reply karke `/broadcast` likhein.")
    
    channels = load_channels()
    if not channels:
        return await message.reply_text("❌ Mere paas kisi channel ka data nahi hai. Pehle mujhe channels mein add karein.")
    
    await message.reply_text(f"⏳ {len(channels)} channels mein message bhej raha hoon...")
    
    success = 0
    failed = 0
    for chat_id in channels:
        try:
            await message.reply_to_message.copy(int(chat_id))
            success += 1
            await asyncio.sleep(1) # Telegram ban se bachne ke liye delay
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(int(chat_id))
            success += 1
        except Exception:
            failed += 1
            
    await message.reply_text(f"✅ **Broadcast Complete!**\n\n🟢 Success: {success} channels\n🔴 Failed: {failed} channels")


if __name__ == "__main__":
    print("🚀 BOT START HO RAHA HAI...", flush=True)
    app.run()
