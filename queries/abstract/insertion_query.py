import abc
from copy import deepcopy

from PythonVoiceCodingPlugin.library import get_source_region 
from PythonVoiceCodingPlugin.library.modification import ModificationHandler
from PythonVoiceCodingPlugin.queries.abstract.query import Query



class InsertionQuery(Query):
	################################################################
	# attributes and methods the user can override\change
	################################################################
	multiple_in = False
	select_insertion = True

	@abc.abstractmethod
	def handle_single(self,view_information,query_description,extra = {}):
		pass

	@abc.abstractmethod
	def handle_multiple(self,view_information,query_description,extra = {}):
		pass

	################################################################
	# standard code for default functionality
	################################################################
	def __init__(self, code,latest_build = None):
		super(InsertionQuery, self).__init__(code, latest_build)
		self.writing_locations_text = []
		self.optional_selection = []

	handle_single._original = True
	handle_multiple._original = True

		
	def __call__(self,view_information,query_description,extra = {}):
		self.view_information = view_information
		self.query_description = query_description
		selection = self._get_selection(view_information,extra)
		if isinstance(selection,list):
			if hasattr(self.handle_multiple,"_original"):
				if hasattr(self.handle_single,"_original") or not self.multiple_in: 
					return [],[]
				self.writing_locations_text = []
				for s in selection:
					temporary_extra = deepcopy(extra)
					temporary_extra["selection"] = s
					w = self.handle_single(view_information,query_description,temporary_extra)
					self.writing_locations_text.extend(w)
			else:
				self.writing_locations_text = self.handle_multiple(view_information,query_description, extra)
		else:
			if hasattr(self.handle_single,"_original"):
				return [],[]
			self.writing_locations_text = self.handle_single(view_information,query_description, extra)
		self.writing_locations_text = sorted(self.writing_locations_text, key = lambda x:x[0],reverse=True)
		if self.select_insertion:
			m = ModificationHandler()
			for location,t in self.writing_locations_text:
				# print(" inside the loop ", location,t,"\n")
				m.modify_from(0, location, t)
			self.optional_selection = [m.forward(x[0])  for x in self.writing_locations_text]
		return self.writing_locations_text,self.optional_selection

