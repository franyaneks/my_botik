import os
import random
import time
import asyncio
from threading import Thread

from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Новый токен:
TOKEN = "7907591643:AAGImUGU5nO9kTfS49a-lE1fdrBq34-t1ho"
URL = "https://sinklit-bot.onrender.com"  # Заменить, если у тебя другой адрес Render

app = Flask(__name__)

bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

user_timers = {}

loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "description": "🦆 Утка Тадмавриэль\nРедкость: 🔵\n1/10\n\n<code>photo_2025-06-09_15-48-23.jpg</code>"
    }
]

rarity_chances = {"🟢": 60, "🔵": 25, "🔴": 15}

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\nНапиши 🦆 <b>кря</b>, чтобы я начал искать утку!",
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
            f"🔍 Начинаю искать утку!\n⏳ Это займёт примерно <b>{minutes} минут(ы)</b>.\nПотерпи немного, скоро вернусь с уткой! 🦆",
            parse_mode="HTML"
        )
    else:
        remaining = int(user_timers[user_id]['end'] - now)
        if remaining <= 0:
            loot = get_random_loot()
            if loot:
                await update.message.reply_photo(
                    photo="https://raw.githubusercontent.com/franyaneks/my_botik/main/photo_2025-06-09_15-48-23.jpg",
                    caption=loot["description"],
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже. 🦆")
            duration = random.randint(600, 3600)
            user_timers[user_id]['end'] = now + duration
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Я всё ещё ищу утку!\n⏱ Осталось: <b>{minutes} мин {seconds} сек</b>\nПотерпи немного... 🦆🔍",
                parse_mode="HTML"
            )

@app.route('/')
def home():
    return "Бот работает 24/7!"

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    await application.process_update(update)
    return "ok"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

async def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^кря$"), handle_krya))

    await application.initialize()
    await application.bot.set_webhook(f"{URL}/{TOKEN}")

    thread = Thread(target=run_flask)
    thread.start()

    print("✅ Webhook установлен")
    print("✅ Бот запущен! Ждём обновлений...")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())


