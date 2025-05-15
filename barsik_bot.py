import os
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineQueryResultPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, InlineQueryHandler, ContextTypes
import openai
import uuid
import traceback

# Leggi API keys dalle variabili ambiente (Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Stile di Barsik
BARSIK_STYLE = (
    "You are Barsik, Hasbulla’s cat. You speak with Hasbulla-style attitude: funny, cocky, unpredictable. "
    "You're full of energy, sarcasm, and playful arrogance. You joke like a social media star, throw light insults, "
    "and act like you're the king of the crypto world. Make references to Solana, NFTs, rug pulls, and meme coins. "
    "Always reply in English. Keep it short, bold, and hilarious. Use slang, emojis, and a confident tone."
)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "😼 Meow! I’m Barsik, Hasbulla’s cat. Type @BarsikBot followed by a message in any chat:\n\n"
        "💬 Normal prompt → Barsik replies in chat\n"
        "🎨 Prompt starting with 'draw', 'image', or 'paint' → Barsik creates an image"
    )

# Modalità inline (text o image)
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
                model="gpt-4-turbo",
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
        traceback.print_exc()

# Lancio bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(InlineQueryHandler(inline_query))
    print("🐾 Barsik inline hybrid is live!")
    app.run_polling()
