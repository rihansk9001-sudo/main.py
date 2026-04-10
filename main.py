import os
import sys
import asyncio
import traceback
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Logs set karna (Taaki Render crash na kare)
logging.basicConfig(level=logging.INFO)
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("🚀 Script Start Hui...", flush=True)

# API keys jo aapne di thi
API_ID = 33603340
API_HASH = "0f1a7f670519f9e44d0d7fdb6aa8efba"
BOT_TOKEN = "7874642792:AAF08vl1-qcMUHOIUZrL5IwJS1A7zoD5ucw"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)


# --- NAYA /start FEATURE (Channel cleanup ke liye) ---
@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    bot = await client.get_me()
    text = (
        f"👋 Hello {message.from_user.first_name}!\n\n"
        "Main ek **Channel Request Approver Bot** hoon.\n\n"
        "Main channel mein koi message nahi bhejunga. **Kaise use karein:**\n\n"
        "1. Mujhe apne channel mein Admin banayein.\n"
        "2. **Zaroori:** Mujhe **'Add Subscribers'** aur **'Invite users via link'** ki permission dein.\n"
        "3. Channel ki ID nikalne ke liye us channel ka koi message mujhe forwarding karke bhej dein.\n"
        "4. Saari requests accept karne ke liye mujhe yahan inbox mein yeh command dein:\n"
        "👉 `/acceptall -100XXXXXXX` (X ki jagah apni channel ID daalein)."
    )
    await message.reply_text(text)


# --- Forward message se ID nikalne ka feature ---
@app.on_message(filters.forwarded & filters.private)
async def get_forwarded_id(client, message):
    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        chat_title = message.forward_from_chat.title
        await message.reply_text(f"Is Channel/Group ki ID hai: `{chat_id}`\n\nCommand format: `/acceptall {chat_id}`")
    else:
        await message.reply_text("Forwarded message mein ID nahi mili.")


# --- NAYA /acceptall FEATURE (Private Inbox ke liye) ---
@app.on_message(filters.command("acceptall") & filters.private)
async def approve_all_requests_private(client, message):
    # Check karna ki ID di hai ya nahi
    if len(message.command) < 2:
        return await message.reply_text("❌ Galat Format. Sahi tarika: `/acceptall -100XXXXXXX`")
    
    chat_id_str = message.command[1]
    
    # ID ko integer mein badalna
    try:
        chat_id = int(chat_id_str)
    except ValueError:
        return await message.reply_text("❌ ID galat hai, sirf numbers hone chahiye.")

    status_msg = await message.reply_text(f"⏳ Channel ID `{chat_id}` ke liye requests accept kar raha hoon... wait karein.")
    
    try:
        # requests approve karna
        await client.approve_all_chat_join_requests(chat_id)
        
        # Sukriya, channel cleanup feature
        await status_msg.edit_text(f"✅ Channel ID `{chat_id}` ki saari pending requests accept kar li gayi hain! Channel ekdum saaf hai.")
        
    except Exception as e:
        error_text = str(e)
        # Permission error pakadna
        if "USER_NOT_PARTICIPANT" in error_text:
            await status_msg.edit_text("❌ Error aaya: Main us channel mein admin nahi hoon.")
        elif "CHAT_ADMIN_REQUIRED" in error_text:
            await status_msg.edit_text("❌ Error aaya: Bot ke paas **'Add Subscribers'** permission OFF hai.")
        else:
            await status_msg.edit_text(f"❌ Error aaya: `{error_text}`")
        logging.error(f"Approve Error: {traceback.format_exc()}")


# --- BOT KO START KARNE KA FINAL TARIKA ---
if __name__ == "__main__":
    try:
        print("🚀 BOT KO START KIYA JA RAHA HAI...", flush=True)
        # app.run() directly call karna sabse stable hai Python 3.10 mein
        app.run()
    except Exception as e:
        print(f"❌ FATAL ERROR IN MAIN: {e}", flush=True)
        traceback.print_exc()
