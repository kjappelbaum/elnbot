# import required libraries
import telebot
import requests
from os import environ
import os
import urllib
from functools import partial

# setup bot with Telegram token from .env
bot = telebot.TeleBot(environ["TELEGRAM_TOKEN"])

bot_text = """
Hello, how are you doing?

This bot helps you using the ELN. For the start 🚀, I need your GASPAR name to be able to deposit data for you. 
"""

bot_commands = """
*Commands:*
- /random -> random picture (for testing and fun) 🎉
- /search -> get some search results to some topic 🔍
- /ui -> upload image of your MOF to the lab notebook, please use white background
- /eln -> open the ELN 💻 
"""

RESULT_STORAGE_PATH = "tmp"
GASPAR = None  # should probably use some kind of session handling for this.

# Handler triggered with the /start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, bot_text)
    cid = message.chat.id
    msggaspar = bot.send_message(cid, "Type the GASPAR:")
    bot.register_next_step_handler(msggaspar, get_gaspar)


def get_gaspar(message):
    global GASPAR
    GASPAR = message.text
    cid = message.chat.id
    bot.send_message(cid, "Thank you, these are the commands I know")
    bot.send_message(cid, bot_commands)


# send random unsplash picture
@bot.message_handler(commands=["random"])
def send_random_pic(message):
    response = requests.get("https://source.unsplash.com/random")
    bot.send_photo(message.chat.id, response.content)


# Handle duckduckgo searches
@bot.message_handler(commands=["search"])
def handle_search(message):
    cid = message.chat.id
    msgQuery = bot.send_message(cid, "Type the query")
    bot.register_next_step_handler(msgQuery, search)


def search(message):
    # wrapping in try:except to catch unexpected errors, for example: JSONDecodeError
    try:
        response = requests.get(
            "http://api.duckduckgo.com/", params={"q": message.text, "format": "json"}
        ).json()
        text = response.get("AbstractText")
        image_url = response.get("Image")
        related_topics_text = response.get("RelatedTopics")[0]["Text"]
        related_topics_icon = response.get("RelatedTopics")[0]["Icon"]["URL"]
        related_topics_full_link = response.get("RelatedTopics")[0]["FirstURL"]
    except:
        bot.send_message(message.from_user.id, "No results")
        return
    if not text:
        bot.send_message(message.from_user.id, related_topics_text)
        bot.send_message(message.from_user.id, related_topics_full_link)
        bot.send_photo(message.from_user.id, related_topics_icon)
    bot.send_message(message.from_user.id, text)
    bot.send_photo(message.from_user.id, image_url)


# configure the webhook for the bot, with the url of the Glitch project
bot.set_webhook(
    "https://{}.glitch.me/{}".format(environ["PROJECT_NAME"], environ["TELEGRAM_TOKEN"])
)


@bot.message_handler(content_types=["photo"])
def handle_image(message):
    image_id = message.photo[-1].file_id
    cid = message.chat.id
    image_name = save_image_from_message(message)
    cleanup_remove_image(image_name)
    msgQuery = bot.send_message(cid, "Type the sample name")
    next_funct = partial(upload_image, image_name=image_name)
    bot.register_next_step_handler(msgQuery, next_funct)


def upload_image(message, image_name=None):
    filename = GASPAR + "_" + message.text
    cid = message.chat.id
    bot.send_message(cid, "🔥 Uploading image 🔥")

    cleanup_remove_image(image_name)


def save_image_from_message(message):
    cid = message.chat.id

    image_id = get_image_id_from_message(message)

    # prepare image for downlading
    file_path = bot.get_file(image_id).file_path

    # generate image download url
    image_url = "https://api.telegram.org/file/bot{0}/{1}".format(
        environ["TELEGRAM_TOKEN"], file_path
    )

    # create folder to store pic temporary, if it doesnt exist
    if not os.path.exists(RESULT_STORAGE_PATH):
        os.makedirs(RESULT_STORAGE_PATH)

    # retrieve and save image
    image_name = "{0}.jpg".format(image_id)
    urllib.request.urlretrieve(
        image_url, "{0}/{1}".format(RESULT_STORAGE_PATH, image_name)
    )

    return image_name


def get_image_id_from_message(message):
    # there are multiple array of images, check the biggest
    return message.photo[len(message.photo) - 1].file_id


@bot.message_handler(commands=["ui"])
def handle_search(message):
    cid = message.chat.id
    msgQuery = bot.send_message(cid, "Select your image")
    bot.register_next_step_handler(msgQuery, handle_image)


def cleanup_remove_image(image_name):
    os.remove("{0}/{1}".format(RESULT_STORAGE_PATH, image_name))


if __name__ == "__main__":
    bot.polling(none_stop=True)
