from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection

@no_build_attempt
class InsertItem(InsertionQuery):
	select_insertion = True
	multiple_in = True

	def handle_single(self,view_information,query_description,extra = {}):
		collection = extra["global_state"]["collection"]
		mode = {
			1:"individual",
			3:"individual",
			2:"range",
		}[query_description["format"]]
		items = ",".join(decode_item_selection(collection,query_description,mode,"item_index"))
		selection = self._get_selection(view_information,extra)
		selection = selection if isinstance(selection,list) else [selection]
		return [(x,items)  for x in selection]







