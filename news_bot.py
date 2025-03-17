import feedparser
from mtranslate import translate
from telegram import Bot
from datetime import datetime
import jdatetime
import requests
import os

# ✅ Load Telegram Bot Token from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@your_channel"

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is not set. Please add it as a GitHub Secret.")

# ✅ Initialize bot
bot = Bot(token=TELEGRAM_TOKEN)

# ✅ Use an RSS feed (NU.nl)
RSS_FEED_URL = "https://www.nu.nl/rss"

def get_dutch_news():
    """Fetch news from the RSS feed and remove advertisements"""
    feed = feedparser.parse(RSS_FEED_URL)

    if not feed.entries:
        print("⚠️ No news found in RSS feed.")
        return []

    news_list = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link

        # 🛑 **Remove Ads**: Skip if title contains ad-related words
        if any(word in title.lower() for word in ["advertentie", "sponsored", "promotie", "partnerbijdrage"]):
            continue

        news_list.append((title, link))

        # Limit to 5 valid news items
        if len(news_list) == 5:
            break

    return news_list

def get_dates():
    """Get Persian and Dutch dates"""
    now = datetime.now()
    persian_date = jdatetime.date.fromgregorian(year=now.year, month=now.month, day=now.day)
    return persian_date.strftime("%Y/%m/%d"), now.strftime("%Y-%m-%d")

def get_daily_quote():
    """Fetch a new daily quote in Dutch"""
    try:
        response = requests.get("https://zenquotes.io/api/today")
        response.raise_for_status()
        quote_data = response.json()[0]
        dutch_quote = quote_data["q"]
        translated_quote = translate(dutch_quote, "fa", "nl")
        return dutch_quote, translated_quote
    except Exception as e:
        print(f"⚠️ Failed to fetch daily quote: {e}")
        return "Elke dag is een kans om opnieuw te beginnen.", "هر روز فرصتی برای شروع دوباره است."

def post_daily_news():
    """Fetch, translate, and post news at 6 AM"""
    persian_date, dutch_date = get_dates()
    news_items = get_dutch_news()
    dutch_quote, persian_quote = get_daily_quote()

    message = f"📅 **تاریخ شمسی امروز:** {persian_date}\n📅 **تاریخ میلادی:** {dutch_date}\n\n"

    if not news_items:
        message += "⚠️ امروزه خبری در دسترس نیست. لطفاً بعداً بررسی کنید.\n\n"
    else:
        for title, link in news_items:
            translated_title = translate(title, "fa", "nl")
            message += f"📰 **{title}**\n🔹 {translated_title}\n🔗 [مشاهده خبر]({link})\n\n"

    message += f"💡 **{dutch_quote}**\n✨ {persian_quote}\n"

    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")

if __name__ == "__main__":
    post_daily_news()
