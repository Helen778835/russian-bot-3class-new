import os
import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ===== НАСТРОЙКА ЛОГИРОВАНИЯ =====
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== FLASK СЕРВЕР ДЛЯ RENDER =====
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "✅ Бот-помощник по русскому языку 3 класс активен!"

# ===== КОНФИГУРАЦИЯ БОТА =====
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# ===== БАЗА ДАННЫХ ПРАВИЛ =====
RUSSIAN_RULES = {
    "предложение и словосочетание": {
        "title": "📝 Предложение и словосочетание",
        "rule": "Предложение выражает законченную мысль, словосочетание — только связь слов.",
        "examples": [
            "Мама читает книгу (предложение).",
            "Читать книгу (словосочетание)."
        ]
    },
    "виды предложений по цели высказывания": {
        "title": "📖 Виды предложений по цели высказывания",
        "rule": "• Повествовательные — сообщают.\n• Вопросительные — спрашивают.\n• Побудительные — просят или приказывают.",
        "examples": [
            "Сегодня хорошая погода. (повествовательное)",
            "Ты сделал уроки? (вопросительное)",
            "Иди сюда! (побудительное)"
        ]
    },
    "главные и второстепенные члены предложения": {
        "title": "🔑 Главные и второстепенные члены предложения",
        "rule": "Главные члены — подлежащее и сказуемое. Второстепенные — дополняют смысл.",
        "examples": [
            "Мальчик (подлежащее) читает (сказуемое) книгу (дополнение)."
        ]
    },
    "имя существительное": {
        "title": "📦 Имя существительное",
        "rule": "Обозначает предмет. Отвечает на вопросы кто? что?",
        "examples": [
            "Кто? — мама, ученик.",
            "Что? — книга, школа."
        ]
    },
    "имя прилагательное": {
        "title": "🎨 Имя прилагательное",
        "rule": "Обозначает признак предмета. Отвечает на вопросы какой? какая? какое?",
        "examples": [
            "Красивый дом, добрая девочка."
        ]
    },
    "местоимение": {
        "title": "🙋 Местоимение",
        "rule": "Указывает на предмет, но не называет его.",
        "examples": [
            "я, ты, он, она, мы, вы, они"
        ]
    },
    "глагол": {
        "title": "⚡ Глагол",
        "rule": "Обозначает действие предмета. Вопросы: что делать? что сделать?",
        "examples": [
            "читать, писать, играть",
            "написать, прочитать"
        ]
    },
    "морфологический разбор глагола": {
        "title": "🛠 Морфологический разбор глагола",
        "rule": "1. Начальная форма (инфинитив)\n2. Вид\n3. Время\n4. Число\n5. Лицо или род",
        "examples": [
            "Играл — инфинитив: играть, вид: несовершенный, время: прошедшее, число: ед., род: мужской."
        ]
    }
}

# ===== КЛАВИАТУРЫ =====
def get_main_keyboard():
    keyboard = [
        ['📚 Синтаксис', '📦 Части речи'],
        ['✍️ Орфография', '⚡ Глаголы'],
        ['📖 Все темы', '❓ Помощь']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== КОМАНДЫ =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "👋 Привет! Я бот по русскому языку для 3 класса.\n\nВыбирай раздел на клавиатуре или пиши название темы.\nКоманды: /rules — список тем, /help — помощь."
    await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🆘 Используй кнопки или пиши название темы. Например: «предложение и словосочетание» или «глагол»."
    await update.message.reply_text(text)

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📖 Все доступные темы:\n\n"
    for key, data in RUSSIAN_RULES.items():
        text += f"• {data['title']}\n"
    await update.message.reply_text(text)

# ===== ОБРАБОТЧИК СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    for key, rule_data in RUSSIAN_RULES.items():
        if user_text in key:
            response = f"📖 {rule_data['title']}\n\n<b>Правило:</b>\n{rule_data['rule']}\n\n<b>Примеры:</b>\n"
            for ex in rule_data['examples']:
                response += f"• {ex}\n"
            await update.message.reply_text(response, parse_mode="HTML")
            return

    await update.message.reply_text("❌ Тема не найдена. Используй /rules.")

# ===== ЗАПУСК =====
def setup_application():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("rules", rules_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден!")
        return
    threading.Thread(target=run_flask_server, daemon=True).start()
    app = setup_application()
    logger.info("✅ Бот запускается...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

