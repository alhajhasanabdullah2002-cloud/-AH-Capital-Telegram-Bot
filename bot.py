import os
import copy
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    CommandHandler,
    filters,
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]

START_URL = (
    "https://t.me/AH_CAPITAL"
    "?text=Hi%2C%20I%20want%20to%20get%20started%20with%20AH%20CAPITAL%20BOT."
    "%20How%20can%20I%20start%3F%20%F0%9F%A4%96%F0%9F%9A%80"
)

# Temporary drafts. Key = Telegram user ID
drafts = {}


def start_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ START ⬅️", url=START_URL)]
    ])


def preview_controls():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Publish", callback_data="publish"),
            InlineKeyboardButton("🗑 Cancel", callback_data="cancel"),
        ]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 AH CAPITAL Publisher\n\n"
        "Send me the post you want to publish.\n"
        "Text, photo or video is supported.\n\n"
        "After you send it, I will show you a preview."
    )


async def receive_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    # Save a copy of the original Telegram message.
    # copy_message preserves Telegram formatting/entities, including
    # custom emoji entities supported by the Bot API.
    drafts[update.effective_user.id] = {
        "chat_id": msg.chat_id,
        "message_id": msg.message_id,
    }

    await msg.reply_text("👀 Preview:")

    try:
        await context.bot.copy_message(
            chat_id=msg.chat_id,
            from_chat_id=msg.chat_id,
            message_id=msg.message_id,
            reply_markup=start_button(),
        )
    except Exception as e:
        await msg.reply_text(f"❌ Could not create preview:\n{e}")
        return

    await msg.reply_text(
        "Publish this post to AH CAPITAL?",
        reply_markup=preview_controls(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if query.data == "cancel":
        drafts.pop(user_id, None)
        await query.edit_message_text("🗑 Post cancelled.")
        return

    if query.data != "publish":
        return

    draft = drafts.get(user_id)

    if not draft:
        await query.edit_message_text(
            "❌ Draft not found. Send the post again."
        )
        return

    try:
        await context.bot.copy_message(
            chat_id=CHANNEL_ID,
            from_chat_id=draft["chat_id"],
            message_id=draft["message_id"],
            reply_markup=start_button(),
        )

        drafts.pop(user_id, None)

        await query.edit_message_text(
            "✅ Published successfully to AH CAPITAL."
        )

    except Exception as e:
        await query.edit_message_text(
            f"❌ Publishing failed:\n{e}"
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    app.add_handler(
        MessageHandler(
            (filters.TEXT | filters.PHOTO | filters.VIDEO)
            & ~filters.COMMAND,
            receive_post,
        )
    )

    print("AH CAPITAL Publisher is running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
