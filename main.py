import os
import random
import time
import asyncio
from threading import Thread

from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"  # замени на свой токен
URL = "https://sinklit-bot.onrender.com"  # замени на свой публичный URL Render

app = Flask(__name__)

bot = Bot(token=TOKEN)

# Создаем отдельный event loop для asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Создаем Application (python-telegram-bot)
application = ApplicationBuilder().token(TOKEN).build()

# Хранилище для таймеров пользователей — когда кончится ожидание
user_timers = {}

# Лут — редкие утки с описанием и фотографиями
loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "photo_path": "IMG_3704.jpeg",  # картинка должна лежать рядом с main.py
        "description": "🦆 Утка Тадмавриэль\nРедкость: 🔵\nВероятность: 1/10",
    },
    # Можно добавить больше уток, например:
    # {
    #     "name": "Утка Грозовая",
    #     "rarity": "🔴",
    #     "photo_path": "storm_duck.jpg",
    #     "description": "⚡ Утка Грозовая\nРедкость: 🔴\nОчень редкая утка!",
    # },
]

# Вероятности по редкости (в процентах)
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
    if filtered:
        return random.choice(filtered)
    # Если нет по выбранной редкости — можно вернуть что-то по умолчанию
    return None


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\nНапиши 🦆 <b>кря</b>, чтобы я начал искать утку!",
        parse_mode="HTML",
    )


# Обработчик сообщения "кря"
async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    # Если таймер либо отсутствует, либо время ожидания прошло — начинаем новый поиск
    if user_id not in user_timers or now >= user_timers[user_id]:
        duration = random.randint(600, 3600)  # от 10 минут до 1 часа (сек)
        user_timers[user_id] = now + duration
        minutes = duration // 60
        await update.message.reply_text(
            f"🔍 Начинаю искать утку!\n⏳ Это займёт примерно <b>{minutes} минут(ы)</b>.\nПотерпи немного, скоро вернусь с уткой! 🦆",
            parse_mode="HTML",
        )
    else:
        # Таймер ещё не истёк — считаем оставшееся время
        remaining = int(user_timers[user_id] - now)
        if remaining <= 0:
            # Время вышло — выдаём утку (если есть)
            loot = get_random_loot()
            if loot:
                try:
                    with open(loot["photo_path"], "rb") as photo:
                        await update.message.reply_photo(photo=photo, caption=loot["description"])
                except FileNotFoundError:
                    await update.message.reply_text(
                        f"🐥 Вот твоя утка!\n{loot['description']}\n(Картинка не найдена)"
                    )
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже. 🦆")

            # Запускаем новый таймер
            duration = random.randint(600, 3600)
            user_timers[user_id] = now + duration
        else:
            # Сообщаем сколько осталось ждать
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Я всё ещё ищу утку!\n⏱ Осталось: <b>{minutes} мин {seconds} сек</b>\nПотерпи немного... 🦆🔍",
                parse_mode="HTML",
            )


# Flask роуты
@app.route("/")
def home():
    return "Бот работает 24/7!"


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True)
    update = Update.de_json(json_update, bot)
    # Обработка update в asyncio loop
    asyncio.run_coroutine_threadsafe(application.process_update(update), loop)
    return "ok"


def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    thread = Thread(target=run)
    thread.start()


async def main_async():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^кря$"), handle_krya))
    await application.initialize()
    await bot.set_webhook(f"{URL}/{TOKEN}")
    print("✅ Webhook установлен")
    print("✅ Бот запущен! Ждём обновлений...")


if __name__ == "__main__":
    keep_alive()
    loop.run_until_complete(main_async())

    # Основной поток просто ждет, Flask уже работает в фоне
    import time

    while True:
        time.sleep(10)



