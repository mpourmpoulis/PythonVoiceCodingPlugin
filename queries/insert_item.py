from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery



class InsertItem(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		collection = state["collection"]
		item = collection[query_description["item_index"]-1]
		selection = self._get_selection(view_information,extra)
		selection = selection if isinstance(selection,list) else [selection]
		return [(x,item)  for x in selection]







