from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery, no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection,result_alternatives_sequence


@no_build_attempt
class SelectBack(SelectionQuery):
	"""docstring for SelectAlternative"""

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)
		
	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		if query_description["format"]==1:
			return state["initial_origin"],[]
		elif query_description["format"]==2:
			return state["origin"],[]

