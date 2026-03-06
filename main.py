import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# TOKENS (Keep these safe!)
TELEGRAM_TOKEN = "8615152845:AAFpHH6XDne2aMoYtqunB25r4TtxDLxZD2c"
GROQ_API_KEY = "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"

# Groq API request
def ask_groq(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ AI error: {response.status_code}"
    except Exception as e:
        return f"⚠️ Connection error: {e}"

# Handle messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text:
        user_message = update.message.text
        await update.message.chat.send_action("typing")
        ai_reply = ask_groq(user_message)
        await update.message.reply_text(ai_reply)

# Start bot
if __name__ == "__main__":
    print("Bot is starting...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Bot is running...")
    app.run_polling()
