#!/usr/bin/env python3
# --------------------------------------------------------------
# Streamify-FB Telegram Video Downloader Bot with Flask server
# Powered by Bhadresh Tech
# © 2025 Bhadresh Tech. All rights reserved.
# --------------------------------------------------------------

import os
import yt_dlp
import telebot
from dotenv import load_dotenv
import datetime
import requests
from flask import Flask
import threading

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
start_time = datetime.datetime.now()

app = Flask('')

@app.route('/')
def home():
    return "Streamify-FB Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def progress_update(d, msg):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').strip()
        speed = d.get('_speed_str', '???/s')
        eta = d.get('_eta_str', '??')
        text = f"📥 Downloading...\nProgress: {percent}\nSpeed: {speed}\nETA: {eta}"
        try:
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=text)
        except:
            pass
    elif d['status'] == 'finished':
        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="✔ Download complete! Uploading...")

def resolve_redirect_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.url
    except Exception:
        return url  # fallback to original if error occurs

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = (
        "Hello 👋 Welcome to **Streamify‑FB**\n\n"
        "Send me any **Facebook video link**, and I’ll download it for you with fast speed and live progress updates.\n\n"
        "🎯 Powered by Bhadresh Tech"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return

    now = datetime.datetime.now()
    uptime_duration = now - start_time
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m {seconds}s"

    bot.reply_to(message, f"⏱ Bot Uptime: {uptime_str}")

@bot.message_handler(func=lambda msg: True)
def handle_links(message):
    original_url = message.text.strip()
    url = original_url

    # Automatically resolve share/redirect URLs on Facebook
    if "facebook.com/share/r/" in original_url:
        resolved_url = resolve_redirect_url(original_url)
        bot.reply_to(message, f"Detected Facebook redirect URL.\nUsing resolved URL:\n{resolved_url}")
        url = resolved_url

    if "facebook.com" in url or "fb.watch" in url:
        status_msg = bot.reply_to(message, "Preparing to download...")

        def hook(d):
            progress_update(d, status_msg)

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'noplaylist': True,
            'progress_hooks': [hook]
        }

 @bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip().lower()

    if "facebook.com" in url or "fb.watch" in url:
        # Process Facebook link using your working Facebook video download handler
        # Example placeholder:
        bot.reply_to(message, "✅ Facebook video downloader is working on your link!")
        # Call your FB download logic here

    else:
        # For any other link (YouTube, Instagram, etc.) reply with coming soon
        bot.reply_to(message, "🚧 This feature is coming soon. Please check back later!")



if __name__ == "__main__":
    # Start Flask server in a separate thread
    threading.Thread(target=run_flask).start()
    # Start Telegram bot polling
    bot.infinity_polling()

