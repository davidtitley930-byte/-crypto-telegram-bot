import os
import requests
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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Welcome to CryptoMarketAssist!\n\n"
        "I can help with crypto questions, market education, and updates.\n\n"
        "Try asking me a crypto question."
    )


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Usage:\n/price bitcoin\n/price btc\n/price ethereum"
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
        "doge": "dogecoin"
    }

    coin = coins.get(coin, coin)

    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={coin}&vs_currencies=usd"
    )

    response = requests.get(url)

    if response.status_code != 200:
        await update.message.reply_text("Unable to fetch price.")
        return

    data = response.json()

    if coin not in data:
        await update.message.reply_text("Coin not found.")
        return

    current_price = data[coin]["usd"]

    await update.message.reply_text(
        f"💰 {coin.upper()}\n\nCurrent Price: ${current_price:,}"
    )


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful cryptocurrency education assistant. "
                    "Provide information and explain concepts clearly. "
                    "Do not promise profits or give guaranteed investment advice."
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


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, ask_ai)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
