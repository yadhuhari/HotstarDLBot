import os
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

force_channel = "AstroverseTG"

@Client.on_message(filters.command(["upgrade"]))
async def upgrade(bot, update):
    await bot.send_message(
        chat_id=update.chat.id,
        text=f"""<b> 👉 If You Liked Our Bots And Service Feel Free To Donate...🥰

  If You Want Any Private Bot Or Supscription Feel Free To Contact Me...@YadhuTG... </b>""",
        parse_mode="html",
        reply_to_message_id=update.message_id,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("start"))
async def start(client, message):
    if force_channel:
        try:
            user = await client.get_chat_member(force_channel, message.from_user.id)
            if user.status == "kicked out":
                await message.reply_text("You Are Banned")
                return
        except UserNotParticipant :
            await message.reply_text(
                text=f"<b> You are not authorised to use this bot..! </b>")
            return
    await message.reply_photo(
        photo="http://postimg.cc/xJ0PQTTG",
        caption=f"""<b> Hey There {message.from_user.mention} 👋,

I am a Hotstar DL Bot, Just Send Me any Hotstar URL and I'll Upload File Remotely to Telegram.

🔒 Subscription required for usage.

⚜ Maintained By : @AstroverseTG </b>""",
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton("📣 Updates", url="t.me/AstroverseTG"),
            InlineKeyboardButton("👥 Support", url="t.me/AstroverseTG")
            ]]
            )
        )

@Client.on_message(filters.command("about"))
async def about(client, message):
    await message.reply_photo(
        photo="http://postimg.cc/xJ0PQTTG",
        caption=f"""<b> Hey There {message.from_user.mention} 👋,

⍟ My Name : Live Recorder Bot
⍟ Owner : @YadhuTG
⍟ Updates Channel : @AstroverseTG
⍟ Language : Python3
⍟ Library : Pyrogram
⍟ Server : Koyeb

⚜ Maintained By : @AstroverseTG </b>""",
        reply_markup=InlineKeyboardMarkup( [[
            InlineKeyboardButton("📣 Updates", url="t.me/AstroverseTG"),
            InlineKeyboardButton("👥 Support", url="t.me/AstroverseTG")
            ]]
            )
        ) 
