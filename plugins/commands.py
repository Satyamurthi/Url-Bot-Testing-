import os
import time
import psutil
import shutil
import string
import asyncio
from presets import Presets
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from helper_funcs.support import users_info
from helper_funcs.sql import add_user, query_msg

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
    
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message


# ------------------------------- Start Message --------------------------------- #

@Client.on_message(filters.command(["start"]) & filters.private)
async def start(bot, update):
    await update.reply_text(
        text=Translation.START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=Translation.START_BUTTONS
    )
    
# ------------------------------- Help Message --------------------------------- #

@Client.on_message(filters.command(["help"]) & filters.private)
async def help_user(bot, update):
    await update.reply_text(
        text=Translation.HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.HELP_BUTTONS
    )

# ------------------------------- About Message --------------------------------- #

@Client.on_message(filters.command(["about"]) & filters.private)
async def get_me_info(bot, update):
    await update.reply_text(
        text=Translation.ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.ABOUT_BUTTONS
    )
    
# ------------------------------- Broadcast Message --------------------------------- #
    
@Client.on_message(filters.private & filters.command('broadcast'))
async def send_text(bot, m: Message):
    id = m.from_user.id
    if id not in Config.AUTH_USERS:
        return
    if (" " not in m.text) and ("broadcast" in m.text) and (m.reply_to_message is not None):
        query = await query_msg()
        for row in query:
            chat_id = int(row[0])
            try:
                await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=m.chat.id,
                    message_id=m.reply_to_message.message_id,
                    caption=m.caption,
                    reply_markup=m.reply_markup
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception:
                pass
    else:
        msg = await m.reply_text(Presets.REPLY_ERROR, m.message_id)
        await asyncio.sleep(8)
        await msg.delete()
        
# ------------------- ** END ** ------------------- #
