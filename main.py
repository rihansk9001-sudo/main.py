import os
import sys
import asyncio
import logging
from pyrogram import Client, filters, idle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Logging setup taaki Render par error dikhe
logging.basicConfig(level=logging.INFO)

# --- CONFIGURATION ---
API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"
ADMIN_ID = 1484173564  # Aapki ID

# Database file (Simple text file to store channel IDs)
DB_FILE = "chats.txt"

def get_chats():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return [int(line.strip()) for line in f.readlines() if line.strip()]

def add_chat(chat_id):
    chats = get_chats()
    if chat_id not in chats:
        with open(DB_FILE, "a") as f:
            f.write(f"{chat_id}\n")

# --- WEB SERVER FOR RENDER ---
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is Live!")
        return

def run_web_server():
    server = HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8080))), handler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# --- BOT CLIENT ---
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# 1. Start Command & Auto-Permission Link
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    bot_info = await client.get_me()
    # Ye link permissions ko auto-tick (right) kar dega
    # invite_users = Pending requests approve karne ke liye
    # post_messages = Broadcast ke liye
    auth_link = f"https://t.me/{bot_info.username}?startchannel=true&admin=invite_users+post_messages+manage_chat+change_info"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD TO CHANNEL (Auto-Tick) ➕", url=auth_link)],
        [InlineKeyboardButton("📢 UPDATES", url="https://t.me/BotNews")]
    ])
    
    await message.reply_text(
        f"👋 **Hello Admin!**\n\nMain aapke channels ki saari Join Requests auto-approve kar sakta hoon aur Broadcast bhi bhej sakta hoon.\n\n"
        "Neeche wale button se mujhe channel mein add karein, permissions apne aap set ho jayengi!",
        reply_markup=keyboard
    )

# 2. Auto-Approve NEW Requests (Jaise hi koi naya join karega)
@app.on_chat_join_request()
async def auto_approve(client, request):
    chat_id = request.chat.id
    user_id = request.from_user.id
    try:
        await client.approve_chat_join_request(chat_id, user_id)
        add_chat(chat_id) # Broadcast list mein channel add karna
    except Exception as e:
        logging.error(f"Error approving: {e}")

# 3. Accept ALL PENDING Requests (Purani bachi hui requests ke liye)
@app.on_message(filters.command("acceptall") & filters.user(ADMIN_ID))
async def accept_all(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Sahi format: `/acceptall -100XXXXID`")
    
    chat_id = int(message.command[1])
    await message.reply_text("⏳ Saari pending requests accept ho rahi hain... thoda time lag sakta hai.")
    try:
        await client.approve_all_chat_join_requests(chat_id)
        await message.reply_text("✅ Sabhi pending members ko channel mein add kar diya gaya hai!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# 4. ADMIN BROADCAST FEATURE
@app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply_text("Kisi message ko reply karke `/broadcast` likhein.")
    
    chats = get_chats()
    if not chats:
        return await message.reply_text("Bot ke paas koi channel list nahi hai.")
    
    sent = 0
    await message.reply_text(f"🚀 {len(chats)} channels mein post bhej raha hoon...")
    
    for chat_id in chats:
        try:
            await message.reply_to_message.copy(chat_id)
            sent += 1
            await asyncio.sleep(0.3) # Flood wait se bachne ke liye
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
            
    await message.reply_text(f"✅ **Broadcast Done!**\nTotal: {sent} channels.")

# Channel ID track karne ke liye
@app.on_message(filters.new_chat_members)
async def track_chats(client, message):
    bot_id = (await client.get_me()).id
    for member in message.new_chat_members:
        if member.id == bot_id:
            add_chat(message.chat.id)
            await client.send_message(ADMIN_ID, f"Bot added to new channel: {message.chat.title} ({message.chat.id})")

print("Bot starting...")
app.run()
