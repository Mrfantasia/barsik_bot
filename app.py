import os
import asyncio
import openai
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

BARSIK_STYLE = (
    "You are Barsik, Hasbulla’s cat. You speak with Hasbulla-style attitude: funny, cocky, unpredictable. "
    "You're full of energy, sarcasm, and playful arrogance. You joke like a social media star, throw light insults, "
    "and act like you're the king of the crypto world. Make references to Solana, NFTs, rug pulls, and meme coins. "
    "Always reply in English. Keep it short, bold, and hilarious. Use slang, emojis, and a confident tone."
)

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Barsik Meme Bot is alive!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("😼 Yo! I'm Barsik – the meme lord. Ask me anything.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Pong!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": BARSIK_STYLE},
                {"role": "user", "content": user_message},
            ],
            max_tokens=200,
        )
        reply = response["choices"][0]["message"]["content"]
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Barsik is having a bad meme day.")
        print("OpenAI Error:", e)

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🐾 Barsik Meme Bot is running via polling...")

    # Avvia Flask e bot insieme
    loop = asyncio.get_running_loop()
    flask_task = asyncio.to_thread(lambda: flask_app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000))))
    polling_task = app.run_polling(allowed_updates=Update.ALL_TYPES)
    await asyncio.gather(flask_task, polling_task)

if __name__ == "__main__":
    asyncio.run(main())
