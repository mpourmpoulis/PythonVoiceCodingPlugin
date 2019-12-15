from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 


@no_build_attempt
class DeleteAlternatives(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		candidates = result_alternatives_sequence(extra["state"],location= True)
		if query_description["format"] == 1:
			selection = {candidates[query_description["color"+i]]  
							for i in ["","2","3","4"] if "color"+i in query_description}
		return [(x,"")  for x in selection]







