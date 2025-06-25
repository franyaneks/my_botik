import os, random, time, asyncio
from threading import Thread
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
URL = os.environ.get("WEBHOOK_URL", "https://sinklit-bot.onrender.com")

app = Flask(__name__)

bot = Bot(token=TOKEN)
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

rarity_chances = {"🟢": 60, "🔵": 25, "🔴": 15}

def get_random_rarity():
    roll = random.randint(1,100)
    cum = 0
    for r, ch in rarity_chances.items():
        cum += ch
        if roll <= cum:
            return r
    return "🟢"

def get_random_loot():
    rarity = get_random_rarity()
    filtered = [i for i in loot_items if i["rarity"] == rarity]
    return random.choice(filtered) if filtered else None

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\n\n"
        "Напиши 🦆 <b>кря</b>, чтобы я начал искать утку!",
        parse_mode="HTML"
    )

async def handle_krya(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]['end']:
        duration = random.randint(600,3600)
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
                    await update.message.reply_photo(photo=photo, caption=loot["description"])
            else:
                await update.message.reply_text("Сегодня утка не нашлась, попробуй позже. 🦆")
            duration = random.randint(600,3600)
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

@app.route('/', methods=['GET'])
def home():
    return "Бот работает 24/7!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

def run():
    port = int(os.environ.get("PORT", "8080"))
    app.run(host='0.0.0.0', port=port)

def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex(r"(?i)^кря$"), handle_krya))

    # запускаем Flask
    Thread(target=run).start()

    # устанавливаем webhook и инициализируем приложение
    asyncio.run(bot.set_webhook(f"{URL}/{TOKEN}"))
    asyncio.run(application.initialize())

    print("✅ Webhook установлен")
    print("✅ Бот запущен! Ждём обновлений...")

    # блокировка main
    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()

