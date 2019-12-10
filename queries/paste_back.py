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
		selection = history[index][2]
		selection = selection if isinstance(selection,list) else [selection]
		i = query_description.get("color",0)
		print(" i.e.'s",i)
		result_text = state["result_text"]
		alternatives_text = state["alternatives_text"]
		output = alternatives_text[i-1] if i != 0 else result_text
		surrounding = query_description.get("surrounding_punctuation",("",""))
		print("output",output)
		return [(x,surrounding[0]+output+surrounding[1])  for x in selection]







