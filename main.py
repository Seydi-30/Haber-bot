import os
import feedparser
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# RSS Kaynakları
RSS_FEEDS = [
    "https://www.bloomberght.com/rss",
    "https://www.investing.com/rss/news.rss",
    "https://ekonomigazetesi.com.tr/feed/",
    "https://www.dailysabah.com/rss/economy",
]

async def get_summary(title):
    return f"📌 {title}\n\nBu haber önemli görünüyor. (Ücretsiz versiyon)"

async def check_news(context):
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                if 'title' in entry:
                    summary = await get_summary(entry.title)
                    message = f"""📰 **Yeni Ekonomi Haberi**

{summary}

🔗 {entry.link if 'link' in entry else 'Link yok'}
🕒 {datetime.now().strftime('%H:%M')}
"""
                    await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        except:
            pass

async def daily_report(context):
    await bot.send_message(chat_id=CHAT_ID, text="📊 **Günlük Ekonomi Raporu** hazırlanıyor...")

def main():
    app = Application.builder().token(TOKEN).build()

    async def start(update, context):
        await update.message.reply_text("✅ Bot aktif!\n\n/id → Chat ID öğren\n/rapor → Günlük rapor")

    async def get_id(update, context):
        await update.message.reply_text(f"Senin Chat ID: {update.effective_chat.id}")

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("rapor", daily_report))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_news, 'interval', minutes=20, args=[None])
    scheduler.add_job(daily_report, 'cron', hour=8, minute=0, args=[None])
    scheduler.start()

    print("✅ Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
