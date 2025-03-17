import feedparser
from googletrans import Translator
from telegram import Bot
from datetime import datetime
import jdatetime
import os
import requests
import json
import time

# ✅ Load Telegram Bot Token from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@your_channel"  # Replace with "@YourChannelName" or "-100XXXXXXXXX" for private channels

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is not set. Please add it as a GitHub Secret.")

# ✅ Initialize bot and translator
bot = Bot(token=TELEGRAM_TOKEN)
translator = Translator()

# ✅ Multiple news sources
RSS_FEEDS = [
    "https://www.nu.nl/rss",
    "https://feeds.nos.nl/nosnieuwsalgemeen",
    "https://www.rtlnieuws.nl/service/rss/nieuws",
    "https://www.ad.nl/rss.xml"
]

# ✅ File to store posted news
POSTED_NEWS_FILE = "posted_news.json"

def load_posted_news():
    """Load previously posted news from a file."""
    if os.path.exists(POSTED_NEWS_FILE):
        with open(POSTED_NEWS_FILE, "r") as f:
            return json.load(f)
    return []

def save_posted_news(news_titles):
    """Save posted news titles to a file."""
    with open(POSTED_NEWS_FILE, "w") as f:
        json.dump(news_titles, f)

def get_dutch_news():
    """Fetch news from multiple RSS feeds and remove duplicate articles"""
    news_list = []
    seen_titles = set()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[1:6]:  # Skip the first item (ad) and take next 5
            title = entry.title
            link = entry.link
            if title not in seen_titles:  # Avoid duplicate news
                seen_titles.add(title)
                news_list.append((title, link))

    return news_list

def get_dates():
    """Get Persian and Dutch dates"""
    now = datetime.now()
    persian_date = jdatetime.date.fromgregorian(year=now.year, month=now.month, day=now.day)
    return now.strftime("%Y-%m-%d"), persian_date.strftime("%Y/%m/%d")

def improve_translation(original_text, translated_text):
    """Enhance the translated text using ChatGPT or a free API"""
    try:
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Improve the translation of a news headline while keeping it accurate."},
                {"role": "user", "content": f"Original: {original_text}\nTranslated: {translated_text}\nImprove it further:"}
            ]
        }
        response = requests.post(api_url, headers=headers, json=data)
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ ChatGPT API error: {e}")
        return translated_text  # Return original translation if API fails

def post_new_news():
    """Continuously check for new news and post immediately when available"""
    print("🚀 Bot is running, checking for new news...")
    
    posted_news = load_posted_news()
    
    while True:
        news_items = get_dutch_news()
        new_news = [item for item in news_items if item[0] not in posted_news]

        if new_news:
            dutch_date, persian_date = get_dates()
            message = f"📅 **تاریخ شمسی:** {persian_date}\n📅 **تاریخ میلادی:** {dutch_date}\n\n"

            for title, link in new_news:
                translated_title = translator.translate(title, src="nl", dest="fa").text
                improved_translation = improve_translation(title, translated_title)

                message += f"📰 **خبر مهم به هلندی**: {title}\n🔹 **ترجمه فارسی (بهبود یافته)**: {improved_translation}\n🔗 [مشاهده خبر]({link})\n\n"

                # ✅ Mark news as posted
                posted_news.append(title)

            bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
            save_posted_news(posted_news)

        # ✅ Wait 10 minutes before checking again
        time.sleep(600)

if __name__ == "__main__":
    post_new_news()