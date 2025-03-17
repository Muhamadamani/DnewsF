name: Telegram News Bot

on:
  workflow_dispatch:  # Allows manual trigger
  schedule:
    - cron: '0 5 * * *'  # Runs at 6 AM Netherlands time (UTC+1)

jobs:
  run-script:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install --no-cache-dir feedparser googletrans==4.0.0-rc1 python-telegram-bot jdatetime requests beautifulsoup4

      - name: Check installed packages
        run: pip list

      - name: Run script
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        run: python news_bot.py
