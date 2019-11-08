from noob.library.partial import partially_parse

class Query():
	"""docstring for Query"""
	def __init__(self, code,latest_build = None):
		self.code = code
		self.general_build = latest_build
		self.attempt_build()


	def __call__(self,view_information,query_description,extra = {}):
		pass

	def get_the_latest_build(self):
		return self.general_build

	def attempt_build(self):
		if self.general_build is None:
			self.general_build = partially_parse(self.code)

	def _get_selection(self,view_information,extra = {}):
		return extra["selection"] if "selection" in extra else view_information["selection"]

def no_build_attempt(cls):
	cls.attempt_build = lambda x: None
	return cls






		









