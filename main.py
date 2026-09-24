import logging
import os
import threading
from flask import Flask

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatMemberStatus
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    CommandHandler,
    ContextTypes,
)

# ==================================================
# FLASK KEEP-ALIVE SERVER
# ==================================================
app = Flask('')


@app.route('/')
def home():
  return 'Bot is running!'


def run():
  port = int(os.environ.get('PORT', 8080))
  app.run(host='0.0.0.0', port=port)


threading.Thread(target=run, daemon=True).start()

# ==================================================
# BOT TOKEN (Render Env Var prioritized)
# ==================================================
BOT_TOKEN = os.environ.get(
    'BOT_TOKEN', '8717201146:AAFTD0CpFcaUVgLJf25gKNd3ieTgxRRRiSg'
)

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
        'chat_id': '@viral_video543',
        'url': 'https://t.me/viral_video543',
    },
    {
        'name': '📢 Channel 4',
        'chat_id': '@gmfmmmm',
        'url': 'https://t.me/gmfmmmm',
    },
]

# ==================================================
# PRIVATE CHANNEL
# ==================================================
PRIVATE_CHANNEL_ID = -1004358649143
PRIVATE_CHANNEL_URL = 'https://t.me/+vDYw2pQRl6hmZTQ1'

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
    rows.append(
        [InlineKeyboardButton(channel['name'], url=channel['url'])]
    )
  rows.append([InlineKeyboardButton('✅ Verify', callback_data='verify')])
  return InlineKeyboardMarkup(rows)


def retry_keyboard():
  rows = []
  for channel in REQUIRED_CHANNELS:
    rows.append(
        [InlineKeyboardButton(channel['name'], url=channel['url'])]
    )
  rows.append(
      [InlineKeyboardButton('🔄 Verify Again', callback_data='verify')]
  )
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
    member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    # Member, Admin, Owner এবং Restricted (গ্রুপের সাধারণ ইউজার) সবাইকে গ্রহণ করবে
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
    if not await is_member(bot, user_id, channel['chat_id']):
      return False
  return True


# ==================================================
# COMMAND HANDLERS
# ==================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user = update.effective_user
  await update.message.reply_text(
      welcome_text(user), reply_markup=verification_keyboard()
  )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      '🆘 সাহায্য\n\n'
      '/start — Bot শুরু করুন\n'
      '/help — সাহায্য দেখুন\n'
      '/menu — Main Menu খুলুন\n'
      '/about — Bot সম্পর্কে জানুন\n'
      '/contact — যোগাযোগের তথ্য দেখুন'
  )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      '📋 Main Menu\n\nনিচের বাটনে চাপ দিয়ে Verification শুরু করুন।',
      reply_markup=verification_keyboard(),
  )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      '⚠︎☠︎︎★彡 VIRAL TOP 1 彡★☠︎︎⚠︎\n\n'
      'এটি একটি Telegram Bot।\n'
      'আপনার জন্য প্রয়োজনীয় তথ্য ও ফিচার '
      'এক জায়গায় দেওয়ার জন্য এটি তৈরি করা হয়েছে।'
  )


async def contact_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  await update.message.reply_text(
      '📞 Contact Support\n\nপ্রয়োজনে Bot Admin-এর সঙ্গে যোগাযোগ করুন।'
  )


# ==================================================
# BUTTON HANDLER
# ==================================================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        '⏳ Verification চলছে...\n\nদয়া করে একটু অপেক্ষা করুন।'
    )

    verified = await check_all_channels(context.bot, user.id)

    if verified:
      await query.edit_message_text(
          '✅ Verification Successful!\n\n'
          f"অভিনন্দন, {user.first_name or 'User'}! 🎉\n\n"
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
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  request = update.chat_join_request
  if not request or request.chat.id != PRIVATE_CHANNEL_ID:
    return

  user = request.from_user
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
    logger.warning('Could not notify join requester %s: %s', user.id, exc)


# ==================================================
# ERROR HANDLER
# ==================================================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
  logger.error(
      'Exception while handling an update:', exc_info=context.error
  )


# ==================================================
# MAIN
# ==================================================
def main():
  app = Application.builder().token(BOT_TOKEN).build()

  app.add_handler(CommandHandler('start', start))
  app.add_handler(CommandHandler('help', help_command))
  app.add_handler(CommandHandler('menu', menu_command))
  app.add_handler(CommandHandler('about', about_command))
  app.add_handler(CommandHandler('contact', contact_command))
  app.add_handler(CallbackQueryHandler(button_handler))
  app.add_handler(ChatJoinRequestHandler(join_request_handler))
  app.add_error_handler(error_handler)

  print('🤖 Bot is running...')
  app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
  main()
