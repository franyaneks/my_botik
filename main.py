import random
import time
from flask import Flask
from threading import Thread

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Бот работает 24/7!"

def run():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

user_timers = {}

loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "photo_2025-06-09_15-48-23.jpg",  # <-- путь к картинке в репозитории
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
    filtered_items = [item for item in loot_items if item["rarity"] == rarity]
    if filtered_items:
        return random.choice(filtered_items)
    else:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        "Напиши 🦆 <b>кря</b>, чтобы я начал искать утку!",
        parse_mode="HTML"
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]['end']:
        duration = random.randint(600, 3600)
        user_timers[user_id] = {'end': now + duration}

        minutes = duration // 60
        await update.message.reply_text(
            f"🔍 Начинаю искать утку!\n"
            f"⏳ Это займёт примерно <b>{minutes} минут(ы)</b>.\n"
            "Потерпи немного, скоро вернусь с уткой! 🦆",
            parse_mode="HTML"
        )
    else:
        remaining = int(user_timers[user_id]['end'] - now)
        if remaining <= 0:
            loot = get_random_loot()
            if loot:
                with open(loot["photo_path"], 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=loot["description"]
                    )
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже. 🦆")

            # Обновляем таймер для следующего поиска
            duration = random.randint(600, 3600)
            user_timers[user_id]['end'] = now + duration
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Я всё ещё ищу утку!\n"
                f"⏱ Осталось: <b>{minutes} мин {seconds} сек</b>\n"
                "Потерпи немного... 🦆🔍",
                parse_mode="HTML"
            )

if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("(?i)^кря$"), handle_krya))

    print("✅ Бот запущен!")
    app.run_polling()




