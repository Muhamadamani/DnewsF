import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from telegram import Bot
from datetime import datetime
import jdatetime
#add
# ✅ Telegram bot credentials
import os
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if TELEGRAM_TOKEN is None:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is not set. Please add it as a GitHub Secret.")


CHANNEL_ID = "@DuchNewsFa"

# ✅ Initialize bot and translator
bot = Bot(token=TELEGRAM_TOKEN)
translator = Translator()

def get_dutch_news():
    """Scrape the latest news from NOS.nl"""
    url = "https://nos.nl/nieuws"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️ Request failed: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", class_="link-block", limit=5)  # Get top 5 news articles

    news_list = []
    for article in articles:
        title = article.text.strip()
        link = "https://nos.nl" + article["href"]
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
