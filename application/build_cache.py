class BuildCache():
	"""docstring for BuildCache"""
	def __init__(self):
		self.cache_memory = {}
	def register_build(self,vid,change_count,build):
		self.cache_memory[vid] = (change_count,build)

	def get_build(self,vid,change_count):
		if vid not in self.cache_memory:
			return None
		data = self.cache_memory[vid]
		if change_count!= data[0]:
			return None
		return  data[1]

		