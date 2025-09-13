import os
import logging
import threading
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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

# ===== БАЗА ДАННЫХ ПРАВИЛ С ПРИМЕРАМИ =====
RUSSIAN_RULES = {
    # Синтаксис
    "предложение": {
        "title": "📝 Предложение и словосочетание",
        "rule": "Предложение — это группа слов, выражающая законченную мысль. Словосочетание — два или более слов, связанных по смыслу.",
        "examples": [
            "✅ Предложение: «Мама читает книгу.» (есть законченная мысль)",
            "✅ Словосочетание: «читать книгу» (нет законченной мысли)",
            "❌ Не предложение: «красивый цветок» (нет законченной мысли)"
        ]
    },
    
    "знаки препинания": {
        "title": "🔤 Знаки препинания в конце предложений",
        "rule": "• Точка (.) — в повествовательных предложениях\n• Вопросительный знак (?) — в вопросах\n• Восклицательный знак (!) — в восклицательных предложениях",
        "examples": [
            "Сегодня хорошая погода. (повествование)",
            "Ты сделал уроки? (вопрос)",
            "Ура! Каникулы! (восклицание)"
        ]
    },

    # Морфология
    "существительное": {
        "title": "📦 Имя существительное",
        "rule": "Обозначает предмет и отвечает на вопросы кто? что?",
        "examples": [
            "кто? — ученик, мама, кошка",
            "что? — книга, школа, солнце"
        ]
    },

    "прилагательное": {
        "title": "🎨 Имя прилагательное", 
        "rule": "Обозначает признак предмета и отвечает на вопросы какой? какая? какое? какие?",
        "examples": [
            "какой? — красивый, умный, быстрый",
            "какая? — интересная, добрая, светлая",
            "какое? — большое, синее, вкусное"
        ]
    },

    "глагол": {
        "title": "⚡ Глагол",
        "rule": "Обозначает действие предмета и отвечает на вопросы что делать? что сделать?",
        "examples": [
            "что делать? — читать, писать, играть",
            "что сделать? — прочитать, написать, поиграть"
        ]
    },

    # Орфография
    "жи ши": {
        "title": "✍️ Правописание ЖИ-ШИ",
        "rule": "После Ж и Ш всегда пишется И (never Ы)!",
        "examples": [
            "✅ жираф, шишка, машина",
            "❌ жыраф, шышка, машына (так нельзя!)"
        ]
    },

    "ча ща": {
        "title": "✍️ Правописание ЧА-ЩА",
        "rule": "После Ч и Щ всегда пишется А (never Я)!",
        "examples": [
            "✅ чашка, щавель, задача",
            "❌ чяшка, щявель, задача (так нельзя!)"
        ]
    },

    "чу щу": {
        "title": "✍️ Правописание ЧУ-ЩУ", 
        "rule": "После Ч и Щ всегда пишется У (never Ю)!",
        "examples": [
            "✅ чудесный, щука, ищу",
            "❌ чюдесный, щюка, ищю (так нельзя!)"
        ]
    },

    # Разборы
    "звуко буквенный разбор": {
        "title": "🔊 Звуко-буквенный разбор слова",
        "rule": "1. Записать слово\n2. Поставить ударение\n3. Разделить на слоги\n4. Охарактеризовать звуки",
        "examples": [
            "Слово: «КОТ»",
            "К [к] — согласный, твердый, глухой",
            "О [о] — гласный, ударный", 
            "Т [т] — согласный, твердый, глухой",
            "3 буквы, 3 звука"
        ]
    },

    "разбор по составу": {
        "title": "🔍 Разбор слова по составу",
        "rule": "Найти: приставку, корень, суффикс, окончание",
        "examples": [
            "ПОДСНЕЖНИК",
            "приставка: ПОД-",
            "корень: -СНЕЖ-",
            "суффикс: -НИК-",
            "окончание: нулевое"
        ]
    }
}

