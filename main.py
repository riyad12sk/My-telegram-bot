from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import threading
import sqlite3

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


# ==================================================
# BUILT-IN HTTP KEEP-ALIVE SERVER
# ==================================================
class HealthCheckHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Bot is running!')

    def log_message(self, format, *args):
        return


def start_health_server():
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()


threading.Thread(
    target=start_health_server,
    daemon=True
).start()


# ==================================================
# BOT CONFIGURATION
# ==================================================
BOT_TOKEN = os.environ.get('BOT_TOKEN')

ADMIN_ID = 7132512163


# ==================================================
# DATABASE
# ==================================================
DB_FILE = 'users.db'


def init_database():
    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_user(user):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        """
        INSERT OR REPLACE INTO users
        (chat_id, first_name, username)
        VALUES (?, ?, ?)
        """,
        (
            user.id,
            user.first_name or '',
            user.username or '',
        )
    )

    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_FILE)

    rows = conn.execute(
        "SELECT chat_id FROM users"
    ).fetchall()

    conn.close()

    return [row[0] for row in rows]


def remove_user(chat_id):
    conn = sqlite3.connect(DB_FILE)

    conn.execute(
        "DELETE FROM users WHERE chat_id = ?",
        (chat_id,)
    )

    conn.commit()
    conn.close()


# ==================================================
# REQUIRED CHANNELS
# ==================================================
REQUIRED_CHANNELS = [
    {
        'name': '📢 Channel 1',
        'chat_id': '@vrailsop',
        'url': 'https://t.me/vrailsop',
    },
    {
        'name': '📢 Channel 2',
        'chat_id': '@hotgolp12',
        'url': 'https://t.me/hotgolp12',
    },
    {
        'name': '📢 Channel 3',
        'chat_id': '@viral_video1538',
        'url': 'https://t.me/viral_video1538',
    },
    {
        'name': '📢 Channel 4',
        'chat_id': '@sk_black_cat',
        'url': 'https://t.me/sk_black_cat',
    },
]


# ==================================================
# PRIVATE CHANNEL
# ==================================================
PRIVATE_CHANNEL_ID = -1004358649143
PRIVATE_CHANNEL_URL = 'https://t.me/hotvideo_14'


# ==================================================
# LOGGING
# ==================================================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ==================================================
# WELCOME TEXT
# ==================================================
def welcome_text(user):
    name = user.first_name or 'User'

    return (
        '⚠︎☠︎︎★彡 VIRAL TOP 1 彡★☠︎︎⚠︎\n\n'
        f'🎉 স্বাগতম, {name}!\n\n'
        'আপনাকে আমাদের Bot-এ স্বাগতম। ❤️\n\n'
        f'🆔 আপনার Telegram ID: {user.id}\n\n'
        '🚀 আমাদের বিশেষ সুবিধাগুলো ব্যবহার করতে '
        'প্রথমে Verification সম্পন্ন করুন।\n\n'
        '👇 নিচের বাটনে চাপ দিয়ে শুরু করুন।'
    )


# ==================================================
# KEYBOARDS
# ==================================================
def verification_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            "🤖 I'm Not a Robot",
            callback_data='start_verify',
        )
    ]])


def channel_keyboard():
    rows = []

    for channel in REQUIRED_CHANNELS:
        rows.append([
            InlineKeyboardButton(
                channel['name'],
                url=channel['url']
            )
        ])

    rows.append([
        InlineKeyboardButton(
            '✅ Verify',
            callback_data='verify'
        )
    ])

    return InlineKeyboardMarkup(rows)


def retry_keyboard():
    rows = []

    for channel in REQUIRED_CHANNELS:
        rows.append([
            InlineKeyboardButton(
                channel['name'],
                url=channel['url']
            )
        ])

    rows.append([
        InlineKeyboardButton(
            '🔄 Verify Again',
            callback_data='verify'
        )
    ])

    return InlineKeyboardMarkup(rows)


def success_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            '🔐 Request to Join Private Channel',
            url=PRIVATE_CHANNEL_URL,
        )
    ]])


# ==================================================
# MEMBERSHIP CHECK
# ==================================================
async def is_member(bot, user_id, chat_id):
    try:
        member = await bot.get_chat_member(
            chat_id=chat_id,
            user_id=user_id
        )

        return member.status not in {
            ChatMemberStatus.LEFT,
            ChatMemberStatus.BANNED,
        }

    except Exception as exc:
        logger.warning(
            'Membership check failed: user=%s chat=%s error=%s',
            user_id,
            chat_id,
            exc,
        )

        return False


async def check_all_channels(bot, user_id):
    for channel in REQUIRED_CHANNELS:

        if not await is_member(
            bot,
            user_id,
            channel['chat_id']
        ):
            return False

    return True


