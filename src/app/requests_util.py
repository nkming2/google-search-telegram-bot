import requests

class _RequestOp():
	def __init__(self, url, **kwargs):
		self._url = url
		self._kwargs = kwargs
		self._response = None

	def __enter__(self):
		self._response = self._do_request(self._url, **self._kwargs)
		return self._response

	def __exit__(self, exc_type, exc_value, traceback):
		if self._response:
			self._response.close()

	def _do_request(self, url, **kwargs):
		return None

class _RequestGet(_RequestOp):
	def __init__(self, url, **kwargs):
		super().__init__(url, **kwargs)

	def _do_request(self, url, headers = None, **kwargs):
		headers_ = {"Connection": "close"}
		if headers:
			headers_.update(headers)
		return requests.get(url, headers = headers_, **kwargs)

class _RequestPost(_RequestOp):
	def __init__(self, url, **kwargs):
		super().__init__(url, **kwargs)

	def _do_request(self, url, headers = None, **kwargs):
		headers_ = {"Connection": "close"}
		if headers:
			headers_.update(headers)
		return requests.post(url, headers = headers_, **kwargs)

def http_request(method, url, **kwargs):
	method_ = method.lower()
	if method_ == "get":
		return _RequestGet(url, **kwargs)
	elif method_ == "post":
		return _RequestPost(url, **kwargs)
	else:
		raise RuntimeError("Method not supported yet: %s" % method)
