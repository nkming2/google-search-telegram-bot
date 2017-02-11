import telepot
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, \
		InlineQueryResultPhoto
import uuid

from app.custom_search_api import CustomSearchApi
from app.lazy import Lazy
from app.log import Log
from app.config_loader import ConfigLoader

## Throw when used in channel
class _ChanelException(Exception):
	pass

## Throw when user initiating the bot is not whitelisted
class _WhitelistException(Exception):
	pass

class _QueryHandler():
	def __init__(self, text):
		self._text = text

	@Lazy
	def filtered_text(self):
		if self.is_image:
			return self._text[len("image"):].strip()
		else:
			return self._text

	@Lazy
	def is_image(self):
		return self._text.lower().startswith("image")

	@Lazy
	def is_empty(self):
		import re
		# Remove all symbols and see if anything left
		characters = re.sub(r"[\t\n ./<>?;:\"'`!@#$%\^&*()\[\]{}_+=|\\-]", "",
				self.filtered_text)
		return not characters

	@Lazy
	def request_args(self):
		args = {
			"q": self.filtered_text,
		}
		if self.is_image:
			args["searchType"] = "image"
		return args

## Bot logic when it's called in an inline mannar
class _InlineMessageBaseHandler():
	RESPONSE_EXCEPTION = [InlineQueryResultArticle(id = str(uuid.uuid4()),
			title = "Error",
			description = "Ehmm... I feel like I'm sick, mind contacting my parents about this?",
			url = "https://github.com/nkming2/google-search-telegram-bot",
			input_message_content = InputTextMessageContent(
					message_text = "Sorry, no results could be provided. Mind contacting my parents about this (with a screenshot of our conversation if you don't mind) at https://github.com/nkming2/google-search-telegram-bot ?"))]
	RESPONSE_NO_RESULTS = [InlineQueryResultArticle(id = str(uuid.uuid4()),
			title = "No results found! \u2639",
			input_message_content = InputTextMessageContent(
					message_text = "No results found! \u2639"))]
	RESPONSE_NO_MORE_QUOTA = [InlineQueryResultArticle(id = str(uuid.uuid4()),
			title = "Google rejected me \U0001F494",
			description = "You may have run out of your daily quota",
			input_message_content = InputTextMessageContent(
					message_text = "Sorry, no results could be provided"))]
	RESPONSE_DISALLOWED_USER = {
		"results": [],
		"switch_pm_text": "Please click here to start a private chat with me first",
	}

	def __init__(self, bot, msg):
		self._bot = bot
		self._msg = msg

	def _do_handle(self):
		Log.v(self._msg)
		query = _QueryHandler(self._glance["query_string"])
		if query.is_empty:
			return []
		try:
			response = CustomSearchApi().list(**query.request_args)
		except CustomSearchApi.NetworkError as e:
			Log.e("Failed while list %d: %s" % (e.status_code, e.message))
			if e.status_code == 403:
				return self.RESPONSE_NO_MORE_QUOTA
			else:
				raise e
		if not response or "items" not in response:
			return self.RESPONSE_NO_RESULTS

		if query.is_image:
			return self._build_image_response(response)
		else:
			return self._build_text_response(response)

	def _build_text_response(self, response):
		results = []
		for it in response["items"]:
			msg = "%s" % _format_msg(it)
			results += [InlineQueryResultArticle(
					id = self._build_result_id(it["link"]),
					title = it["title"],
					description = it["snippet"],
					input_message_content = InputTextMessageContent(
							message_text = msg,
							parse_mode = "Markdown"),
					url = it["link"])]
		return results if results else self.RESPONSE_NO_RESULTS

	def _build_image_response(self, response):
		results = []
		for it in response["items"]:
			image = it["image"]
			results += [InlineQueryResultPhoto(
					id = self._build_result_id(it["link"]),
					photo_url = it["link"],
					thumb_url = image["thumbnailLink"],
					photo_width = image["width"],
					photo_height = image["height"],
					title = it["title"],
					description = it["snippet"])]
		return results if results else self.RESPONSE_NO_RESULTS

	def _ensure_allowed_users(self):
		_ensure_allowed_users(self._msg["from"])

	@Lazy
	def _glance(self):
		query_id, from_id, query_string = telepot.glance(self._msg,
				flavor = "inline_query")
		return {
			"query_id": query_id,
			"from_id": from_id,
			"query_string": query_string,
		}

	def _build_result_id(self, url):
		import hashlib
		return hashlib.sha256(url.encode("utf-8")).hexdigest()

