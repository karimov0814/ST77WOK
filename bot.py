"""
Taklif & Shikoyat Telegram Bot
--------------------------------
O'rnatish:
  pip install python-telegram-bot==20.7

Ishga tushirish:
  python bot.py
"""

import json
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# =====================================================
#  SOZLAMALAR  —  faqat shu qismni o'zgartiring
# =====================================================
BOT_TOKEN = "8919742379:AAG_mBtlsxU4DluKoeXUvCfn2mscdZ1pP1M"          # @BotFather dan olgan token
ADMIN_CHAT_ID = 7780854728             # Sizning Telegram ID'ingiz (https://t.me/userinfobot orqali oling)
MINI_APP_URL = "https://karimov0814.github.io/feedback-bot/index.html"  # Mini app joylashgan URL
# =====================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat_id = update.effective_chat.id
    is_admin = (chat_id == ADMIN_CHAT_ID)

    if is_admin:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "📊 Admin Panel",
                web_app=WebAppInfo(url=MINI_APP_URL + "?admin=1")
            )
        ]])
        await update.message.reply_text(
            "👋 Salom, Admin!\n\nXodimlarning murojaatlari shu yerga keladi.",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "💬 Taklif yoki Shikoyat yuborish",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )
        ]])
        await update.message.reply_text(
            f"👋 Salom, {user.first_name}!\n\n"
            f"💡 <b>Taklif</b> — g'oyalaringizni yuboring\n"
            f"⚠️ <b>Shikoyat</b> — muammolaringizni bildiring\n\n"
            f"🔒 Anonim yuborish imkoniyati mavjud.\n\n"
            f"Boshlash uchun tugmani bosing 👇",
            reply_markup=keyboard,
            parse_mode="HTML"
        )


async def web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mini App'dan yuborilgan ma'lumotni qabul qilish va adminга forward qilish"""
    try:
        raw = update.message.web_app_data.data
        data = json.loads(raw)

        msg_type = data.get('type', '')
        filial = data.get('filial', '')
        text = data.get('text', '')
        anon = data.get('anon', False)
        time = data.get('time', '')

        sender_user = update.effective_user
        if anon:
            sender_text = "🕵️ <b>Anonim</b>"
        else:
            name = sender_user.first_name
            if sender_user.last_name:
                name += ' ' + sender_user.last_name
            username = f" @{sender_user.username}" if sender_user.username else ""
            sender_text = f"👤 {name}{username}"

        type_emoji = "💡" if msg_type == "taklif" else "⚠️"
        type_label = "TAKLIF" if msg_type == "taklif" else "SHIKOYAT"

        message = (
            f"{type_emoji} <b>{type_label}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏢 <b>Filial:</b> {filial}\n"
            f"{sender_text}\n"
            f"📅 <b>Vaqt:</b> {time}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💬 <b>Matn:</b>\n{text}"
        )

        # Adminга yuborish
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=message,
            parse_mode="HTML"
        )

        # Xodimga tasdiqlash xabari
        await update.message.reply_text(
            "✅ Murojaatingiz yuborildi!\n\nRahmat, tez orada ko'rib chiqiladi."
        )

        logger.info(f"Yangi {type_label}: {filial} — {'anonim' if anon else sender_user.id}")

    except Exception as e:
        logger.error(f"web_app_data xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")


import asyncio

async def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
    logger.info("✅ Bot ishga tushdi!")
    async with app:
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Bot polling boshlandi. To'xtatish uchun Ctrl+C")
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
