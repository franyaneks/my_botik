import random
import time
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from flask import Flask
from threading import Thread

TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"

app = Flask(__name__)
user_timers = {}

# Список уток
loot_items = [{
    "rarity": "🔵",
    "photo_path": "IMG_3704.jpeg",
    "description": "Утка Тадмавриэль\nРедкость: 🔵\n1/10"
}]
rarity_chances = {"🟢": 60, "🔵": 25, "🔴": 15}

def get_random_loot():
    roll = random.randint(1,100)
    cum = 0
    for r, c in rarity_chances.items():
        cum += c
        if roll <= cum:
            return next((i for i in loot_items if i["rarity"] == r), None)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Напиши 'кря' чтобы найти утку.")

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    now = time.time()
    if uid not in user_timers or now >= user_timers[uid]:
        dur = random.randint(600,3600)
        user_timers[uid] = now + dur
        m = dur // 60
        await update.message.reply_text(f"🔍 Ищу утку, займет ~{m} мин.")
    else:
        rem = int(user_timers[uid] - now)
        if rem <= 0:
            loot = get_random_loot()
            if loot:
                with open(loot["photo_path"], "rb") as ph:
                    await update.message.reply_photo(photo=ph, caption=loot["description"])
            else:
                await update.message.reply_text("Утка не найдена.")
            user_timers[uid] = now + random.randint(600,3600)
        else:
            m, s = divmod(rem, 60)
            await update.message.reply_text(f"🌐 Ищу... Осталось {m} мин {s} сек")

def run_web():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    Thread(target=run_web).start()

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("(?i)^кря$"), handle_krya))

    application.run_polling()
