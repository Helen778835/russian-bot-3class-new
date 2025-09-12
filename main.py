import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("Переменная окружения BOT_TOKEN не задана")
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана")

rules = {
    "Предложение и словосочетание": "Словосочетание — два и более слов, связанных по смыслу. Предложение — выражает законченную мысль...",
    "Виды предложений по цели высказывания": "Повествовательные (.) Вопросительные (?) Побудительные (. или !)",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот по русскому языку для 3 класса 📚\nНапиши название темы или используй команду /rules.")

async def list_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = "\n".join([f"• {topic}" for topic in rules.keys()])
    await update.message.reply_text("Доступные темы:\n" + topics)

async def get_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    for key, value in rules.items():
        if text in key.lower():
            await update.message.reply_text(f"**{key}**\n\n{value}", parse_mode='Markdown')
            return
    await update.message.reply_text("Правило не найдено. Используй /rules, чтобы увидеть список тем.")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("rules", list_rules))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_rule))
        
        logger.info("Бот запускается...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    main()
