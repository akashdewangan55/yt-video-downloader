import os
from fastapi import FastAPI
import yt_dlp
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from telegram.ext.fastapi import create_app as create_telegram_app

BOT_TOKEN = os.getenv("BOT_TOKEN", "7710160278:AAEuNEnQOfIz2zNMWGWLLNCiNwiBn_4h-gw")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send a YouTube link to download audio/video.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        return await update.message.reply_text("❌ Invalid YouTube URL.")

    msg = await update.message.reply_text("⏳ Downloading... Please wait...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.getsize(file_path) > 49 * 1024 * 1024:
            await msg.edit_text("⚠️ File too large for Telegram (max 50MB).")
            os.remove(file_path)
            return

        with open(file_path, 'rb') as f:
            await update.message.reply_video(video=f, caption="✅ Here's your video!")

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f"⚠️ Error: {e}")

# --- FastAPI and Telegram Webhook ---
app = FastAPI()
bot_app = Application.builder().token(BOT_TOKEN).build()

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

telegram_app = create_telegram_app(bot_app, path=WEBHOOK_PATH)
app.mount("/", telegram_app)

@app.on_event("startup")
async def set_webhook():
    await bot_app.bot.set_webhook(url=WEBHOOK_URL)
