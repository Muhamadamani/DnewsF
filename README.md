# 📢 Telegram Dutch News Bot 🇳🇱➡️🇮🇷

A bot that **fetches Dutch news**, translates it into **Persian**, enhances the translation using **ChatGPT**, and posts **new articles every hour** to a **Telegram channel**.

## **🛠 Setup Instructions**

### **1️⃣ Create a Telegram Bot**
1. Go to [@BotFather](https://t.me/BotFather) and create a bot.
2. Copy the **API Token**.

### **2️⃣ Add the Bot to Your Channel**
1. Make the bot an **admin** in your Telegram channel.
2. Use `@YourChannelName` or a **numeric ID** (`-100XXXXXXXXX`).

### **3️⃣ Fork & Set Up GitHub Actions**
1. Fork this repo.
2. Go to **Settings → Secrets → Actions**.
3. Add:
   - **`TELEGRAM_BOT_TOKEN`** → Your bot’s API token.
   - **`OPENAI_API_KEY`** → Your OpenAI API key.

### **4️⃣ Run the Bot**
- **Manually:** Go to **"Actions"** → **"Telegram News Bot"** → **"Run workflow"**.
- **Automatically:** The bot checks for new news **every hour**.

## **⚙️ How It Works**
✅ Fetches **Dutch news** (NU.nl/NOS).  
✅ **Skips ads** and **posts only new articles**.  
✅ **Translates to Persian** & **enhances it via ChatGPT**.  
✅ **Runs every hour** via **GitHub Actions**.

## **📜 License**
MIT License. Open for contributions.

🚀 **Ready to go!** Questions? Open an issue. 😊