# ===== КЛАВИАТУРЫ =====
def get_main_keyboard():
    keyboard = [
        ['📚 Синтаксис', '📦 Морфология'],
        ['✍️ Орфография', '🔍 Разборы'],
        ['❓ Помощь', '🎯 Все темы']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_syntax_keyboard():
    keyboard = [
        ['📝 Предложение', '🔤 Знаки препинания'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_morphology_keyboard():
    keyboard = [
        ['📦 Существительное', '🎨 Прилагательное'],
        ['⚡ Глагол', '🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_spelling_keyboard():
    keyboard = [
        ['ЖИ-ШИ', 'ЧА-ЩА', 'ЧУ-ЩУ'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_analysis_keyboard():
    keyboard = [
        ['🔊 Звуко-буквенный', '🔍 По составу'],
        ['🏠 Главное меню']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===== КОМАНДЫ БОТА =====
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome_text = """
    👋 Привет! Я бот-помощник по русскому языку для 3 класса! 💡

    📖 Я могу:
    • Объяснить правила с примерами
    • Показать орфограммы
    • Помочь с разборами слов
    • Ответить на вопросы по темам

    Выбери категорию на клавиатуре ↓ или напиши название темы!
    """
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """
    🆘 <b>Как пользоваться ботом:</b>

    • Используй кнопки для навигации
    • Или напиши название темы: 
      - «предложение»
      - «жи ши» 
      - «разбор по составу»
      - и другие

    📚 <b>Доступные категории:</b>
    • 📚 Синтаксис — предложения, знаки препинания
    • 📦 Морфология — части речи
    • ✍️ Орфография — правила написания
    • 🔍 Разборы — анализ слов

    Напиши /rules чтобы увидеть все темы!
    """
    await update.message.reply_text(help_text, parse_mode='HTML')

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /rules - все темы"""
    rules_text = "📚 <b>Все доступные темы:</b>\n\n"
    
    categories = {
        "📚 Синтаксис": ["предложение", "знаки препинания"],
        "📦 Морфология": ["существительное", "прилагательное", "глагол"],
        "✍️ Орфография": ["жи ши", "ча ща", "чу щу"],
        "🔍 Разборы": ["звуко буквенный разбор", "разбор по составу"]
    }
    
    for category, topics in categories.items():
        rules_text += f"<b>{category}:</b>\n"
        for topic in topics:
            rules_text += f"• {RUSSIAN_RULES[topic]['title']}\n"
        rules_text += "\n"
    
    rules_text += "\n📝 <i>Напиши название темы или выбери из меню!</i>"
    await update.message.reply_text(rules_text, parse_mode='HTML')

# ===== ОБРАБОТЧИКИ СООБЩЕНИЙ =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_text = update.message.text.lower()
    
    # Обработка кнопок главного меню
    if user_text == '📚 синтаксис':
        await update.message.reply_text(
            "📚 <b>Выбери тему по синтаксису:</b>",
            reply_markup=get_syntax_keyboard(),
            parse_mode='HTML'
        )
        return
        
    elif user_text == '📦 морфология':
        await update.message.reply_text(
            "📦 <b>Выбери часть речи:</b>",
            reply_markup=get_morphology_keyboard(),
            parse_mode='HTML'
        )
        return
        
    elif user_text == '✍️ орфография':
        await update.message.reply_text(
            "✍️ <b>Выбери орфограмму:</b>",
            reply_markup=get_spelling_keyboard(),
            parse_mode='HTML'
        )
        return
        
    elif user_text == '🔍 разборы':
        await update.message.reply_text(
            "🔍 <b>Выбери тип разбора:</b>",
            reply_markup=get_analysis_keyboard(),
            parse_mode='HTML'
        )
        return
        
    elif user_text == '🎯 все темы':
        await rules_command(update, context)
        return
        
    elif user_text == '❓ помощь':
        await help_command(update, context)
        return
        
    elif user_text == '🏠 главное меню':
        await update.message.reply_text(
            "🏠 <b>Главное меню:</b>",
            reply_markup=get_main_keyboard(),
            parse_mode='HTML'
        )
        return

    # Обработка тем из кнопок
    button_to_topic = {
        '📝 предложение': 'предложение',
        '🔤 знаки препинания': 'знаки препинания',
        '📦 существительное': 'существительное',
        '🎨 прилагательное': 'прилагательное',
        '⚡ глагол': 'глагол',
        'жи-ши': 'жи ши',
        'ча-ща': 'ча ща', 
        'чу-щу': 'чу щу',
        '🔊 звуко-буквенный': 'звуко буквенный разбор',
        '🔍 по составу': 'разбор по составу'
    }
    
    topic_key = button_to_topic.get(user_text.lower(), user_text)
    
    # Поиск темы в базе
    for key, rule_data in RUSSIAN_RULES.items():
        if topic_key in key or key in topic_key:
            response = f"📖 <b>{rule_data['title']}</b>\n\n"
            response += f"<b>Правило:</b>\n{rule_data['rule']}\n\n"
            response += "<b>Примеры:</b>\n"
            for example in rule_data['examples']:
                response += f"• {example}\n"
            
            await update.message.reply_text(response, parse_mode='HTML')
            return
    
    # Если тема не найдена
    await update.message.reply_text(
        "❌ Тема не найдена. Используй /rules чтобы увидеть все доступные темы "
        "или выбери категорию из меню ↓",
        reply_markup=get_main_keyboard()
    )

# ===== ОСНОВНАЯ КОНФИГУРАЦИЯ =====
def setup_application():
    """Настройка приложения бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rules", rules_command))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    return application

def run_flask_server():
    """Запуск Flask сервера"""
    port = int(os.environ.get('PORT', 5000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def main():
    """Главная функция запуска"""
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден!")
        return
    
    # Запуск Flask сервера
    flask_thread = threading.Thread(target=run_flask_server, daemon=True)
    flask_thread.start()
    logger.info("🌐 Flask сервер запущен")
    
    # Запуск бота
    try:
        application = setup_application()
        logger.info("✅ Бот запускается...")
        application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()
