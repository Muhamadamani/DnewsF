import feedparser
from googletrans import Translator
from telegram import Bot
from datetime import datetime
import jdatetime
import os

# ✅ Load Telegram Bot Token from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@your_channel"

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is not set. Please add it as a GitHub Secret.")

# ✅ Initialize bot and translator
bot = Bot(token=TELEGRAM_TOKEN)
translator = Translator()

# ✅ Use an RSS feed instead of web scraping (to avoid website blocks)
RSS_FEED_URL = "https://www.nu.nl/rss"  # Alternative: "https://feeds.nos.nl/nosnieuwsalgemeen"

def get_dutch_news():
    """Fetch news from the RSS feed"""
    feed = feedparser.parse(RSS_FEED_URL)

    if not feed.entries:
        print("⚠️ No news found in RSS feed.")
        return []

    news_list = []
    for entry in feed.entries[:5]:  # Get top 5 news items
        title = entry.title
        link = entry.link
        news_list.append((title, link))

    return news_list

def get_dates():
    """Get Persian and Dutch dates"""
    now = datetime.now()
    persian_date = jdatetime.date.fromgregorian(year=now.year, month=now.month, day=now.day)
    return now.strftime("%Y-%m-%d"), persian_date.strftime("%Y/%m/%d")

def post_daily_news():
    """Fetch, translate, and post news at 6 AM"""
    dutch_date, persian_date = get_dates()
    news_items = get_dutch_news()

    if not news_items:
        message = "⚠️ امروزه خبری در دسترس نیست. لطفاً بعداً بررسی کنید."
        bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        return

    message = f"📅 **تاریخ شمسی:** {persian_date}\n📅 **تاریخ میلادی:** {dutch_date}\n\n"

    for title, link in news_items:
        translated_title = translator.translate(title, src="nl", dest="fa").text
        message += f"📰 **خبر مهم به هلندی**: {title}\n🔹 **ترجمه فارسی**: {translated_title}\n🔗 [مشاهده خبر]({link})\n\n"

    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")

if __name__ == "__main__":
    post_daily_news()
