import os
import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ===== ЛОГИ =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== FLASK ДЛЯ RENDER =====
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Бот Рус.язык 3 класс запущен!"

# ===== ПЕРЕМЕННАЯ С ТОКЕНОМ =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ===== ПРАВИЛА =====
RULES = {
    "предложение и словосочетание": {
        "title": "📝 Предложение и словосочетание",
        "rule": "Предложение выражает законченную мысль. Словосочетание — это два или более слов, связанных по смыслу.",
        "examples": ["Мама читает книгу. (предложение)", "читать книгу (словосочетание)"]
    },
    "виды предложений": {
        "title": "📚 Виды предложений по цели высказывания",
        "rule": "• Повествовательные — сообщают.\n• Вопросительные — задают вопрос.\n• Побудительные — выражают просьбу или приказ.",
        "examples": ["Я читаю книгу.", "Ты читаешь?", "Прочитай!"]
    },
    "главные и второстепенные члены предложения": {
        "title": "📖 Главные и второстепенные члены предложения",
        "rule": "Главные члены: подлежащее и сказуемое.\nВторостепенные: дополнение, определение, обстоятельство.",
        "examples": ["Кот (подлежащее) спит (сказуемое) на диване (обстоятельство)."]
    },
    "имя существительное": {
        "title": "📦 Имя существительное",
        "rule": "Обозначает предмет, отвечает на вопросы кто? что?",
        "examples": ["кто? — мама, ученик", "что? — книга, солнце"]
    },
    "имя прилагательное": {
        "title": "🎨 Имя прилагательное",
        "rule": "Обозначает признак предмета, отвечает на вопросы какой? какая? какое?",
        "examples": ["какой? красивый", "какая? добрая", "какое? большое"]
    },
    "местоимение": {
        "title": "👤 Местоимение",
        "rule": "Указывает на предмет, но не называет его.",
        "examples": ["я, ты, он, она, мы, вы, они"]
    },
    "глагол": {
        "title": "⚡ Глагол",
        "rule": "Обозначает действие. Отвечает на вопросы что делать? что сделать?",
        "examples": ["читать, писать, играть", "прочитать, написать, поиграть"]
    },
    "морфологический разбор глагола": {
        "title": "🔍 Морфологический разбор глагола",
        "rule": "1. Начальная форма (инфинитив).\n2. Время, лицо, число.\n3. Вид (сов./несов.).\n4. Возвратность.",
        "examples": ["Читать — инфинитив, несов. вид, 1 спряжение."]
    }
}

# ===== КЛАВИАТУРЫ =====
def main_keyboard():
    kb = [
        ["📚 Синтаксис", "📦 Части речи"],
        ["✍️ Орфография", "⚡ Глаголы"],
        ["📑 Все темы", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

# ===== КОМАНДЫ =====
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет! Я бот по русскому языку для 3 класса.\n\n"
        "Выбирай раздел на клавиатуре или напиши название темы.\n"
        "Команды: /rules — список всех тем, /help — подсказка."
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 Как пользоваться ботом:\n\n"
        "• Выбери тему на клавиатуре\n"
        "• Или напиши её название (например: 'глагол')\n"
        "• /rules — список всех тем"
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📑 <b>Все доступные темы:</b>\n\n"
    for key, data in RULES.items():
        text += f"• {data['title']}\n"
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=main_keyboard())

# ===== ОБРАБОТЧИК СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()
    for key, data in RULES.items():
        if query in key or query in data["title"].lower():
            response = f"<b>{data['title']}</b>\n\n"
            response += f"<b>Правило:</b> {data['rule']}\n\n"
            response += "<b>Примеры:</b>\n"
            for ex in data["examples"]:
                response += f"• {ex}\n"
            await update.message.reply_text(response, parse_mode="HTML", reply_markup=main_keyboard())
            return
    await update.message.reply_text("❌ Тема не найдена. Используй /rules", reply_markup=main_keyboard())

# ===== ЗАПУСК =====
def setup_app():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    app = setup_app()
    app.run_polling()

if __name__ == "__main__":
    main()

