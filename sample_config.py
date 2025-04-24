import os

class Config(object):

    # get a token from @BotFather
    TG_BOT_TOKEN = "7982317461:AAG7lVec938tpdPm9MKG95N_XWPr95OR-yU"

    # The Telegram API things
    # Get these values from my.telegram.org
    APP_ID = "22136772"
    API_HASH = "7541e5b6d298eb1f60dac89aae92868c"

    # Array to store users who are authorized to use the bot
    AUTH_USERS = "8083702486"

    # Ban Unwanted Members..
    BANNED_USERS = []

    # the download location, where the HTTP Server runs
    DOWNLOAD_LOCATION = "./DOWNLOADS"

    # Telegram maximum file upload size
    TG_MAX_FILE_SIZE = 2097152000

    # chunk size that should be used with requests
    CHUNK_SIZE = 128

    # Generate screenshots for file after uploading
    # Defaults to True
    SCREENSHOTS = os.environ.get("SCREENSHOTS", "True")

    # default thumbnail to be used in the videos
    DEF_THUMB_NAIL_VID_S = os.environ.get("DEF_THUMB_NAIL_VID_S", "http://postimg.cc/xJ0PQTTG")

    # proxy for accessing youtube-dl in GeoRestricted Areas
    # Get your own proxy from https://github.com/rg3/youtube-dl/issues/1091#issuecomment-230163061
    HTTP_PROXY = os.environ.get("HTTP_PROXY", "")

    # maximum message length in Telegram
    MAX_MESSAGE_LENGTH = 4096

    # set timeout for subprocess
    PROCESS_MAX_TIMEOUT = 3600

    # watermark file
    DEF_WATER_MARK_FILE = ""

    # Sql Database url
    DB_URI = "mongodb+srv://mrprincebotx:mrprincebotx@cluster0.ikmilh0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
