import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from rules import RULES

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Flask для Render ---
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# --- Переменная окружения ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# --- Клавиатура ---
def main_keyboard():
    keyboard = [
        ["📚 Синтаксис", "📦 Части речи"],
        ["✍️ Орфография", "⚡ Глаголы"],
        ["📑 Все темы", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Команды ---
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот по русскому языку для 3 класса.\n\n"
        "Выбирай раздел на клавиатуре или напиши название темы.\n"
        "Команды:\n"
        "/rules — список всех тем\n"
        "/help — подсказка.",
        reply_markup=main_keyboard()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ Используй кнопки или напиши название темы.\n"
        "/rules — полный список тем."
    )

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📑 <b>Все доступные темы:</b>\n\n"
    for key, data in RULES.items():
        text += f"- {data['title']}\n"
    await update.message.reply_text(text, parse_mode="HTML")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()

    for key, data in RULES.items():
        if query in key or query in data["title"].lower():
            text = f"<b>{data['title']}</b>\n\n"
            text += f"<b>Правило:</b> {data['rule']}\n\n"
            text += "<b>Примеры:</b>\n" + "\n".join(data["examples"])
            await update.message.reply_text(text, parse_mode="HTML")
            return

    await update.message.reply_text("❌ Тема не найдена. Используй /rules")

# --- Основной запуск ---
def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден!")
        return

    tg_app = Application.builder().token(BOT_TOKEN).build()

    tg_app.add_handler(CommandHandler("start", cmd_start))
    tg_app.add_handler(CommandHandler("help", cmd_help))
    tg_app.add_handler(CommandHandler("rules", cmd_rules))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен...")

    # Запускаем Flask в отдельном потоке
    Thread(target=run_flask, daemon=True).start()

    tg_app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
