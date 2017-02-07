import json

## Provide access to constants kept outside of the repo. config.json should be a
#  text file holding valid serialized JSON. Refer to the readme file for more
#  info about this file
class ConfigLoader():
	@staticmethod
	def load(identifier):
		return ConfigLoader._ensure_config()[identifier]

	@staticmethod
	def _ensure_config():
		if ConfigLoader._config is None:
			with open("config.json", "r") as f:
				ConfigLoader._config = json.loads(f.read())
		return ConfigLoader._config

	_config = None
