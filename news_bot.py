import feedparser
from telegram import Bot
import os
import requests
import json

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = "@DutchNewsFa"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or OPENAI_API_KEY")

bot = Bot(token=TELEGRAM_TOKEN)

RSS_FEEDS = [
    "https://www.nu.nl/rss",
    "https://feeds.nos.nl/nosnieuwsalgemeen",
    "https://www.rtlnieuws.nl/service/rss/nieuws",
    "https://www.telegraaf.nl/feed/route66.rss",
    "https://sportnieuws.nl/feed"
]

POSTED_NEWS_FILE = "posted_news.json"

def load_posted_news():
    if os.path.exists(POSTED_NEWS_FILE):
        with open(POSTED_NEWS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_posted_news(news_titles):
    with open(POSTED_NEWS_FILE, "w") as f:
        json.dump(news_titles, f)

def get_dutch_news():
    news_list = []
    for rss_url in RSS_FEEDS:
        feed = feedparser.parse(rss_url)
        if len(feed.entries) > 1:
            for entry in feed.entries[1:6]:
                title = entry.title.strip()
                link = entry.link.strip()
                news_list.append((title, link))
    return news_list[:5]

def summarize_and_translate(title, link):
    try:
        api_url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        messages = [
            {"role": "system", "content": "You are a professional translator and summarizer for a Persian-speaking audience."},
            {"role": "user", "content": f"Summarize and translate this Dutch news headline into fluent Persian:\n\nTitle: {title}"}
        ]
        data = {"model": "gpt-3.5-turbo", "messages": messages}
        response = requests.post(api_url, headers=headers, json=data)
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠️ GPT error: {e}")
        return "ترجمه در حال حاضر در دسترس نیست."

def post_new_news():
    posted_news = load_posted_news()
    news_items = get_dutch_news()
    new_news = [(title, link) for title, link in news_items if title not in posted_news]

    if not new_news:
        print("✅ No new news to post.")
        return

    message = ""
    for title, link in new_news:
        translated = summarize_and_translate(title, link)
        message += f"📢 {title}\n📢 {translated}\n🔗 [مشاهده خبر]({link})\n\n"
        posted_news.append(title)

    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
    save_posted_news(posted_news)

if __name__ == "__main__":
    post_new_news()