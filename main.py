import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не задана")

rules = {
    "Предложение и словосочетание": "Словосочетание — два и более слов, связанных по смыслу. "
                                     "Предложение — выражает законченную мысль, начинается с заглавной буквы и заканчивается знаком (. ? !)",
    "Виды предложений по цели высказывания": "Повествовательные (.) Вопросительные (?) Побудительные (. или !)",
    "Главные и второстепенные члены предложения": "Главные: подлежащее и сказуемое. "
                                                  "Второстепенные: дополнение, определение, обстоятельство.",
    "Имя существительное": "Отвечает на вопросы кто? что?.",
    "Имя прилагательное": "Обозначает признак предмета.",
    "Глагол": "Обозначает действие.",
    "Местоимение": "Указывает на предметы, признаки. Не называет их.",
    "Повторение": "Закрепи: орфограммы, части речи, разборы."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот по русскому языку для 3 класса 📚\n"
        "Напиши название темы или используй команду /rules."
    )

async def list_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = "\n".join(rules.keys())
    await update.message.reply_text("Доступные темы:\n" + topics)

async def get_rule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    for key, value in rules.items():
        if text in key.lower():
            await update.message.reply_text(value)
            return
    await update.message.reply_text("Правило не найдено. Используй /rules.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rules", list_rules))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_rule))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
