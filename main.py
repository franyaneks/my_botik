import random
import time
import datetime
from threading import Thread
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
URL = "https://sinklit-bot.onrender.com"  # Твой URL на Render

bot = Bot(TOKEN)
app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

user_timers = {}

loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "IMG_3704.jpeg",  # файл рядом с main.py
        "description": "Утка Тадмавриэль\nРедкость: 🔵\n1/10"
    }
]

rarity_chances = {
    "🟢": 60,
    "🔵": 25,
    "🔴": 15
}

def get_random_rarity():
    roll = random.randint(1, 100)
    cumulative = 0
    for rarity, chance in rarity_chances.items():
        cumulative += chance
        if roll <= cumulative:
            return rarity
    return "🟢"

def get_random_loot():
    rarity = get_random_rarity()
    filtered = [item for item in loot_items if item["rarity"] == rarity]
    return random.choice(filtered) if filtered else None

@app.route("/")
def home():
    return "Бот работает!"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"Привет, {username}! Напиши 'кря', чтобы начать искать утку."
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]['end']:
        duration = random.randint(600, 3600)
        user_timers[user_id] = {'end': now + duration}
        minutes = duration // 60
        await update.message.reply_text(
            f"Начинаю искать утку! Это займет примерно {minutes} мин."
        )
    else:
        remaining = int(user_timers[user_id]['end'] - now)
        if remaining <= 0:
            loot = get_random_loot()
            if loot:
                with open(loot["photo_path"], 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption=loot["description"])
            else:
                await update.message.reply_text("Утка не найдена, попробуй позже.")
            # Запускаем новый таймер после выдачи утки
            duration = random.randint(600, 3600)
            user_timers[user_id]['end'] = now + duration
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"Утка еще не найдена. Осталось: {minutes} мин {seconds} сек."
            )

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()

def main():
    keep_alive()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^кря$"), handle_krya))
    print("Бот запущен, ждем вебхук...")
    application.run_webhook(
        listen="0.0.0.0",
        port=8080,
        webhook_url=f"{URL}/{TOKEN}"
    )

if __name__ == "__main__":
    main()
