import telepot

from app.config_loader import ConfigLoader
from app.log import Log
from app.message_handler import MessageHandler, InlineMessageHandler

class StandaloneApp():
	TELEGRAM_TOKEN = ConfigLoader.load("telegram_bot_token")

	def __init__(self):
		Log.i("Initializing standalone app")
		self._bot = telepot.Bot(self.TELEGRAM_TOKEN)
		self._answerer = telepot.helper.Answerer(self._bot)

	def run(self):
		import time
		self._start()
		Log.i("Running...")
		while True:
			time.sleep(10)

	def _start(self):
		Log.i("Starting app")
		def _listener(msg):
			self._on_message(msg)
		def _inline_listener(msg):
			self._on_inline_message(msg)
		self._bot.setWebhook("")
		self._bot.message_loop({
			"chat": _listener,
			"inline_query": _inline_listener,
		})

	def _on_message(self, msg):
		MessageHandler(self._bot, msg).handle()

	def _on_inline_message(self, msg):
		InlineMessageHandler(self._bot, self._answerer, msg).handle()
