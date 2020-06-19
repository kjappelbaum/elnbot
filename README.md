# elnbot

Me playing around with a telegram bot to conveniently add data to the ELN and also query some chemistry information.
A fun application would be to couple it also with some online analysis (e.g. image recognition) or integrate it with lab automation.

t.me/epfl_eln_bot

## How to run it

For simple testing without upload on EPFL internal servers, one can host it on [glitch](https://glitch.com/).
If the upload to the samba share for images is needed, it is important to have the corresponding share mounted in the filesystem of the server which is running the bot.

Environmental variables that need to be set:

- `TELEGRAM_TOKEN`: Telegram token for the bot.
- `IMAGE_STORAGE_PATH`: Path at which the samba share for image upload is mounted.

## ToDo:

- [ ] Add more functioanlities from the ELN API
- [ ] Test with more concurrent requests
- [ ] Permanently host on EPFL servers