# ==================================================
# START COMMAND
# ==================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    # Save user for broadcast
    save_user(user)

    try:
        username = (
            f'@{user.username}'
            if user.username
            else 'নেই'
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                '🔔 **নতুন ইউজার বট চালু করেছে!**\n\n'
                f'👤 **নাম:** {user.first_name}\n'
                f'🆔 **User ID:** `{user.id}`\n'
                f'🔗 **ইউজারনেম:** {username}'
            ),
            parse_mode='Markdown',
        )

    except Exception as exc:
        logger.warning(
            'Could not notify admin about new start: %s',
            exc
        )

    await update.message.reply_text(
        welcome_text(user),
        reply_markup=verification_keyboard()
    )


# ==================================================
# HELP
# ==================================================
async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        '🆘 সাহায্য\n\n'
        '/start — Bot শুরু করুন\n'
        '/help — সাহায্য দেখুন\n'
        '/menu — Main Menu খুলুন\n'
        '/about — Bot সম্পর্কে জানুন\n'
        '/contact — যোগাযোগের তথ্য দেখুন'
    )


# ==================================================
# MENU
# ==================================================
async def menu_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        '📋 Main Menu\n\n'
        'নিচের বাটনে চাপ দিয়ে Verification শুরু করুন।',
        reply_markup=verification_keyboard(),
    )


# ==================================================
# ABOUT
# ==================================================
async def about_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        '⚠︎☠︎︎★彡 VIRAL TOP 1 彡★☠︎︎⚠︎\n\n'
        'এটি একটি Telegram Bot।\n'
        'আপনার জন্য প্রয়োজনীয় তথ্য ও ফিচার '
        'এক জায়গায় দেওয়ার জন্য এটি তৈরি করা হয়েছে।'
    )


# ==================================================
# CONTACT
# ==================================================
async def contact_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        '📞 Contact Support\n\n'
        'প্রয়োজনে Bot Admin-এর সঙ্গে যোগাযোগ করুন।'
    )


# ==================================================
# ADMIN BROADCAST COMMAND
# ==================================================
async def broadcast_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    # Only admin
    if not user or user.id != ADMIN_ID:
        return

    context.user_data['broadcast_mode'] = True

    total_users = len(get_all_users())

    await update.message.reply_text(
        '📢 **Video Broadcast Mode চালু হয়েছে।**\n\n'
        'এখন আমাকে একটি ভিডিও পাঠান।\n\n'
        f'👥 বর্তমানে সংরক্ষিত User: {total_users}\n\n'
        '❌ বন্ধ করতে /cancelbroadcast লিখুন।',
        parse_mode='Markdown',
    )


# ==================================================
# CANCEL BROADCAST
# ==================================================
async def cancel_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    if not user or user.id != ADMIN_ID:
        return

    context.user_data['broadcast_mode'] = False

    await update.message.reply_text(
        '❌ Video Broadcast বন্ধ করা হয়েছে।'
    )


# ==================================================
# VIDEO BROADCAST
# ==================================================
async def video_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    # Only admin can broadcast
    if not user or user.id != ADMIN_ID:
        return

    # Check broadcast mode
    if not context.user_data.get(
        'broadcast_mode',
        False
    ):
        return

    if not update.message or not update.message.video:
        return

    video = update.message.video

    users = get_all_users()

    if not users:
        context.user_data['broadcast_mode'] = False

        await update.message.reply_text(
            '⚠️ কোনো User পাওয়া যায়নি।'
        )

        return

    success = 0
    failed = 0

    await update.message.reply_text(
        f'📤 Broadcast শুরু হয়েছে...\n\n'
        f'👥 মোট User: {len(users)}'
    )

    for chat_id in users:

        try:

            await context.bot.send_video(
                chat_id=chat_id,
                video=video.file_id,
                caption=update.message.caption,
                parse_mode=update.message.parse_mode,
            )

            success += 1

        except Exception as exc:

            failed += 1

            logger.warning(
                'Broadcast failed for %s: %s',
                chat_id,
                exc
            )

            # User blocked bot / chat unavailable
            error_text = str(exc).lower()

            if (
                'blocked' in error_text
                or 'chat not found' in error_text
                or 'user is deactivated' in error_text
            ):
                remove_user(chat_id)

    context.user_data['broadcast_mode'] = False

    await update.message.reply_text(
        '✅ **Broadcast সম্পন্ন হয়েছে!**\n\n'
        f'📨 সফলভাবে পাঠানো: {success}\n'
        f'❌ পাঠানো যায়নি: {failed}\n'
        f'👥 মোট User: {len(users)}',
        parse_mode='Markdown',
    )


