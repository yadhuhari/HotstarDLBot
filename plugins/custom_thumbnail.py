import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from pyrogram import Client, filters    

from translation import Translation
from helper_funcs.database import *


@Client.on_message(filters.private & filters.photo)
async def save_photo(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    if update.media_group_id is not None:
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + "/" + str(update.media_group_id) + "/"
        if not os.path.isdir(download_location):
            os.makedirs(download_location)
        await df_thumb(update.from_user.id, update.message_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
    else:
        download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
        await df_thumb(update.from_user.id, update.message_id)
        await bot.download_media(
            message=update,
            file_name=download_location
        )
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"""<b> Custom thumbnail saved. This will be permanent.
            
Use /deletethumbnail to clear it. </b>""",
            reply_to_message_id=update.message_id
        )


@Client.on_message(filters.private & filters.command(["deletethumbnail"]))
async def delete_thumbnail(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return
    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    
    try:
        await del_thumb(update.from_user.id)
    except:
        pass

    try:
        os.remove(thumb_image_path)
    except:
        pass

    await bot.send_message(
        chat_id=update.chat.id,
        text=f"<b> Custom thumbnail cleared succesfully. </b>",
        reply_to_message_id=update.message_id
    )

@Client.on_message(filters.private & filters.command(["showthumb"]))
async def show_thumb(bot, update):
    if update.from_user.id in Config.BANNED_USERS:
        await bot.delete_messages(
            chat_id=update.chat.id,
            message_ids=update.message_id,
            revoke=True
        )
        return

    thumb_image_path = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".jpg"
    if not os.path.exists(thumb_image_path):
        mes = await thumb(update.from_user.id)
        if mes != None:
            m = await bot.get_messages(update.chat.id, mes.msg_id)
            await m.download(file_name=thumb_image_path)
            thumb_image_path = thumb_image_path
        else:
            thumb_image_path = None    
    
    if thumb_image_path is not None:
        try:
            await bot.send_photo(
                chat_id=update.chat.id,
                photo=thumb_image_path,
                caption=f"<b> Use /deletethumbnail to clear this thumbnail. </b>"
            )
        except:
            pass
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=f"<b> No saved thumbnails Found!!\n\nSend an image to save it as your thumbnail permanently. </b>",
            reply_to_message_id=update.message_id
        )
