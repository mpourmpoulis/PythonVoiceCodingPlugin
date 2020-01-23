from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery, no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection,result_alternatives_sequence


@no_build_attempt
class SelectAlternative(SelectionQuery):
	"""docstring for SelectAlternative"""

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)
		
	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		print("state:\n",state)
		candidates = result_alternatives_sequence(state,location=True)
		print("candidates:\n",candidates)
		if "alternative_index" in query_description:
			name="alternative_index"
		elif "color" in query_description:
			name = "color"
		else:
			return None,None
		if state["mode"]=="single":
			result = decode_item_selection(candidates,query_description,"individual",name,decrement=False)
			if len(result)==1:
				result = result[0]
		else:
			result = [decode_item_selection(x,query_description,"individual",name,decrement=False) for x in candidates]
			selection =self._get_selection(view_information,extra)
			if not isinstance(selection,list) or len(selection)==1:
				try : 
					result = make_flat(result)
				except :
					pass
			print("result is ",result)
		return result, []


