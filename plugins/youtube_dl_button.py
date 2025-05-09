import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import asyncio
import json
import os
import shutil
import time

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from datetime import datetime
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from pyrogram.types import InputMediaPhoto

from translation import Translation
from helper_funcs.database import thumb
from helper_funcs.help_Nekmo_ffmpeg import generate_screen_shots
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes

from PIL import Image


async def youtube_dl_call_back(bot, update):
    cb_data = update.data
    tg_send_type, youtube_dl_format, youtube_dl_ext = cb_data.split("|")

    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".json"
    try:
        with open(save_ytdl_json_path, "r", encoding="utf8") as f:
            response_json = json.load(f)
    except (FileNotFoundError) as e:
        await bot.delete_messages(
            chat_id=update.message.chat.id,
            message_ids=update.message.message_id,
            revoke=True
        )
        return False
    youtube_dl_url = update.message.reply_to_message.text
    custom_file_name = str(response_json.get("title")) + \
        "_" + youtube_dl_format + "." + youtube_dl_ext
    youtube_dl_username = None
    youtube_dl_password = None
    if "|" in youtube_dl_url:
        url_parts = youtube_dl_url.split("|")
        if len(url_parts) == 2:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
        elif len(url_parts) == 4:
            youtube_dl_url = url_parts[0]
            custom_file_name = url_parts[1]
            youtube_dl_username = url_parts[2]
            youtube_dl_password = url_parts[3]
        else:
            for entity in update.message.reply_to_message.entities:
                if entity.type == "text_link":
                    youtube_dl_url = entity.url
                elif entity.type == "url":
                    o = entity.offset
                    l = entity.length
                    youtube_dl_url = youtube_dl_url[o:o + l]
        if youtube_dl_url is not None:
            youtube_dl_url = youtube_dl_url.strip()
        if custom_file_name is not None:
            custom_file_name = custom_file_name.strip()
        if youtube_dl_username is not None:
            youtube_dl_username = youtube_dl_username.strip()
        if youtube_dl_password is not None:
            youtube_dl_password = youtube_dl_password.strip()

    else:
        for entity in update.message.reply_to_message.entities:
            if entity.type == "text_link":
                youtube_dl_url = entity.url
            elif entity.type == "url":
                o = entity.offset
                l = entity.length
                youtube_dl_url = youtube_dl_url[o:o + l]
    await bot.edit_message_text(
        text=f"<b> Trying to download your file... </b>",
        chat_id=update.message.chat.id,
        message_id=update.message.message_id
    )
    description = Translation.CUSTOM_CAPTION_UL_FILE
    if "fulltitle" in response_json:
        description = response_json["fulltitle"][0:1021]
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + custom_file_name
    command_to_exec = []
    if tg_send_type == "audio":
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--prefer-ffmpeg",
            "--extract-audio",
            "--audio-format", youtube_dl_ext,
            "--audio-quality", youtube_dl_format,
            youtube_dl_url,
            "-o", download_directory
        ]
    else:
        minus_f_format = youtube_dl_format
        if "youtu" in youtube_dl_url:
            minus_f_format = youtube_dl_format + "+bestaudio"
        command_to_exec = [
            "youtube-dl",
            "-c",
            "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
            "--embed-subs",
            "-f", minus_f_format,
            "--hls-prefer-ffmpeg", youtube_dl_url,
            "-o", download_directory
        ]
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    if youtube_dl_username is not None:
        command_to_exec.append("--username")
        command_to_exec.append(youtube_dl_username)
    if youtube_dl_password is not None:
        command_to_exec.append("--password")
        command_to_exec.append(youtube_dl_password)
    command_to_exec.append("--no-warnings")
    if "hotstar" in youtube_dl_url:
        command_to_exec.append("--geo-bypass-country")
        command_to_exec.append("IN")

    start = datetime.now()
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    # logger.info(e_response)
    # logger.info(t_response)
    ad_string_to_replace = f"<b> please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output. </b>"
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await bot.edit_message_text(
            chat_id=update.message.chat.id,
            message_id=update.message.message_id,
            text=error_message
        )
        return False
    if t_response:
        try:
            os.remove(save_ytdl_json_path)
        except:
            pass
        end_one = datetime.now()
        time_taken_for_download = (end_one -start).seconds
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            try:
                download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
                file_size = os.stat(download_directory).st_size
            except Exception as e:
                await bot.edit_message_text(
                    chat_id=update.message.chat.id,
                    text=f"<b> Some errors occured while downloading video! </b>",
                    message_id=update.message.message_id
                )
                logger.info("FnF error - " + str(e))
                return
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.message.chat.id,
                text=f"""<b> Downloaded in {time_taken_for_download} seconds.\nDetected File Size: {humanbytes(file_size)}
Sorry. But, I cannot upload files greater than 1.95GB due to Telegram API limitations. </b>""",
                message_id=update.message.message_id
            )
        else:
            if Config.SCREENSHOTS=="True":
                is_w_f = False
                images = await generate_screen_shots(
                    download_directory,
                    tmp_directory_for_each_user,
                    is_w_f,
                    Config.DEF_WATER_MARK_FILE,
                    300,
                    9
                )

            await bot.edit_message_text(
                text=f"<b> Uploading now.. </b>",
                chat_id=update.message.chat.id,
                message_id=update.message.message_id
            )
            # get the correct width, height, and duration for videos greater than 10MB
            width = 0
            height = 0
            duration = 0
            if tg_send_type != "file":
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None:
                    if metadata.has("duration"):
                        duration = metadata.get('duration').seconds

            thumb_image_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + ".jpg"

            if not os.path.exists(thumb_image_path):
                mes = await thumb(update.from_user.id)
                if mes != None:
                    m = await bot.get_messages(update.message.chat.id, mes.msg_id)
                    await m.download(file_name=thumb_image_path)
                    thumb_image_path = thumb_image_path

            if os.path.exists(thumb_image_path):
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata.has("width"):
                    width = metadata.get("width")
                if metadata.has("height"):
                    height = metadata.get("height")
                if tg_send_type == "vm":
                    height = width
                Image.open(thumb_image_path).convert(
                    "RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                if tg_send_type == "file":
                    img.resize((320, height))
                else:
                    img.resize((90, height))
                img.save(thumb_image_path, "JPEG")
            else:
                thumb_image_path = None

            start_time = time.time()
            if tg_send_type == "audio":
                await bot.send_audio(
                    chat_id=update.message.chat.id,
                    audio=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    # performer=response_json["uploader"],
                    # title=response_json["title"],
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<b> Uploading now.. </b>",
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                await bot.send_document(
                    chat_id=update.message.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    parse_mode="HTML",
                    # reply_markup=reply_markup,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<b> Uploading now.. </b>",
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "vm":
                await bot.send_video_note(
                    chat_id=update.message.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<b> Uploading now.. </b>",
                        update.message,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                await bot.send_video(
                    chat_id=update.message.chat.id,
                    video=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    # reply_markup=reply_markup,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message.reply_to_message.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"<b> Uploading now.. </b>",
                        update.message,
                        start_time
                    )
                )
            else:
                logger.info("Did this happen? :\\")
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds

            media_album_p = []
            if Config.SCREENSHOTS=="True":
                if images is not None:
                    i = 0
                    caption = ""
                    if is_w_f:
                        caption = ""
                    for image in images:
                        if os.path.exists(image):
                            if i == 0:
                                media_album_p.append(
                                    InputMediaPhoto(
                                        media=image,
                                        caption=caption,
                                        parse_mode="html"
                                    )
                                )
                            else:
                                media_album_p.append(
                                    InputMediaPhoto(
                                        media=image
                                    )
                                )
                            i = i + 1
                    await bot.send_media_group(
                        chat_id=update.message.chat.id,
                        disable_notification=True,
                        reply_to_message_id=update.message.message_id,
                        media=media_album_p
                    )
            try:
                shutil.rmtree(tmp_directory_for_each_user)   
            except:
                pass
            try:
                os.remove(thumb_image_path)
            except:
                pass
            await bot.edit_message_text(
                text="""<b> Downloaded in {time_taken_for_download} seconds.
                
Uploaded in {time_taken_for_upload} seconds. </b>""",
                chat_id=update.message.chat.id,
                message_id=update.message.message_id,
                disable_web_page_preview=True
            )
