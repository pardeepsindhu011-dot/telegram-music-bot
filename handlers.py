from config import ADMIN_ID

from database import (
    get_all_users,
    get_user_count,
    get_users
)
from telegram import Update
from telegram.ext import ContextTypes


# ==============================
# ADMIN AUTHENTICATION
# ==============================

def is_admin(user_id):
    return user_id == ADMIN_ID


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if is_admin(user_id):
        await update.message.reply_text(
            "✅ Admin access granted."
        )
    else:
        await update.message.reply_text(
            "❌ Access denied."
        )


# ==============================
# BROADCAST
# ==============================

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Access denied."
        )
        return

    message = " ".join(context.args)

    if not message:
        await update.message.reply_text(
            "Please enter a message.\n"
            "Example: /broadcast Hello everyone!"
        )
        return

    users = get_all_users()

    for user in users:

        target_user_id = user[0]

        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=message
            )

        except Exception:
            pass

    await update.message.reply_text(
        "✅ Broadcast sent."
    )


# ==============================
# USER STATISTICS
# ==============================

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    print(f"TEST LOG: Stats requested by user {user_id}")

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Access denied."
        )
        return

    total_users = get_user_count()

    await update.message.reply_text(
        f"📊 User Statistics\n\n"
        f"Total users: {total_users}"
    )


# ==============================
# USER MANAGEMENT
# ==============================

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Access denied."
        )
        return

    user_list = get_users()

    if not user_list:
        await update.message.reply_text(
            "No users found."
        )
        return

    message = "👥 Users\n\n"

    for user in user_list:

        target_user_id = user[0]
        language = user[1]

        message += (
            f"ID: {target_user_id}\n"
            f"Language: {language}\n\n"
        )

    await update.message.reply_text(
        message
    )


# ==============================
# REMINDER
# ==============================

async def reminder_callback(context: ContextTypes.DEFAULT_TYPE):

    data = context.job.data

    await context.bot.send_message(
        chat_id=data["chat_id"],
        text=f"⏰ Reminder\n\n{data['message']}"
    )


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) < 2:

        await update.message.reply_text(
            "Please use:\n"
            "/remind seconds message\n\n"
            "Example:\n"
            "/remind 30 Drink water"
        )

        return

    try:

        seconds = int(context.args[0])

    except ValueError:

        await update.message.reply_text(
            "Time must be a number.\n"
            "Example: /remind 30 Drink water"
        )

        return

    if seconds <= 0:

        await update.message.reply_text(
            "Please enter a time greater than 0 seconds."
        )

        return

    reminder_message = " ".join(context.args[1:])

    chat_id = update.effective_chat.id

    await update.message.reply_text(
        f"✅ Reminder set for {seconds} seconds."
    )

    context.job_queue.run_once(
        reminder_callback,
        seconds,
        data={
            "chat_id": chat_id,
            "message": reminder_message
        }
    )


# ==============================
# NOTIFICATION
# ==============================

async def send_notification(context: ContextTypes.DEFAULT_TYPE):

    chat_id = context.job.data["chat_id"]

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "🔔 Notification\n\n"
            "This is your scheduled notification."
        )
    )


async def notify(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    context.job_queue.run_once(
        send_notification,
        10,
        data={
            "chat_id": chat_id
        }
    )

    await update.message.reply_text(
        "✅ Notification scheduled for 10 seconds."
    )


# ==============================
# DATABASE MONITORING
# ==============================

async def monitor_database(context: ContextTypes.DEFAULT_TYPE):

    try:

        total_users = get_user_count()

        print(
            f"MONITORING: Database OK | "
            f"Users: {total_users}"
        )

    except Exception as error:

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🚨 Database monitoring error:\n{error}"
        )
