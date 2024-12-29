from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# متغیرهای اصلی
users = {}
connections = {}
MAX_MESSAGES = 10

# مرحله 1: شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! لطفا نام، سن و جنسیت خود را وارد کنید:")
    return 1

# مرحله 2: ذخیره اطلاعات کاربر
async def save_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    users[user_id] = {"info": update.message.text, "messages_left": MAX_MESSAGES}
    await update.message.reply_text("اطلاعات شما ذخیره شد. منتظر اتصال به یک نفر دیگر باشید.")
    
    # اتصال به یک کاربر دیگر
    for uid, data in users.items():
        if uid != user_id and uid not in connections.values():
            connections[user_id] = uid
            connections[uid] = user_id
            await context.bot.send_message(uid, "شما به یک کاربر متصل شدید! شروع به چت کنید.")
            await update.message.reply_text("شما به یک کاربر متصل شدید! شروع به چت کنید.")
            return ConversationHandler.END
    
    await update.message.reply_text("فعلا کاربری برای اتصال وجود ندارد. لطفاً منتظر بمانید.")
    return ConversationHandler.END

# مرحله 3: مدیریت چت بین کاربران
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in connections:
        partner_id = connections[user_id]
        if users[user_id]["messages_left"] > 0:
            users[user_id]["messages_left"] -= 1
            await context.bot.send_message(partner_id, update.message.text)
        else:
            await update.message.reply_text("تعداد پیام‌های شما تمام شده است. لطفاً بسته پیام خریداری کنید.")
    else:
        await update.message.reply_text("شما هنوز به کسی متصل نشده‌اید.")

# تعریف دستور خرید پیام‌های اضافی
async def buy_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id in users:
        users[user_id]["messages_left"] += 10  # اضافه کردن 10 پیام
        await update.message.reply_text("10 پیام جدید خریداری شد!")
    else:
        await update.message.reply_text("لطفاً ابتدا از دستور /start استفاده کنید.")

# تنظیمات اولیه ربات
app = ApplicationBuilder().token("7915679282:AAFCgO8nB29XfzifsjJdLOlZ81xnvqAoyXU").build()  # توکن ربات خود را جایگزین کنید

# تعریف حالت‌های ربات
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_info)]
    },
    fallbacks=[],
)

app.add_handler(conv_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.add_handler(CommandHandler("buy", buy_messages))  # اضافه کردن دستور خرید پیام

# شروع ربات
if __name__ == "__main__":
    app.run_polling()