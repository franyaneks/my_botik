import os
import random
import asyncio
from flask import Flask, request
from telegram import Update, Bot, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
WEBHOOK_URL = f"https://sinklit-bot.onrender.com/{TOKEN}"

app = Flask(__name__)

bot = Bot(token=TOKEN)
application = ApplicationBuilder().token(TOKEN).build()

user_timers = {}

rarity_chances = {"🟢": 60, "🔵": 25, "🔴": 15}

loot_items = [
    {"name": "Утка Тадмавриэль", "rarity": "🔵", "description": "Утка Тадмавриэль\nРедкость: 🔵\n1/10", "photo": "photo_2025-06-09_15-48-23.jpg"},
    # Можно добавить ещё предметы с фото
]

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
        f"Привет, {username}! Напиши 'кря', чтобы начать искать утку."
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    import time
    now = time.time()
    if user_id not in user_timers or now >= user_timers[user_id]:
        # Новый таймер
        delay = random.randint(600, 3600)  # 10мин-1час
        user_timers[user_id] = now + delay
        minutes = delay // 60
        await update.message.reply_text(
            f"Начинаю искать утку! Подожди примерно {minutes} минут."
        )
    else:
        remaining = int(user_timers[user_id] - now)
        if remaining <= 0:
            loot = get_random_loot()
            if loot:
                photo_path = os.path.join(os.getcwd(), loot["photo"])
                if os.path.exists(photo_path):
                    with open(photo_path, "rb") as photo_file:
                        await update.message.reply_photo(photo=InputFile(photo_file), caption=loot["description"])
                else:
                    await update.message.reply_text(loot["description"] + "\n(Картинка не найдена)")
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже.")
            # Перезапускаем таймер
            delay = random.randint(600, 3600)
            user_timers[user_id] = now + delay
        else:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"Я ещё ищу утку! Осталось: {minutes} мин {seconds} сек."
            )

@app.route('/')
def index():
    return "Бот работает!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.create_task(application.process_update(update))
    return "ok"

def setup_handlers():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"(?i)^кря$"), handle_krya))

async def set_webhook():
    await application.initialize()
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен на {WEBHOOK_URL}")

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    setup_handlers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())

    run_flask()

