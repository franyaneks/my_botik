import random
import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
bot = Bot(TOKEN)
app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

next_duck_time = {}

def generate_duck_rarity():
    roll = random.randint(1, 100)
    if roll <= 50:
        return "обычная"
    elif roll <= 80:
        return "редкая"
    elif roll <= 95:
        return "эпическая"
    elif roll <= 99:
        return "легендарная"
    else:
        return "мифическая"

@app.route("/")
def home():
    return "Bot is running!"

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "ok"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напиши 'кря', чтобы начать искать утку.")

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = datetime.datetime.now()

    if user_id not in next_duck_time or now >= next_duck_time[user_id]:
        minutes = random.randint(10, 60)
        next_time = now + datetime.timedelta(minutes=minutes)
        next_duck_time[user_id] = next_time
        await update.message.reply_text(f"🦆 Ищу утку... Возвращайся через {minutes} минут!")
    else:
        remaining = next_duck_time[user_id] - now
        if remaining.total_seconds() <= 0:
            rarity = generate_duck_rarity()
            await update.message.reply_text(f"🎉 Поздравляю! Ты нашёл {rarity} утку!")
            del next_duck_time[user_id]
        else:
            minutes_left = int(remaining.total_seconds() // 60)
            seconds_left = int(remaining.total_seconds() % 60)
            await update.message.reply_text(
                f"⏳ До следующей утки осталось {minutes_left} мин {seconds_left} сек."
            )

def main():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^(?i)кря$"), handle_krya))

    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
