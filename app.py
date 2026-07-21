import os
import requests
import feedparser

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from openai import OpenAI


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)


# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to CryptoMarketAssist!\n\n"
        "I can help with crypto questions, live prices, and AI market news.\n\n"
        "Available commands:\n"
        "/price btc\n"
        "/price eth\n"
        "/price sol\n"
        "/news\n"
    )


# =========================
# LIVE PRICE COMMAND
# =========================
async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n"
            "/price btc\n"
            "/price eth\n"
            "/price sol\n"
            "/price xrp\n"
            "/price bnb"
        )
        return

    coin = context.args[0].lower()

    coins = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "xrp": "ripple",
        "bnb": "binancecoin",
        "ada": "cardano",
        "doge": "dogecoin",
    }

    coin = coins.get(coin, coin)

    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin}&vs_currencies=usd"
    )

    response = requests.get(url)

    if response.status_code != 200:
        await update.message.reply_text("⚠️ Unable to fetch price right now.")
        return

    data = response.json()

    if coin not in data:
        await update.message.reply_text("❌ Coin not found.")
        return

    current_price = data[coin]["usd"]

    await update.message.reply_text(
        f"💰 {coin.upper()}\n\nCurrent Price: ${current_price:,.2f}"
    )


# =========================
# AI NEWS ANALYSIS
# =========================
async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://news.google.com/rss/search?q=cryptocurrency"

    feed = feedparser.parse(url)

    if not feed.entries:
        await update.message.reply_text("⚠️ No news found right now.")
        return

    headlines = [item.title for item in feed.entries[:5]]
    raw_news = "\n".join(headlines)

    ai_response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a crypto market analyst. Summarize the headlines, "
                    "explain why they matter, and give a short market sentiment "
                    "(Bullish, Bearish, or Neutral). Keep it under 150 words."
                ),
            },
            {
                "role": "user",
                "content": raw_news,
            },
        ],
    )

    summary = ai_response.choices[0].message.content

    await update.message.reply_text(
        f"📰 Crypto Market Intelligence\n\n{summary}"
    )


# =========================
# GENERAL AI CHAT
# =========================
async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful cryptocurrency education assistant. "
                    "Explain concepts clearly. Do not promise profits or guaranteed investment advice."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    answer = response.choices[0].message.content

    await update.message.reply_text(answer)


# =========================
# MAIN APP
# =========================
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("news", news))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
