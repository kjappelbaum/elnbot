# import required libraries
import telebot
import requests
from os import environ

# setup bot with Telegram token from .env
bot = telebot.TeleBot(environ["TELEGRAM_TOKEN"])

bot_text = """
Hello, how are you doing?

This bot helps you using the ELN. For the start, I need your GASPAR name to be able to deposit data for you. 
"""

bot_commands = """
Commands:
- /random -> random picture (for testing and fun)
- /search -> get some search results to some topic
- /ui -> upload image of your MOF to the lab notebook, please use white background
- /eln -> open the ELN 
"""

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

if __name__ == "__main__":
    bot.polling(none_stop=True)
