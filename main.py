import random
import time
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Глобальная переменная для хранения времени последнего "кря"
last_duck_time = 0
next_duck_cooldown = 0

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put(update)
    return 'OK'

@app.route('/')
def home():
    return 'бот жив'

# Обработка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши 'кря', чтобы позвать утку!")

# Обработка команды кря
async def kray(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_duck_time, next_duck_cooldown

    now = time.time()
    remaining = int((last_duck_time + next_duck_cooldown) - now)

    if remaining > 0:
        mins = remaining // 60
        secs = remaining % 60
        await update.message.reply_text(f"Ранняя утка уже прилетала! Следующая будет через {mins} мин {secs} сек.")
        return

    # Случайное время до следующей утки
    next_duck_cooldown = random.randint(600, 3600)
    last_duck_time = now

    rarity = random.choices(
        ['обычная', 'редкая', 'эпическая', 'легендарная'],
        weights=[80, 15, 4, 1],
        k=1
    )[0]

    await update.message.reply_text(f"Утка прилетела! Ее редкость: {rarity.upper()}")

# Обработка всех сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "кря":
        await kray(update, context)
    else:
        await update.message.reply_text("Напиши 'кря' чтобы позвать утку!")

# Хендлеры
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Запуск Flask-сервера и Telegram polling в одном потоке
def run():
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=10000)

    threading.Thread(target=run_flask).start()
    application.run_polling()

if __name__ == '__main__':
    run()

