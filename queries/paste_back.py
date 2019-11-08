from noob.queries.abstract import InsertionQuery



class PasteBack(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		history  =  extra["history"]
		code = view_information["code"]
		index = len(history)
		while history[index-1][0]=="selection"  and index>=1 and history[index-1][1]  == view_information["change_count"]:
			index -=1
		if index==len(history) or history[index][1] != view_information["change_count"]:
			return []
		selection = history[index][2]
		selection = selection if isinstance(selection,list) else [selection]
		f = query_description["format"]
		if f==1:
			i = query_description["paste_back_index"]
		elif f==2:
			i = query_description["color"]
		else:
			return []
		result = state["result"]
		alternatives = state["alternatives"]
		location = alternatives[i-1] if i != 0 else result
		location = location if isinstance(location,list) else [location]
		return [(x,code[l[0]:l[1]])  for x,l in zip(selection, location)]







