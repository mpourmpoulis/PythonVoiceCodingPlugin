from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery, no_build_attempt



@no_build_attempt
class RememberHere(SelectionQuery):
	"""docstring for SelectAlternative"""
	initial_origin_force_update = True

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)
		
	def handle_single(self,view_information,query_description,extra = {}):
		selection = self._get_selection(view_information,extra)
		return selection,[]


