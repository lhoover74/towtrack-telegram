from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from requests.exceptions import HTTPError, RequestException

from bot.config import BOT_TOKEN
from bot.services.api import create_vehicle, search_vehicle

PLATE, PROPERTY_NAME, LOCATION, TOW_REASON, NOTES = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "TowTrack bot is running.\n\n"
        "/start - start bot\n"
        "/ping - test bot\n"
        "/add - add a new vehicle\n"
        "/search ABC123 - search by plate"
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong")


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter the plate number:")
    return PLATE


async def add_plate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    context.user_data["plate"] = text
    await update.message.reply_text("Enter property name:")
    return PROPERTY_NAME


async def add_property(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["property_name"] = update.message.text.strip()
    await update.message.reply_text("Enter location:")
    return LOCATION


async def add_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["location"] = update.message.text.strip()
    await update.message.reply_text("Enter tow reason:")
    return TOW_REASON


async def add_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tow_reason"] = update.message.text.strip()
    await update.message.reply_text(
        "Enter notes (or type 'skip' to leave blank):"
    )
    return NOTES


async def add_notes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    if message_text.lower() in {"skip", "none", "n/a"}:
        notes = None
    else:
        notes = message_text

    payload = {
        "plate": context.user_data.get("plate"),
        "property_name": context.user_data.get("property_name"),
        "location": context.user_data.get("location"),
        "tow_reason": context.user_data.get("tow_reason"),
        "notes": notes,
    }

    try:
        vehicle = create_vehicle(payload)
    except RequestException:
        await update.message.reply_text("Service unavailable. Please try again later.")
        return ConversationHandler.END
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if status == 422:
            await update.message.reply_text("Validation error: please check the provided fields.")
        else:
            await update.message.reply_text(f"Error saving vehicle ({status}): {e}")
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"Error saving vehicle: {e}")
        return ConversationHandler.END

    await update.message.reply_text(
        f"Vehicle added successfully:\n"
        f"Plate: {vehicle.get('plate')}\n"
        f"Property: {vehicle.get('property_name')}\n"
        f"Location: {vehicle.get('location')}\n"
        f"Reason: {vehicle.get('tow_reason')}\n"
        f"Status: {vehicle.get('status', 'Observed')}"
    )

    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Add operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /search ABC123")
        return

    plate = context.args[0].upper()

    try:
        results = search_vehicle(plate)
    except HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            await update.message.reply_text("No records found")
        else:
            await update.message.reply_text("Service unavailable. Please try again later.")
        return
    except RequestException:
        await update.message.reply_text("Service unavailable. Please try again later.")
        return
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

    add_conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            PLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_plate)],
            PROPERTY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_property)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location)],
            TOW_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reason)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_notes)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_user=True,
        per_chat=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(add_conv)

    app.run_polling()


if __name__ == "__main__":
    main()
