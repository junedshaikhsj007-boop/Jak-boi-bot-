from telethon import TelegramClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --- Telegram API (full) ---
api_id = 22467314       # from my.telegram.org
api_hash = "08181401f6807cdc954f6c7d8231dfcf"
client = TelegramClient("session", api_id, api_hash)

# --- Telegram Bot ---
BOT_TOKEN = "7962211786:AAHBZIxnb6oJr2W3KXQE"
CHANNEL_ID = -2324737561   # your private channel ID
user_selected = {}

# Start bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a keyword to search my library:")

# Search handler
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.lower()

    results = []
    async with client:
        async for msg in client.iter_messages(CHANNEL_ID, search=query, limit=5):
            if msg.text:  # only text messages for now
                results.append((msg.id, msg.text[:40]))  # message ID + preview

    if not results:
        await update.message.reply_text("❌ No results found.")
        return

    keyboard = [[InlineKeyboardButton(text, callback_data=str(mid))] for mid, text in results]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🔎 Found results:", reply_markup=reply_markup)

# Button click
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    msg_id = int(query.data)
    user_selected[query.from_user.id] = msg_id

    # Short link (replace with your shortener)
    short_link = f"https://shortxlinks.com/{msg_id}"

    await query.edit_message_text(
        text=f"👉 Click this link to continue:\n{short_link}\n\nAfter ads, type /done"
    )

# Deliver final content
async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if uid not in user_selected:
        await update.message.reply_text("❌ No active request. Search again.")
        return

    msg_id = user_selected[uid]
    async with client:
        msg = await client.get_messages(CHANNEL_ID, ids=msg_id)
        await update.message.reply_text(f"🎁 Here is your content:\n\n{msg.text}")
    del user_selected[uid]

# Setup bot
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler("done", done))

print("✅ Bot is running...")
app.run_polling()
