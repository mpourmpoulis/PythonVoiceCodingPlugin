from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt


@no_build_attempt
class InsertItem(InsertionQuery):
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["global_state"]
		collection = state["collection"]
		mode = query_description["format"]
		if mode==1:
			item = collection[query_description["item_index"]-1]
		elif mode==2:
			print(mode,query_description)
			item_range = (query_description["item_index"]-1, query_description.get("item_index2"))
			item = ",".join(collection[item_range[0]:item_range[1]])
		elif mode==3:
			item = []
			for i in ["","2","3","4"]:
				index =  query_description.get("item_index"+i)
				if index:
					item.append(collection[index-1])
			item = ",".join(item) 
		selection = self._get_selection(view_information,extra)
		selection = selection if isinstance(selection,list) else [selection]
		return [(x,item)  for x in selection]







