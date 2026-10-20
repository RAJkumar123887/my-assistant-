"""Telegram channel: your assistant answers messages sent to your bot."""
import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

import brain

load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Optional: comma-separated Telegram user IDs allowed to use the bot.
ALLOWED = {u.strip() for u in os.getenv("ALLOWED_USER_IDS", "").split(",") if u.strip()}


def is_allowed(update: Update) -> bool:
    return not ALLOWED or str(update.effective_user.id) in ALLOWED


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    await update.message.reply_text(
        "Hi! I'm your assistant. Just send me a message. Use /reset to clear my memory."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    brain.reset(str(update.effective_chat.id))
    await update.message.reply_text("Memory cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        await update.message.reply_text("Sorry, you are not allowed to use this bot.")
        return
    await context.bot.send_chat_action(update.effective_chat.id, "typing")
    # The model call is blocking, so run it in a thread.
    answer = await asyncio.to_thread(
        brain.reply, str(update.effective_chat.id), update.message.text
    )
    await update.message.reply_text(answer[:4000])  # Telegram message limit


def main() -> None:
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in your .env file first (see README).")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Telegram bot running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
