#!/usr/bin/env python3
# --------------------------------------------------------------
# StreamifyFB - Facebook Video Downloader Bot with Coming Soon Placeholder for Other Platforms
# Powered by Bhadresh Tech
# © 2025 Bhadresh Tech. All rights reserved.
# --------------------------------------------------------------

import os
import yt_dlp
import telebot
from dotenv import load_dotenv
import datetime
import threading
from flask import Flask

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN)
start_time = datetime.datetime.now()

app = Flask(__name__)

@app.route('/')
def home():
    return "StreamifyFB Bot is running. Facebook download active; other platforms coming soon."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome to StreamifyFB!\n"
        "Send me a Facebook video link to download.\n"
        "Other platforms downloads are coming soon. Stay tuned!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['uptime'])
def send_uptime(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ You are not authorized to use this command.")
        return
    now = datetime.datetime.now()
    uptime_duration = now - start_time
    hours, remainder = divmod(int(uptime_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    bot.reply_to(message, f"⏱ Bot Uptime: {uptime}")

@bot.message_handler(func=lambda message: True)
def handle_links(message):
    url = message.text.strip().lower()

    if "facebook.com" in url or "fb.watch" in url:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'noplaylist': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as video:
                caption = "✅ Facebook video processed by Bhadresh Tech"
                bot.send_video(message.chat.id, video, caption=caption)
            os.remove(filename)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {e}")
    else:
        bot.reply_to(message, "🚧 This download feature for this platform is coming soon! Please check back later.")

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    bot.infinity_polling()
