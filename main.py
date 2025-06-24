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

# === Настройки ===
TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
URL = "https://sinklit-bot.onrender.com"  # Укажи свой публичный URL Render или где хостишь

app = Flask(__name__)
bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

# Хранилище для таймеров пользователей
user_timers = {}

# Список лута (пример)
loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "IMG_3704.jpeg",
        "description": "Утка Тадмавриэль\nРедкость: 🔵\n1/10"
    },
    # Можно добавить другие утки с разной редкостью и фото
]

# Вероятности выпадения по редкости
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
    if not filtered:
        return None
    return random.choice(filtered)

# === Обработчики Telegram ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\nНапиши 'кря', чтобы начать искать утку!"
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    # Если пользователь не в таймерах или таймер истёк — запускаем новый
    if user_id not in user_timers or now >= user_timers[user_id]['end']:
        duration = random.randint(600, 3600)  # от 10 минут до 1 часа
        user_timers[user_id] = {'end': now + duration}
        minutes = duration // 60
        await update.message.reply_text(
            f"🔍 Начинаю искать утку!\n⏳ Это займет примерно {minutes} минут(ы). Потерпи немного..."
        )
        return

    # Если таймер активен — показываем сколько осталось
    remaining = int(user_timers[user_id]['end'] - now)
    if remaining <= 0:
        # Таймер закончился — выдаём утку
        loot = get_random_loot()
        if loot:
            try:
                with open(loot["photo_path"], 'rb') as photo:
                    await update.message.reply_photo(photo=photo, caption=loot["description"])
            except Exception:
                # Если фото не загрузилось — просто текстом
                await update.message.reply_text(f"Вот твоя утка:\n{loot['description']}")
        else:
            await update.message.reply_text("Сегодня утка не нашлась, попробуй позже.")

        # Запускаем новый таймер после выдачи
        duration = random.randint(600, 3600)
        user_timers[user_id]['end'] = now + duration
    else:
        minutes = remaining // 60
        seconds = remaining % 60
        await update.message.reply_text(
            f"🙈 Я всё ещё ищу утку!\n⏳ Осталось примерно {minutes} мин {seconds} сек."
        )

# === Flask сервер ===

@app.route('/')
def home():
    return "Бот работает 24/7!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)

    loop = asyncio.get_event_loop()
    future = asyncio.run_coroutine_threadsafe(application.process_update(update), loop)
    try:
        future.result(timeout=10)
    except Exception as e:
        print(f"Ошибка в webhook: {e}")

    return "ok"

# === Запуск Flask в отдельном потоке ===

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.start()

# === Главная функция запуска ===

def main():
    keep_alive()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^кря$"), handle_krya))

    loop = asyncio.get_event_loop()

    # Инициализация и запуск бота + установка webhook
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    loop.run_until_complete(bot.set_webhook(f"{URL}/{TOKEN}"))

    print("✅ Бот запущен и webhook установлен!")

    # Flask уже запущен в отдельном потоке, просто держим main активным
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Бот остановлен пользователем")

if __name__ == "__main__":
    main()