# ==================================================
# BUTTON HANDLER
# ==================================================
async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query
    user = query.from_user

    try:
        await query.answer()
    except Exception:
        pass

    if query.data == 'start_verify':

        await query.edit_message_text(
            '🔐 Verification Required\n\n'
            'আপনি একজন আসল User কিনা নিশ্চিত করতে '
            'নিচের সবগুলো Channel/Group-এ Join করুন।\n\n'
            '✅ সবগুলো Channel/Group-এ Join করার পর '
            'নিচের Verify বাটনে চাপ দিন।',
            reply_markup=channel_keyboard(),
        )

        return

    if query.data == 'verify':

        await query.edit_message_text(
            '⏳ Verification চলছে...\n\n'
            'দয়া করে একটু অপেক্ষা করুন।'
        )

        verified = await check_all_channels(
            context.bot,
            user.id
        )

        if verified:

            try:

                username = (
                    f'@{user.username}'
                    if user.username
                    else 'নেই'
                )

                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=(
                        '🎉 **ইউজার সফলভাবে Verify সম্পন্ন করেছে!**\n\n'
                        f'👤 **নাম:** {user.first_name}\n'
                        f'🆔 **User ID:** `{user.id}`\n'
                        f'🔗 **ইউজারনেম:** {username}'
                    ),
                    parse_mode='Markdown',
                )

            except Exception as exc:

                logger.warning(
                    'Could not notify admin about verification: %s',
                    exc
                )

            await query.edit_message_text(
                '✅ Verification Successful!\n\n'
                f'অভিনন্দন, {user.first_name or "User"}! 🎉\n\n'
                'আপনার Verification সফলভাবে সম্পন্ন হয়েছে।\n\n'
                '🔐 এখন নিচের Private Channel-এ Join Request পাঠান।\n\n'
                '📨 Request পাঠানোর পর Admin আপনার Request চেক করে আপনাকে Add'
                ' করবেন।\n\n'
                '👇 নিচের বাটনে চাপ দিন:',
                reply_markup=success_keyboard(),
            )

        else:

            await query.edit_message_text(
                '❌ Verification Failed\n\n'
                'আপনি এখনো সবগুলো Required Channel/Group-এ Join করেননি।\n\n'
                'দয়া করে উপরের সবগুলো Channel/Group-এ Join করুন, তারপর আবার Verify'
                ' করুন।',
                reply_markup=retry_keyboard(),
            )


# ==================================================
# JOIN REQUEST HANDLER
# ==================================================
async def join_request_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    request = update.chat_join_request

    if not request:
        return

    if request.chat.id != PRIVATE_CHANNEL_ID:
        return

    user = request.from_user

    # Save user too
    save_user(user)

    try:

        username = (
            f'@{user.username}'
            if user.username
            else 'নেই'
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                '📩 **Private Channel-এ নতুন Join Request এসেছে!**\n\n'
                f'👤 **নাম:** {user.first_name}\n'
                f'🆔 **User ID:** `{user.id}`\n'
                f'🔗 **ইউজারনেম:** {username}'
            ),
            parse_mode='Markdown',
        )

    except Exception as exc:

        logger.warning(
            'Could not notify admin about join request: %s',
            exc
        )

    try:

        await context.bot.send_message(
            chat_id=user.id,
            text=(
                '📨 আপনার Private Channel Join Request পাওয়া গেছে।\n\n'
                '⏳ Admin আপনার Request চেক করে আপনাকে Add করবেন।\n\n'
                'দয়া করে অপেক্ষা করুন। ❤️'
            ),
        )

    except Exception as exc:

        logger.warning(
            'Could not notify join requester %s: %s',
            user.id,
            exc
        )


# ==================================================
# ERROR HANDLER
# ==================================================
async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        'Exception while handling an update:',
        exc_info=context.error
    )


# ==================================================
# MAIN
# ==================================================
def main():

    if not BOT_TOKEN:

        logger.error(
            'BOT_TOKEN is missing in Render Environment!'
        )

        return

    # Initialize database
    init_database()

    app = (
        Application
        .builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Normal commands
    app.add_handler(
        CommandHandler('start', start)
    )

    app.add_handler(
        CommandHandler('help', help_command)
    )

    app.add_handler(
        CommandHandler('menu', menu_command)
    )

    app.add_handler(
        CommandHandler('about', about_command)
    )

    app.add_handler(
        CommandHandler('contact', contact_command)
    )

    # Broadcast commands
    app.add_handler(
        CommandHandler(
            'broadcast',
            broadcast_command
        )
    )

    app.add_handler(
        CommandHandler(
            'cancelbroadcast',
            cancel_broadcast
        )
    )

    # Video broadcast handler
    app.add_handler(
        MessageHandler(
            filters.VIDEO,
            video_broadcast
        )
    )

    # Buttons
    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # Join request
    app.add_handler(
        ChatJoinRequestHandler(
            join_request_handler
        )
    )

    # Error handler
    app.add_error_handler(error_handler)

    print('🤖 Bot is running...')

    app.run_polling(
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
