import feedparser
from googletrans import Translator
from telegram import Bot
import os
import requests
import json

# ✅ Load Telegram Bot Token from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@DuchNewsFa"  # Replace with "@YourChannelName" or "-100XXXXXXXXX" for private channels

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN is not set. Please add it as a GitHub Secret.")

# ✅ Initialize bot and translator
bot = Bot(token=TELEGRAM_TOKEN)
translator = Translator()

# ✅ List of Dutch news sources
RSS_FEEDS = [
    "https://www.nu.nl/rss",  
    "https://feeds.nos.nl/nosnieuwsalgemeen",  
    "https://www.rtlnieuws.nl/service/rss/nieuws",  
    "https://www.telegraaf.nl/feed/route66.rss"  
]

# ✅ File to store posted news titles
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
    """Fetch news from multiple RSS feeds and remove ads"""
    news_list = []
    for rss_url in RSS_FEEDS:
        feed = feedparser.parse(rss_url)
        if len(feed.entries) > 1:
            for entry in feed.entries[1:6]:  # Skip the first item (often an ad)
                title = entry.title
                link = entry.link
                news_list.append((title, link))

    return news_list[:5]  # Limit total news items to 5 per update

def improve_translation(original_text, translated_text):
    """Enhance the translated text using ChatGPT or a free API"""
    try:
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",  # Store your API key as a secret
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
        return translated_text  # Return the original translation if API fails

def post_new_news():
    """Fetch, translate, enhance, and post only new news items every hour"""
    news_items = get_dutch_news()

    if not news_items:
        print("⚠️ No new news available.")
        return

    # ✅ Load previously posted news
    posted_news = load_posted_news()
    new_news = [item for item in news_items if item[0] not in posted_news]

    if not new_news:
        print("✅ No new articles to post.")
        return

    message = ""

    for title, link in new_news:
        translated_title = translator.translate(title, src="nl", dest="fa").text
        improved_translation = improve_translation(title, translated_title)  # Improve translation

        message += f"📢 {title}\n📢 {improved_translation}\n🔗 [مشاهده خبر]({link})\n\n"

        # ✅ Mark news as posted
        posted_news.append(title)

    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")

    # ✅ Save the updated list of posted news
    save_posted_news(posted_news)

if __name__ == "__main__":
    post_new_news()
