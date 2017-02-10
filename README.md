# Unofficial Google Search Bot for Telegram
Telegram bot (support both inline/chat) that return search results (web/image)
from Google

## How to use
You are strongly advised to host your own as Google has imposed a **100 searches
per day** limits on their API unless you start paying. As an idependent dev,
it's not something I could afford. Currently you could test the bot at
[https://telegram.me/GoogleSearchUnofficialBot], but it's only intended for
evaluation purpose due to the limited quota available. Sorry, but it has to be
like this

## Run instruction
```
git clone https://github.com/nkming2/google-search-telegram-bot
cd google-search-telegram-bot
pip install -e .
PYTHONPATH=src python3 src/app/__init__.py
```
You might want to do this in a venv env

After setting up these you'll have to fill in your API keys in config.json

### Hosting on pythonanywhere
One easy option to host the bot freely is on PAW. In your web console you should
set the source directory to src and modify the WSGI config file based on the
sample given in this repo (misc/pythonanywhere_com_wsgi.py)

## config.json
This file holds constants like API keys that should be kept outside of the repo.
config.json should be a text file of valid serialized JSON. The following fields
must be present:
- telegram_bot_token
  - Your telegram bot token. You need to obtain it via @BotFather following the
  instructions outlined at https://core.telegram.org/bots
- google_api_key
  - Your Google API key used to authenticate the Custom Search API. You need to
  obtain it using the setup tool here:
  https://console.developers.google.com/start/api?id=customsearch&credential=client_key
- search_engine_id
  - Your Search Engine ID. Create a new engine at https://cse.google.com/cse/all.
  When creating a new engine, input a random site in "Sites to search". After
  creation, click modify, then change "Search only included sites" to "Search
  the entire web" and remove the random site you just added
- allow_only_users
  - You could limit who could use the bot hosted by you. You can either
  whitelist a user by id or username. Example: [999999,"fancy_user"] would allow
  the 2 users to use your hosted bot. An empty list would allow all
- paw_app
  - Useful only when you are hosting on PAW (See
  [Hosting on pythonanywhere](#hosting-on-pythonanywhere) for more details)
  - url
    - The URL of your web app
  - webhook_secret
    - Any string, must be valid URL character

## Dependency
- Python 3 (developed and tested on 3.5)
- Telepot (https://github.com/nickoala/telepot)
