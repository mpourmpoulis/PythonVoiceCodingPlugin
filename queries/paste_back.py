from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 

@no_build_attempt
class PasteBack(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		print(" inside query",state,"\n")
		print("origin\n\n",state["origin"],"\n\n")
		history  =  extra["history"]
		index = len(history)
		# while history[index-1][0]=="selection"  and index>=1 and history[index-1][1]  == view_information["change_count"]:
			# index -=1
		# if index==len(history) or history[index][1] != view_information["change_count"]:
			# return []
		candidates = result_alternatives_sequence(state,text = True)
		candidates_location = result_alternatives_sequence(state,location = True)
		if query_description["format"]==1:
			# selection = history[index][2]
			selection = state["origin"]
			selection = selection if isinstance(selection,list) else [selection]
		if query_description["format"]==2:
			selection = {candidates_location[query_description["color"+i]]  
							for i in ["2","3","4"] if "color"+i in query_description}
		output = candidates[query_description.get("color",0)]
		surrounding = query_description.get("surrounding_punctuation",("",""))
		return [(x,surrounding[0]+output+surrounding[1])  for x in selection]







