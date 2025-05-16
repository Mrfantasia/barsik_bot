import os
import asyncio
import openai
from openai import OpenAI
import requests
from flask import Flask
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
import threading

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COINMARKET_API_KEY = os.getenv("COINMARKET_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

BARSIK_STYLE = (
    "You are Barsik, Hasbulla’s cat. You respond like a witty, funny chatbot with slang and emojis. "
    "Keep replies fresh and never repeat exactly the same."
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Barsik Meme Bot is alive!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😼 Yo! I'm Barsik – your crypto meme cat. Ask me anything!")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Pong!")

async def generate_image(prompt: str) -> str:
    try:
        response = client.images.generate(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        return response.data[0].url
    except Exception as e:
        print("Image generation error:", e)
        return None

async def img_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_prompt = ' '.join(context.args)
    if not user_prompt:
        await update.message.reply_text("Please provide a prompt for the image. Usage: /img <prompt>")
        return

    await update.message.reply_text("🎨 Generating your image, wait a moment...")

    image_url = await generate_image(user_prompt)
    if image_url:
        await update.message.reply_photo(photo=image_url)
    else:
        await update.message.reply_text("Sorry, I couldn't create the image.")

async def chat_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": BARSIK_STYLE},
                {"role": "user", "content": user_message},
            ],
            max_tokens=200,
            temperature=0.9,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.6,
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Barsik is having a bad meme day.")
        print("OpenAI Error:", e)

def get_token_price(contract_address: str):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    headers = {
        "X-CMC_PRO_API_KEY": COINMARKET_API_KEY,
        "Accepts": "application/json",
    }
    params = {
        "contract_address": contract_address,
        "convert": "USD"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        try:
            price = data["data"][contract_address]["quote"]["USD"]["price"]
            return price
        except KeyError:
            return None
    else:
        return None

async def barsik_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contract = "7ZqzGzTNg5tjK1CHTBdGFHyKjBtXdfvAobuGgdt4pump"  # Barsik token contract address
    price = get_token_price(contract)
    if price:
        await update.message.reply_text(f"🐾 The current Barsik token price is ${price:.6f} USD")
    else:
        await update.message.reply_text("⚠️ Sorry, I couldn't fetch Barsik token price right now.")

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("img", img_command))
    application.add_handler(CommandHandler("barsikprice", barsik_price))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_response))

    print("🐾 Barsik Meme Bot is running via polling...")

    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())

    threading.Thread(target=run_flask).start()

    loop.run_forever()

if __name__ == "__main__":
    main()

