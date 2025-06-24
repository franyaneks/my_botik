import random
import time
import asyncio
from flask import Flask, request
from threading import Thread

from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
URL = "https://sinklit-bot.onrender.com"  # Замени на свой Render URL

bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

flask_app = Flask(__name__)
user_timers = {}

loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "IMG_3704.jpeg",
        "description": "🌸 Утка Тадмавриэль\nРедкость: 🔵\nОсобенность: на её спине растёт цветок, который она очень любит."
    }
]

rarity_chances = {
    "🟢": 75,
    "🔵": 20,
    "🔴": 5
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
    filtered_items = [item for item in loot_items if item["rarity"] == rarity]
    return random.choice(filtered_items) if filtered_items else None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {name}!\n\nНапиши <b>кря</b>, чтобы я начал искать утку!\nРедкая утка — не проморгай! 🦆",
        parse_mode="HTML"
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]["end"]:
        duration = random.randint(600, 3600)
        user_timers[user_id] = {"end": now + duration}
        minutes = duration // 60
        await update.message.reply_text(
            f"🔍 Всё, ищу утку! Это займёт около <b>{minutes} минут</b>.\nНе волнуйся, скоро вернусь с новостями 🦆",
            parse_mode="HTML"
        )
    else:
        remaining = int(user_timers[user_id]["end"] - now)
        if remaining <= 0:
            loot = get_random_loot()
            if loot:
                with open(loot["photo_path"], 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption=loot["description"])
            else:
                await update.message.reply_text("Сегодня утка не пришла... попробуй позже 🥲")

            duration = random.randint(600, 3600)
            user_timers[user_id]["end"] = now + duration
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Всё ещё ищу утку!\n⏱ Осталось: <b>{minutes} мин {seconds} сек</b>\nПотерпи немного...",
                parse_mode="HTML"
            )

@flask_app.route("/")
def home():
    return "Бот запущен."

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    asyncio.run(application.process_update(update))
    return "ok"

def run():
    flask_app.run(host="0.0.0.0", port=8080)

def keep_alive():
    thread = Thread(target=run)
    thread.start()

def main():
    keep_alive()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^(?i)кря$"), handle_krya))
    bot.set_webhook(f"{URL}/{TOKEN}")
    print("✅ Бот работает и ждёт вебхуки...")
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()

