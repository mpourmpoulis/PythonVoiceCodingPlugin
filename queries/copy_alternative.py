from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery, no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection,result_alternatives_sequence


@no_build_attempt
class CopyAlternative(SelectionQuery):
	"""docstring for SelectAlternative"""

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)
		
	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		if state["mode"] != "single":
			return 
		candidates = result_alternatives_sequence(state,text=True) # get only the text
		result = decode_item_selection(candidates,query_description,"individual","color",decrement=False)
		if result:
			self._register_for_external(clipboard = result[0])
		return None,None


