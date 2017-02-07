# See: http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
class Lazy(object):
	def __init__(self, lazy_init):
		self._lazy_init = lazy_init

	def __get__(self, instance, owner):
		if not instance:
			return None

		val = self._lazy_init(instance)
		setattr(instance, self._lazy_init.__name__, val)
		return val
