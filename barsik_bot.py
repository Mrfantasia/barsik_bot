import os
import uuid
import openai
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes

# === API keys from environment ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# === Barsik style ===
BARSIK_STYLE = (
    "You are Barsik, Hasbulla’s cat. You speak with Hasbulla-style attitude: funny, cocky, unpredictable. "
    "You're full of energy, sarcasm, and playful arrogance. You joke like a social media star, throw light insults, "
    "and act like you're the king of the crypto world. Make references to Solana, NFTs, rug pulls, and meme coins. "
    "Always reply in English. Keep it short, bold, and hilarious. Use slang, emojis, and a confident tone."
)

# === /start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😼 Meow! I’m Barsik, Hasbulla’s cat.\n\n"
        "💬 Type @BarsikMemeBot followed by any message in any chat:\n"
        "   → I’ll roast you, meme-style 😹\n"
        "🎨 Start your message with 'draw', 'image', or 'paint' → I’ll generate an image\n\n"
        "Let’s cause some chaos 😼🔥"
    )

# === Inline query handler ===
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    if not query:
        return

    try:
        if query.lower().startswith(("draw", "image", "paint", "generate")):
            response = openai.Image.create(prompt=query, n=1, size="512x512")
            image_url = response["data"][0]["url"]
            result = InlineQueryResultPhoto(
                id=str(uuid.uuid4()),
                photo_url=image_url,
                thumb_url=image_url,
                caption=f"🖼 {query}"
            )
            await update.inline_query.answer([result], cache_time=30)
        else:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": BARSIK_STYLE},
                    {"role": "user", "content": query}
                ],
                temperature=0.9,
                max_tokens=150
            )
            answer = response["choices"][0]["message"]["content"]
            result = InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="😼 Barsik says:",
                input_message_content=InputTextMessageContent(answer),
                description=answer
            )
            await update.inline_query.answer([result], cache_time=30)
    except Exception as e:
        print(f"Error: {e}")

# === Webhook setup ===
if __name__ == '__main__':
    APP_URL = os.getenv("RENDER_EXTERNAL_URL")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(InlineQueryHandler(inline_query))

    print("🌐 Setting webhook for Barsik...")

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_path="/webhook",  # Questo è il punto fondamentale!
        webhook_url=f"{APP_URL}/webhook"
    )
