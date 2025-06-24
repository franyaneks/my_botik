from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import random
import time

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"

app = Flask(__name__)
duck_timer = {}  # Словарь: user_id -> (время_конца, сообщение)

# Запускаем Flask-сервер для Render
@app.route('/')
def index():
    return "Бот работает!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Команда "кря"
async def krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in duck_timer or now >= duck_timer[user_id][0]:
        # Новый таймер
        seconds = random.randint(600, 3600)  # от 10 мин до 1 часа
        end_time = now + seconds
        duck_timer[user_id] = (end_time, None)
        await update.message.reply_text(f"🦆 Начал искать утку. Вернись через {seconds // 60} минут.")
    else:
        end_time, _ = duck_timer[user_id]
        time_left = int(end_time - now)
        if time_left > 0:
            await update.message.reply_text(f"⏳ Осталось {time_left // 60} мин. и {time_left % 60} сек.")
        else:
            # Таймер завершён, утка найдена
            duck = random.choice([
                "🦆 Обычная утка",
                "✨ Золотая утка",
                "🌈 Радужная утка",
                "🔥 Огненная утка"
            ])
            duck_timer[user_id] = (0, None)
            await update.message.reply_text(f"🎉 Ты нашёл утку: {duck}\nНапиши 'кря', чтобы искать заново.")

# Запуск Telegram-бота
async def start_bot():
    print("🔁 Запускаю бота...")
    app_telegram = Application.builder().token(TOKEN).build()
    app_telegram.add_handler(CommandHandler("start", krya))
    app_telegram.add_handler(CommandHandler("кря", krya))
    await app_telegram.initialize()
    await app_telegram.start()
    print("✅ Бот запущен!")
    await app_telegram.updater.start_polling()
    await app_telegram.updater.idle()

# Главный запуск
if __name__ == "__main__":
    # Запуск Flask в отдельном потоке
    Thread(target=run_flask).start()

    # Запуск Telegram бота
    asyncio.run(start_bot())





