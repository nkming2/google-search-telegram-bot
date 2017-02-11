from app.config_loader import ConfigLoader
from app.log import Log
from app.requests_util import http_request

class CustomSearchApi():
	API_KEY = ConfigLoader.load("google_api_key")
	SEARCH_ENGINE_ID = ConfigLoader.load("search_engine_id")
	URL = "https://www.googleapis.com/customsearch/v1"

	class NetworkError(RuntimeError):
		def __init__(self, url, status_code, message = ""):
			self.url = url
			self.status_code = status_code
			self.message = message if message else \
					"%d while requesting %s" % (status_code, url)

	def list(self, q, **kwargs):
		Log.d("Searching: %s" % q)
		if not q:
			return {}
		args = dict(kwargs)
		args.update({
			"key": self.API_KEY,
			"cx": self.SEARCH_ENGINE_ID,
			"safe": "medium",
			"q": q,
		})
		with http_request("GET", self.URL, params = args) as response:
			if response.status_code != 200:
				Log.e("Failed while list: %d" % response.status_code)
				if response.text:
					raise self.NetworkError(url = self.URL,
							status_code = response.status_code,
							message = response.text)
				else:
					raise self.NetworkError(url = self.URL,
							status_code = response.status_code)
			else:
				return response.json()