## Inline handler for normal use
class InlineMessageHandler(_InlineMessageBaseHandler):
	def __init__(self, bot, answerer, msg):
		super().__init__(bot, msg)
		self._answerer = answerer

	def handle(self):
		def _callback():
			try:
				self._ensure_allowed_users()
				return self._do_handle()
			except _WhitelistException as e:
				Log.i("Disallowed user (%s) is chating with us"
						% self._msg["from"]["first_name"])
				return self.RESPONSE_DISALLOWED_USER
			except Exception as e:
				Log.e("Failed while _do_handle", e)
				return self.RESPONSE_EXCEPTION
		self._answerer.answer(self._msg, _callback)

## Inline handler that doesn't use thread (Answerer). This would likely results
#  in more meaningless requests. Only intended for PAW use as they have disabled
#  threading support
class InlineMessageNoThreadHandler(_InlineMessageBaseHandler):
	def handle(self):
		try:
			self._ensure_allowed_users()
			response = self._do_handle()
		except _WhitelistException as e:
			Log.i("Disallowed user (%s) is chating with us"
					% self._msg["from"]["first_name"])
			response = self.RESPONSE_DISALLOWED_USER
		except Exception as e:
			Log.e("Failed while _do_handle", e)
			response = self.RESPONSE_EXCEPTION

		if isinstance(response, list):
			self._bot.answerInlineQuery(self._glance["query_id"], response)
		elif isinstance(response, tuple):
			self._bot.answerInlineQuery(self._glance["query_id"], *response)
		elif isinstance(response, dict):
			self._bot.answerInlineQuery(self._glance["query_id"], **response)
		else:
			raise ValueError("Invalid response format")

