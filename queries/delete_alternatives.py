from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt


@no_build_attempt
class DeleteAlternatives(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		result = state["result"]
		alternatives = state["alternatives"]
		candidates = [result]+alternatives if alternatives else [result]
		if query_description["format"] == 1:
			selection = {candidates[query_description["color"+i]]  
							for i in ["","2","3","4"] if "color"+i in query_description}
		return [(x,"")  for x in selection]







