import os
import traceback
import logging
import time
import psutil
import shutil
import string
import asyncio


from translation import Translation

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config


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
    

             # ------------------- ** END ** ------------------- #
