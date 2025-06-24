import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
import asyncio

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
WEBHOOK_URL = f"https://YOUR-RENDER-URL.onrender.com/{TOKEN}"

app = Flask(__name__)

# Создание Telegram приложения
application = ApplicationBuilder().token(TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Бот работает.")

# Добавление хендлера
application.add_handler(CommandHandler("start", start))

# Установка webhook
@app.before_first_request
def init_webhook():
    asyncio.get_event_loop().create_task(
        application.bot.set_webhook(WEBHOOK_URL)
    )

# Обработка запроса от Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

