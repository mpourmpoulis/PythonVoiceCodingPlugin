from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt


@no_build_attempt
class PasteBack(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		history  =  extra["history"]
		index = len(history)
		while history[index-1][0]=="selection"  and index>=1 and history[index-1][1]  == view_information["change_count"]:
			index -=1
		if index==len(history) or history[index][1] != view_information["change_count"]:
			return []
		
		result_text = state["result_text"]
		alternatives_text = state["alternatives_text"]
		candidates = [result_text]+alternatives_text if alternatives_text else [result_text]
		if query_description["format"]==1:
			selection = history[index][2]
			selection = selection if isinstance(selection,list) else [selection]
		if query_description["format"]==2:
			result = state["result"]
			alternatives = state["alternatives"]
			candidates_location = [result]+alternatives if alternatives else [result]
			selection = {candidates_location[query_description["color"+i]]  
							for i in ["2","3","4"] if "color"+i in query_description}
		output = candidates[query_description.get("color",0)]
		surrounding = query_description.get("surrounding_punctuation",("",""))
		return [(x,surrounding[0]+output+surrounding[1])  for x in selection]







