from noob.queries.abstract import SelectionQuery, no_build_attempt

@no_build_attempt
class SelectAlternative(SelectionQuery):
	"""docstring for SelectAlternative"""
	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		alternatives = state["alternatives"]
		if "alternative_index" in query_description:
			index = query_description["alternative_index"]
		elif "color" in query_description:
			index = query_description["color"]
		else:
			return None,None
		index=index-1
		if len(alternatives)>index:
			return alternatives[index],[]
		else:
			return None,None


