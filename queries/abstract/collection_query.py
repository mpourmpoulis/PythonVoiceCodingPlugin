from copy import deepcopy
from PythonVoiceCodingPlugin.library import get_source_region , nearest_node_from_offset,node_from_range
from PythonVoiceCodingPlugin.library.modification import ModificationHandler
from PythonVoiceCodingPlugin.queries.abstract.query import Query


class CollectionQuery(Query):
	"""docstring for CollectionQuery"""

	multiple_in = False
	indexable = False
	select_insertion = True

	def handle_single(self,view_information,query_description,extra = {}):
		pass

	def handle_multiple(self,view_information,query_description,extra = {}):
		pass

	################################################################
	################################################################

	def __init__(self, code,latest_build = None):
		super(CollectionQuery, self).__init__(code,latest_build)
		self.result = None
		self.writing_positions = []
		self.items = []
		self.optional_selection = []


	def __call__(self,view_information,query_description,extra = {}):
		selection = self._get_selection(view_information,extra)
		self.writing_positions = selection if isinstance(selection,list) else [selection]
		self.writing_positions = sorted(self.writing_positions)
		if self.indexable:
			self.result,self.items = self.handle_single(view_information,query_description,extra)	
			if self.result and self.select_insertion:
				m = ModificationHandler()
				for location in self.writing_positions:
					m.modify_from(0, location, self.result)
				self.optional_selection = [m.forward(x)  for x in self.writing_positions]
		else:
			self.items = self.handle_single(view_information,query_description,extra)

		return self.result,self.items,self.writing_positions ,self.optional_selection

	def _preliminary(self,view_information,query_description, extra = {}):
		selection = self._get_selection(view_information,extra)
		build = self.general_build 
		if not build  or not build[0] :
			return None,None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		return build, selection, origin


		






