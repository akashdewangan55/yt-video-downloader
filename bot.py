import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = "8405906800:AAGWdrBtEyqTWVIP2nSTRHuWruJ7OrzAmek"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Send a YouTube link to download audio/video.")

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if "youtube.com" not in url and "youtu.be" not in url:
        return await update.message.reply_text("❌ Invalid YouTube URL.")

    await update.message.reply_text("⏳ Downloading... Please wait.")

    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',   # Unique filenames
            'quiet': True,
            'nocheckcertificate': True,
            'noplaylist': True,
            'cachedir': False  # Disable cache
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        with open(file_name, 'rb') as f:
            await update.message.reply_video(video=f, caption="✅ Here's your video!")

        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))
    print("📥 YouTube Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()