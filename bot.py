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

# Handler triggered with the /start command
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, bot_text)
    cid = message.chat.id
    msggaspar = bot.send_message(cid, "Type the GASPAR:")
    bot.register_next_step_handler(msggaspar, get_gaspar)


def get_gaspar(message):
    gaspar = message.text
    cid = message.chat.id
    bot.send_message(cid, "Thank you, these are the commands I know")
    bot.send_message(cid, bot_commands)


# send random unsplash picture
@bot.message_handler(commands=["random"])
def send_random_pic(message):
    response = requests.get("https://source.unsplash.com/random")
    bot.send_photo(message.chat.id, response.content)


def step_Set_Topics(message):
    cid = message.chat.id
    topics = message.text
    response = requests.get("https://source.unsplash.com/random?{0}".format(topics))
    bot.send_photo(message.chat.id, response.content)


# configure the webhook for the bot, with the url of the Glitch project
bot.set_webhook(
    "https://{}.glitch.me/{}".format(environ["PROJECT_NAME"], environ["TELEGRAM_TOKEN"])
)

