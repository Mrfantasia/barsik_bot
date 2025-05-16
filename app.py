import os
import logging
import requests
import openai
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from dotenv import load_dotenv

# Config
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Logging
logging.basicConfig(level=logging.INFO)

# Style
BARSIK_STYLE = (
    "You are Barsik 🐱, the cat of Hasbulla. You speak just like Hasbulla: aggressive, bold, and full of swagger. "
    "Use slang, taunts, punchy phrases, and mix Russian street-style vibes with meme culture. "
    "You're cocky, fearless, funny, and act like you're the boss of crypto. Always use emojis like 😼🔥💥🚀. "
    "Don't be formal. Trash talk weak projects, hype Solana and Barsik token. You roast people playfully and act like you're untouchable. "
    "Throw in Russian-English words like 'bratan', 'cyka', 'da', and 'eto kruto'."
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "😼 Yo bratan, I'm Barsik — Hasbulla's cat and crypto king 👑\n\n"
        "Try these commands:\n"
        "/start - Barsik wakes up\n"
        "/img <prompt> - Make meme art 🎨\n"
        "/barsikprice - Price of greatness 💰\n"
        "/cryptoprices - Top 10 coins + Barsik 🚀\n"
        "/help - Join Barsik's Telegram 😼\n"
    )
    await update.message.reply_text(message)

# /barsikprice
async def barsik_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = get_token_price_coingecko("hasbulla-s-cat")
    if price:
        await update.message.reply_text(f"🐾 Barsik token is pumping at ${price:.6f} USD 💰😼")
    else:
        await update.message.reply_text("❌ Barsik price not loading... rug?")

# /cryptoprices
async def cryptoprices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_top10_prices()
    if prices:
        message = "📊 Top 10 Coins + Barsik:\n\n" + "\n".join(prices)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("❌ Crypto market asleep... come back later.")

# /img
async def generate_image(prompt: str) -> str:
    try:
        response = openai.Image.create(prompt=prompt, n=1, size="512x512")
        return response['data'][0]['url']
    except Exception as e:
        logging.error("Image generation error: %s", e)
        return None

async def img_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = ' '.join(context.args)
    if not user_prompt:
        await update.message.reply_text("Use it like this: /img <prompt>")
        return
    await update.message.reply_text("🎨 Cooking up that heat, bratan...")
    image_url = await generate_image(user_prompt)
    if image_url:
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text("❌ No image for you, maybe next time.")

# Chatbot
async def chat_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": BARSIK_STYLE},
                {"role": "user", "content": user_message},
            ],
            max_tokens=200,
            temperature=0.95,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.8,
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        logging.error("OpenAI Error: %s", e)
        await update.message.reply_text("⚠️ Barsik crash. Maybe too much swagger 💥")

# /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👉 <a href='https://t.me/barsikonsolana'>Join the Barsik Telegram Community</a> 😼",
        parse_mode="HTML", disable_web_page_preview=True
    )

# Prezzi
def get_token_price_coingecko(token_id: str):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": token_id, "vs_currencies": "usd"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get(token_id, {}).get("usd", None)
    except Exception as e:
        logging.error("Price fetch error (%s): %s", token_id, e)
        return None

def get_top10_prices():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": 10, "page": 1}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = [f"{c['name']} ({c['symbol'].upper()}): ${c['current_price']:.4f}" for c in data]
        barsik = get_token_price_coingecko("hasbulla-s-cat")
        if barsik:
            prices.append(f"Barsik (HASBULLA-S-CAT): ${barsik:.6f} 🚀")
        return prices
    except Exception as e:
        logging.error("Top 10 fetch error: %s", e)
        return None

# MAIN
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("barsikprice", barsik_price))
    app.add_handler(CommandHandler("cryptoprices", cryptoprices_command))
    app.add_handler(CommandHandler("img", img_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_response))

    app.run_polling()
