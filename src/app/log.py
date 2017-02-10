import logging
import traceback

def _build_logger():
	product = logging.getLogger(__name__)
	product.setLevel(1)
	handler = logging.StreamHandler()
	handler.setLevel(1)
	handler.setFormatter(logging.Formatter("%(asctime)s\n%(message)s"))
	product.addHandler(handler)
	return product

class Log():
	@staticmethod
	def wtf(msg, e = None):
		if e:
			Log._log.critical("WTF %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.critical("WTF %s\n\tFile \"%s\", line %d, in %s" % (msg,
					src[0], src[1], src[2]))

	@staticmethod
	def e(msg, e = None):
		if e:
			Log._log.error("ERROR %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.error("ERROR %s\n\tFile \"%s\", line %d, in %s" % (msg,
					src[0], src[1], src[2]))

	@staticmethod
	def w(msg, e = None):
		if e:
			Log._log.warning("WARN %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.warning("WARN %s\n\tFile \"%s\", line %d, in %s" % (msg,
					src[0], src[1], src[2]))

	@staticmethod
	def i(msg, e = None):
		if e:
			Log._log.info("INFO %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.info("INFO %s\n\tFile \"%s\", line %d, in %s" % (msg, src[0],
					src[1], src[2]))

	@staticmethod
	def d(msg, e = None):
		if e:
			Log._log.debug("DEBUG %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.debug("DEBUG %s\n\tFile \"%s\", line %d, in %s" % (msg,
					src[0], src[1], src[2]))

	@staticmethod
	def v(msg, e = None):
		if e:
			Log._log.log(logging.DEBUG - 1,
					"VERBOSE %s\n%s" % (msg, traceback.format_exc()))
		else:
			src = traceback.extract_stack(limit = 2)[0]
			Log._log.log(logging.DEBUG - 1,
					"VERBOSE %s\n\tFile \"%s\", line %d, in %s" % (msg, src[0],
							src[1], src[2]))

	_log = _build_logger()
