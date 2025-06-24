import random
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

user_timers = {}

loot_items = [
    {
        "name": "Утка Тадмавриэль",
        "rarity": "🔵",
        "description": "Утка Тадмавриэль\nРедкость: 🔵\n1/10"
    }
]

def get_random_loot():
    return random.choice(loot_items)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.first_name
    await update.message.reply_text(
        f"👋 Привет, {username}!\nНапиши 'кря', чтобы я начал искать утку!"
    )

async def handle_krya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    now = time.time()

    if user_id not in user_timers or now >= user_timers[user_id]:
        duration = random.randint(600, 3600)  # от 10 минут до 1 часа
        user_timers[user_id] = now + duration
        minutes = duration // 60
        await update.message.reply_text(
            f"🔍 Начинаю искать утку! Это займёт примерно {minutes} минут(ы).\n"
            "Потерпи немного, скоро вернусь с уткой! 🦆"
        )
    else:
        remaining = int(user_timers[user_id] - now)
        if remaining > 0:
            minutes = remaining // 60
            seconds = remaining % 60
            await update.message.reply_text(
                f"🙈 Я всё ещё ищу утку!\nОсталось: {minutes} мин {seconds} сек.\nПотерпи немного... 🦆🔍"
            )
        else:
            loot = get_random_loot()
            await update.message.reply_text(f"Утка найдена!\n{loot['description']}")
            user_timers[user_id] = 0  # сбросить таймер

if __name__ == '__main__':
    TOKEN = "7907591643:AAHzqBkgdUiCDaKRBO4_xGRzYhF56325Gi4"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("(?i)^кря$"), handle_krya))

    print("✅ Бот запущен!")
    app.run_polling()




