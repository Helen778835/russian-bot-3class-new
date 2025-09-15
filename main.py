import os
import logging
import threading
import re
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ---------- ЛОГИ ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- FLASK СЕРВЕР (Render держит порт открытым) ----------
web_app = Flask(__name__)

@web_app.get("/")
def healthcheck():
    return "OK: russian-bot-3class is running"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    web_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ---------- НАСТРОЙКИ БОТА ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ---------- БАЗА ПРАВИЛ (короткая версия) ----------
RUSSIAN_RULES = {
    "предложение и словосочетание": {
        "title": "📝 Предложение и словосочетание",
        "rule": "Словосочетание — два и более слов, связанных по смыслу. "
                "Предложение выражает законченную мысль, начинается с заглавной буквы и оканчивается знаком (. ? !).",
        "example": "«читать книгу» — словосочетание; «Мама читает книгу.» — предложение."
    },
    "виды предложений по цели высказывания": {
        "title": "🎯 Виды предложений по цели высказывания",
        "rule": "Повествовательные (.) — сообщают; Вопросительные (?) — спрашивают; Побудительные (! или .) — призывают к действию.",
        "example": "«Сегодня тепло.» — повествовательное; «Ты сделал уроки?» — вопросительное; «Давай читать!» — побудительное."
    },
    "главные и второстепенные члены предложения": {
        "title": "🏗 Главные и второстепенные члены предложения",
        "rule": "Главные: подлежащее (кто? что?) и сказуемое (что делает?). Второстепенные: дополнение, определение, обстоятельство.",
        "example": "«Кот (подлеж.) спит (сказ.) на коврике (обст.).»"
    },
    "часть речи имя существительное": {
        "title": "📦 Имя существительное",
        "rule": "Обозначает предмет, отвечает на вопросы кто? что?, изменяется по числам и падежам.",
        "example": "кто? — мама; что? — дом."
    },
    "часть речи имя прилагательное": {
        "title": "🎨 Имя прилагательное",
        "rule": "Обозначает признак предмета, отвечает на вопросы какой? какая? какое? какие?, согласуется с существительным.",
        "example": "весёлый мальчик, синее небо."
    },
    "часть речи местоимение": {
        "title": "🧭 Местоимение",
        "rule": "Указывает на предметы, признаки, количества, не называя их.",
        "example": "он, она, это, такой, столько."
    },
    "часть речи глагол": {
        "title": "⚡ Глагол",
        "rule": "Обозначает действие. Вопросы: что делать? что сделать? Изменяется по временам, числам, родам.",
        "example": "читать, написал, думают."
    },
    "морфологический разбор глагола": {
        "title": "🧾 Морфологический разбор глагола",
        "rule": "Определи начальную форму, вид, время, число/род, лицо.",
        "example": "читает: инф. «читать», вид — несов., наст. вр., ед.ч., 3-е лицо."
    }
}

def clean_text(text: str) -> str:
    """Очистка текста: убираем эмодзи и приводим к нижнему регистру"""
    return re.sub(r"[^\w\s]", "", text).lower().strip()

# ---------- КЛАВИАТУРЫ ----------
def main_keyboard():
    kb = [
        ["📚 Синтаксис", "📦 Части речи"],
        ["✍️ Орфография", "⚡ Глаголы"],
        ["🎯 Все темы", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True)

# ---------- КОМАНДЫ ----------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 Привет! Я бот по русскому языку для 3 класса.\n\n"
        "Выбирай раздел на клавиатуре или напиши название темы.\n"
        "Команды: /rules — список тем, /help — помощь."
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🆘 Помощь\n"
        "— Нажимай кнопки для выбора раздела.\n"
        "— Или пиши тему (например: «глагол», «существительное»).\n"
        "— Команда /rules покажет все темы по разделам."
    )
    await update.message.reply_text(text, reply_markup=main_keyboard())

async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = ["📚 Все доступные темы:\n"]
    for key, val in RUSSIAN_RULES.items():
        txt.append(f"• {val['title']}")
    await update.message.reply_text("\n".join(txt), reply_markup=main_keyboard())

# ---------- ОБРАБОТКА ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = clean_text(update.message.text)

    # Реакция на кнопки разделов
    if "синтаксис" in msg:
        await update.message.reply_text(
            "📚 Темы по синтаксису:\n• Предложение и словосочетание\n• Виды предложений по цели высказывания\n• Главные и второстепенные члены предложения",
            reply_markup=main_keyboard()
        )
        return
    elif "орфография" in msg:
        await update.message.reply_text(
            "✍️ Темы по орфографии:\n• Жи-ши\n• Ча-ща\n• Чу-щу",
            reply_markup=main_keyboard()
        )
        return
    elif "части речи" in msg:
        await update.message.reply_text(
            "📦 Части речи:\n• Имя существительное\n• Имя прилагательное\n• Местоимение\n• Глагол",
            reply_markup=main_keyboard()
        )
        return
    elif "глагол" in msg or "глаголы" in msg:
        await update.message.reply_text(
            "⚡ Темы по глаголу:\n• Времена глаголов\n• Морфологический разбор глагола",
            reply_markup=main_keyboard()
        )
        return
    elif "все темы" in msg:
        await cmd_rules(update, context)
        return
    elif "помощь" in msg:
        await cmd_help(update, context)
        return

    # Проверка по базе правил
    for key, data in RUSSIAN_RULES.items():
        if msg in key or key in msg:
            resp = f"📖 <b>{data['title']}</b>\n\n<b>Правило:</b> {data['rule']}\n\n<b>Пример:</b> {data['example']}"
            await update.message.reply_text(resp, parse_mode="HTML", reply_markup=main_keyboard())
            return

    # Если ничего не найдено
    await update.message.reply_text("❌ Тема не найдена. Используй /rules.", reply_markup=main_keyboard())

# ---------- ЗАПУСК ----------
def build_app():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не задан!")
        raise SystemExit(1)
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("rules", cmd_rules))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return app

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    application = build_app()
    logger.info("✅ Бот запускается...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