## Bot logic when it's called in a private chat
class MessageHandler():
	RESPONSE_NON_TEXTUAL_INPUT = "Sorry I can only read text \U0001F62E"
	RESPONSE_EXCEPTION = "Ehmm... I feel like I'm sick \U0001F635 Mind contacting my parents about this (with a screenshot of our conversation if you don't mind) at https://github.com/nkming2/google-search-telegram-bot ?"
	RESPONSE_NO_RESULTS = "No results found! \u2639"
	RESPONSE_HI_TEMPLATE = "Hi there \U0001F44B\U0001F600 You can initiate a search by typing your query here, or using the inline syntax @%s [SEARCH_QUERY...] in your other chats. You can also start an image search by beginning your search query with \"image\"\n\nThis bot is open source! Visit us at https://github.com/nkming2/google-search-telegram-bot"
	RESPONSE_UNKNOWN_CMD = "Ehmm I don't quite undertand \U0001F914"
	RESPONSE_NO_MORE_QUOTA = "Google has rejected my search request. \u2639 You may have run out of your daily Custom Search quota"
	RESPONSE_MD_DISALLOWED_USER = "Sorry, due to a *very limited* Search API usage quota imposed by Google, I could only serve a small amount of audience.\n\n*However, I am open source and you could easily host me with your own API key*. Visit my home for more details at https://github.com/nkming2/google-search-telegram-bot"

	def __init__(self, bot, msg):
		self._bot = bot
		self._msg = msg

	def handle(self):
		try:
			self._ensure_supported_chat()
			self._ensure_allowed_users()
			self._do_handle()
		except _ChanelException as e:
			pass
		except _WhitelistException as e:
			Log.i("Disallowed user (%s) is chating with us"
					% self._msg["from"]["first_name"])
			self._bot.sendMessage(self._glance["chat_id"],
					self.RESPONSE_MD_DISALLOWED_USER, parse_mode = "Markdown")
		except Exception as e:
			Log.e("Failed while _do_handle", e)
			self._bot.sendMessage(self._glance["chat_id"],
					self.RESPONSE_EXCEPTION)

	class _TextResponse():
		def __init__(self, content, type = "Markdown"):
			self._content = content
			self._type = type

		def send(self, bot, chat_id):
			args = {
				"chat_id": chat_id,
				"text": self._content,
			}
			if self._type:
				args["parse_mode"] = self._type
			bot.sendMessage(**args)

	class _ImageResponse():
		def __init__(self, image, caption = None):
			self._image = image
			self._caption = caption

		def send(self, bot, chat_id):
			args = {
				"chat_id": chat_id,
				"photo": self._image,
			}
			if self._caption:
				args["caption"] = self._caption
			bot.sendPhoto(**args)

	def _do_handle(self):
		Log.v(self._msg)
		if self._glance["content_type"] == "text":
			if self._msg["text"].startswith("/"):
				self._handle_command(self._msg["text"])
			else:
				self._handle_text(self._msg["text"])
		else:
			self._bot.sendMessage(self._glance["chat_id"],
					self.RESPONSE_NON_TEXTUAL_INPUT)

	def _handle_command(self, text):
		if text == "/start":
			self._bot.sendMessage(self._glance["chat_id"],
					self.RESPONSE_HI_TEMPLATE % self._bot.getMe()["username"])
		else:
			self._bot.sendMessage(self._glance["chat_id"],
					self.RESPONSE_UNKNOWN_CMD)

	def _handle_text(self, text):
		response = self._build_response(text)
		if isinstance(response, list):
			for r in response:
				r.send(self._bot, self._glance["chat_id"])
		else:
			response.send(self._bot, self._glance["chat_id"])

	def _build_response(self, text):
		query = _QueryHandler(text)
		if query.is_empty:
			return self._TextResponse(self.RESPONSE_NO_RESULTS)
		try:
			response = CustomSearchApi().list(**query.request_args)
		except CustomSearchApi.NetworkError as e:
			Log.e("Failed while list %d: %s" % (e.status_code, e.message))
			if e.status_code == 404:
				return self._TextResponse(self.RESPONSE_NO_MORE_QUOTA)
			else:
				raise e
		if not response or "items" not in response:
			return self._TextResponse(self.RESPONSE_NO_RESULTS)

		if query.is_image:
			return self._build_image_response(response)
		else:
			return self._build_text_response(response)

	def _build_text_response(self, response):
		msg = ""
		for i, it in enumerate(response["items"]):
			if i > 2:
				break
			msg += "%s\n\n" % _format_msg(it)
		return self._TextResponse(msg.strip() if msg else \
				self.RESPONSE_NO_RESULTS)

	def _build_image_response(self, response):
		responses = []
		for i, it in enumerate(response["items"]):
			if i > 2:
				break
			responses += [self._ImageResponse(it["link"], caption = it["title"])]
		return responses if responses else \
				self._TextResponse(self.RESPONSE_NO_RESULTS)

	def _ensure_supported_chat(self):
		if "from" not in self._msg:
			raise _ChanelException()

	def _ensure_allowed_users(self):
		_ensure_allowed_users(self._msg["from"])

	@Lazy
	def _glance(self):
		content_type, chat_type, chat_id = telepot.glance(self._msg)
		return {
			"content_type": content_type,
			"chat_type": chat_type,
			"chat_id": chat_id,
		}

def _markdown_escape(str):
	import re
	return re.sub(r"([*_#\[\]<>])", r"\\\1", str)

def _format_msg(cse_item):
	title = _markdown_escape(cse_item["title"])
	snippet = _markdown_escape(cse_item["snippet"].replace("\n", ""))
	link = _markdown_escape(cse_item["link"])
	return "*%s*\n%s\n%s" % (title, snippet, link)

def _ensure_allowed_users(user):
	allows = ConfigLoader.load("allow_only_users")
	if not allows:
		# Empty list == allow all
		return
	# Allow if either id or username is whitelisted
	if user["id"] in allows:
		return
	elif "username" in user and user["username"] in allows:
		return
	else:
		raise _WhitelistException()
