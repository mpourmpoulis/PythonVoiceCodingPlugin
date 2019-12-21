from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery, no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection

@no_build_attempt
class SelectAlternative(SelectionQuery):
	"""docstring for SelectAlternative"""
	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		alternatives = state["alternatives"]
		if "alternative_index" in query_description:
			name="alternative_index"
		elif "color" in query_description:
			name = "color"
		else:
			return None,None
		result = decode_item_selection(alternatives,query_description,"individual",name)
		if len(result)==1:
			result = result[0]
		return result, []


