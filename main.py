import os
import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ===== ЛОГИ =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== FLASK =====
web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "✅ Бот Рус.язык 3 класс работает!"

# ===== TOKEN =====
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ===== ПРАВИЛА =====
RULES = {
    "предложение и словосочетание": {
        "title": "📖 Предложение и словосочетание",
        "rule": "Предложение выражает законченную мысль, словосочетание — нет.",
        "examples": ["Мама читает книгу. — предложение", "Читать книгу — словосочетание"]
    },
    "виды предложений": {
        "title": "📖 Виды предложений",
        "rule": "По цели высказывания бывают повествовательные, вопросительные и восклицательные.",
        "examples": ["Сегодня хорошая погода.", "Ты сделал уроки?", "Ура! Каникулы!"]
    },
    "главные и второстепенные члены предложения": {
        "title": "📖 Главные и второстепенные члены предложения",
        "rule": "Главные — подлежащее и сказуемое. Второстепенные — дополнение, определение, обстоятельство.",
        "examples": ["Кот спит. — подлежащее и сказуемое", "Кот спит на диване. — обстоятельство"]
    },
    "имя существительное": {
        "title": "📦 Имя существительное",
        "rule": "Отвечает на вопросы кто? что?",
        "examples": ["кто? — мама, ученик", "что? — книга, школа"]
    },
    "имя прилагательное": {
        "title": "🎨 Имя прилагательное",
        "rule": "Отвечает на вопросы какой? какая? какое? какие?",
        "examples": ["какой? — красный", "какая? — добрая", "какое? — синее"]
    },
    "местоимение": {
        "title": "🙋 Местоимение",
        "rule": "Указывает на предметы, но не называет их.",
        "examples": ["я, ты, он, она, мы, вы, они"]
    },
    "глагол": {
        "title": "⚡ Глагол",
        "rule": "Обозначает действие. Вопросы: что делать? что сделать?",
        "examples": ["читать, писать, играть"]
    },
    "времена глаголов": {
        "title": "⏳ Времена глаголов",
        "rule": "Прошедшее, настоящее, будущее.",
        "examples": ["читал, читаю, буду читать"]
    },
    "морфологический разбор глагола": {
        "title": "🛠 Морфологический разбор глагола",
        "rule": "Укажи начальную форму, время, число, лицо, род (если есть).",
        "examples": ["Читаю: глагол, инфинитив — читать, наст. время, 1 лицо, ед. число"]
    },
    "жи-ши": {
        "title": "✍ Жи-ши",
        "rule": "После Ж и Ш всегда пишется И.",
        "examples": ["жираф, шишка — верно", "жыраф — ошибка"]
    },
    "ча-ща": {
        "title": "✍ Ча-ща",
        "rule": "После Ч и Щ всегда пишется А.",
        "examples": ["чашка, щавель — верно", "чяшка — ошибка"]
    },
    "чу-щу": {
        "title": "✍ Чу-щу",
        "rule": "После Ч и Щ всегда пишется У.",
        "examples": ["чудо, щука — верно", "чюдо — ошибка"]
    }
}

# ===== КНОПКИ =====
def main_keyboard():
    keyboard = [
        ["📚 Синтаксис", "📦 Части речи"],
        ["✍ Орфография", "⚡ Глаголы"],
        ["📋 Все темы", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== КОМАНДЫ =====
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот по русскому языку для 3 класса.\n\n"
        "Выбирай раздел на клавиатуре или напиши название темы.\n"
        "Команды: /rules — список всех тем, /help — подсказка.",
        reply_markup=main_keyboard()
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Используй кнопки или напиши название темы.\n"
        "/rules — полный список тем."
    )

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 <b>Все доступные темы:</b>\n\n"
    for key, data in RULES.items():
        text += f"• {data['title']}\n"
    await update.message.reply_text(text, parse_mode="HTML")

# ===== ОБРАБОТКА СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower().strip()

    # Категории
    if query in ["📚 синтаксис", "синтаксис"]:
        await update.message.reply_text(
            "📚 Темы по синтаксису:\n"
            "• Предложение и словосочетание\n"
            "• Виды предложений\n"
            "• Главные и второстепенные члены предложения"
        )
        return
    elif query in ["📦 части речи", "части речи"]:
        await update.message.reply_text(
            "📦 Темы по частям речи:\n"
            "• Имя существительное\n"
            "• Имя прилагательное\n"
            "• Местоимение\n"
            "• Глагол"
        )
        return
    elif query in ["✍ орфография", "орфография"]:
        await update.message.reply_text(
            "✍ Темы по орфографии:\n"
            "• Жи-ши\n• Ча-ща\n• Чу-щу"
        )
        return
    elif query in ["⚡ глаголы", "глаголы"]:
        await update.message.reply_text(
            "⚡ Темы по глаголу:\n"
            "• Времена глаголов\n"
            "• Морфологический разбор глагола"
        )
        return

    # Поиск темы
    for key, data in RULES.items():
        if query in key or key in query:
            text = f"📖 <b>{data['title']}</b>\n\n"
            text += f"<b>Правило:</b> {data['rule']}\n\n"
            text += "<b>Примеры:</b>\n" + "\n".join(f"• {ex}" for ex in data["examples"])
            await update.message.reply_text(text, parse_mode="HTML")
            return

    await update.message.reply_text("❌ Тема не найдена. Используй /rules")

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
        logger.error("❌ BOT_TOKEN не найден!")
        return
    threading.Thread(target=run_flask, daemon=True).start()
    app = setup_app()
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

