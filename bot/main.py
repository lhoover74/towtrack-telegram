from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from bot.config import BOT_TOKEN
from bot.services.api import search_vehicle


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "TowTrack bot is running.\n\n"
        "/start - start bot\n"
        "/ping - test bot\n"
        "/search ABC123 - search by plate"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search ABC123")
        return

    plate = context.args[0].upper()

    try:
        results = search_vehicle(plate)
    except Exception as e:
        await update.message.reply_text(f"Search failed: {e}")
        return

    if not results:
        await update.message.reply_text("No records found")
        return

    lines = []
    for r in results:
        lines.append(
            f"Plate: {r.get('plate')}\n"
            f"Property: {r.get('property_name')}\n"
            f"Location: {r.get('location')}\n"
            f"Reason: {r.get('tow_reason')}\n"
            f"Status: {r.get('status')}"
        )

    await update.message.reply_text("\n\n".join(lines))


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("search", search))
    app.run_polling()


if __name__ == "__main__":
    main()
