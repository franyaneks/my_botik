import random
import time
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application, MessageHandler, ContextTypes, filters
)

# === НАСТРОЙКИ ===
TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
WEBHOOK_URL = f"https://sinklit-bot.onrender.com/{TOKEN}"

# === Flask-приложение ===
app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()
bot = Bot(token=TOKEN)

# === Обработка сообщения "кря" ===
last_duck_time = 0
duck_interval = 0

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_duck_time, duck_interval
    now = time.time()

    if now - last_duck_time > duck_interval:
        duck_interval = random.randint(600, 3600)
        last_duck_time = now
        await update.message.reply_text(
            f"🦆 Появилась редкая утка! Следующая через {duck_interval // 60} мин."
        )
    else:
        remaining = int(duck_interval - (now - last_duck_time))
        await update.message.reply_text(
            f"⏳ До следующей редкой утки: {remaining // 60} мин {remaining % 60} сек."
        )

# === Обработчик текста "кря" ===
application.add_handler(
    MessageHandler(filters.TEXT & filters.Regex(r"(?i)^кря$"), handle_krya)
)

# === Обработка webhook от Telegram ===
@app.post(f"/{TOKEN}")
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.create_task(application.process_update(update))
    return "ok", 200

# === Точка входа ===
if __name__ == "__main__":
    async def run():
        await application.initialize()
        await application.start()
        await bot.set_webhook(WEBHOOK_URL)
        print("✅ Webhook установлен:", WEBHOOK_URL)

    asyncio.run(run())
    app.run(host="0.0.0.0", port=8080)




