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
URL = "https://sinklit-bot.onrender.com"  # Твой URL на Render

# Flask приложение
flask_app = Flask(__name__)

# Таймеры для пользователей
user_timers = {}

# Список уток (лоота)
loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "IMG_3704.jpeg",  # Файл должен лежать в папке с main.py
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
        f"👋 Привет, {username}!\n\nНапиши 🦆 <b>кря</b>, чтобы я начал искать утку!",
        parse_mode="HTML"
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]['end']:
        duration = random.randint(600, 3600)  # 10-60 минут
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
                try:
                    with open(loot["photo_path"], 'rb') as photo:
                        await update.message.reply_photo(photo=photo, caption=loot["description"])
                except Exception as e:
                    # Если фото не найдено, просто отправим текст
                    await update.message.reply_text(
                        f"{loot['name']}\nРедкость: {loot['rarity']}\n(Фото не найдено)"
                    )
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже. 🦆")

            # Новый таймер для следующего поиска
            duration = random.randint(600, 3600)
            user_timers[user_id]['end'] = now + duration
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Я всё ещё ищу утку!\n⏱ Осталось: <b>{minutes} мин {seconds} сек</b>\nПотерпи немного... 🦆🔍",
                parse_mode="HTML"
            )

@flask_app.route('/')
def home():
    return "Бот работает 24/7!"

@flask_app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    # process_update — асинхронная, запускаем через loop
    asyncio.get_event_loop().run_until_complete(application.process_update(update))
    return 'ok'

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.daemon = True
    thread.start()

async def set_webhook():
    # Установка вебхука
    success = await bot.set_webhook(f"{URL}/{TOKEN}")
    if success:
        print(f"Webhook установлен на {URL}/{TOKEN}")
    else:
        print("Ошибка при установке webhook")

if __name__ == '__main__':
    # Инициализация бота и добавление хендлеров
    application = ApplicationBuilder().token(TOKEN).build()
    bot = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^(?i)кря$"), handle_krya))

    keep_alive()  # Запускаем Flask в отдельном потоке

    # Устанавливаем webhook (асинхронно)
    asyncio.run(set_webhook())

    print("Бот запущен и webhook установлен!")

    # Чтобы скрипт не завершался — цикл ожидания
    import time
    while True:
        time.sleep(10)




