from flask import Flask, request
import telepot
import urllib3

from app.config_loader import ConfigLoader
from app.log import Log
from app.message_handler import MessageHandler, InlineMessageNoThreadHandler

flask_app = None

class PawApp():
	TELEGRAM_TOKEN = ConfigLoader.load("telegram_bot_token")

	def __init__(self):
		Log.i("Initializing PAW app")
		self._init_paw_telepot()
		self._bot = telepot.Bot(self.TELEGRAM_TOKEN)

	def run(self):
		url = ConfigLoader.load("paw_app")["url"]
		secret = ConfigLoader.load("paw_app")["webhook_secret"]

		app = Flask(__name__)
		def _webhook_view():
			return self._on_webhook()
		app.add_url_rule("/%s" % secret, view_func = _webhook_view,
				methods = ["POST"])

		global flask_app
		flask_app = app

		self._bot.setWebhook("%s/%s" % (url, secret), max_connections = 1)

	def _init_paw_telepot(self):
		# You can leave this bit out if you're using a paid PythonAnywhere
		# account
		proxy_url = "http://proxy.server:3128"
		telepot.api._pools = {
			"default": urllib3.ProxyManager(proxy_url = proxy_url, num_pools = 3,
					maxsize = 10, retries = False, timeout = 30),
		}
		telepot.api._onetime_pool_spec = (urllib3.ProxyManager,
				dict(proxy_url = proxy_url, num_pools = 1, maxsize = 1,
						retries = False, timeout = 30))
		# end of the stuff that's only needed for free accounts

	def _on_webhook(self):
		update = request.get_json()
		if "message" in update:
			# message request
			MessageHandler(self._bot, update["message"]).handle()
		elif "inline_query" in update:
			# inline request
			InlineMessageNoThreadHandler(self._bot, update["inline_query"]) \
					.handle()
		return "OK"
