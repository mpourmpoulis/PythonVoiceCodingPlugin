from copy import deepcopy

from PythonVoiceCodingPlugin.library import get_source_region 
from PythonVoiceCodingPlugin.queries.abstract.query import Query

class SelectionQuery(Query):
	################################################################
	# attributes and methods the user can override\change
	################################################################
	multiple_in = False

	def handle_single(self,view_information,query_description,extra = {}):
		pass

	def handle_multiple(self,view_information,query_description,extra = {}):
		pass
		
	################################################################
	# standard code for default functionality
	################################################################
	def __init__(self, code,latest_build = None):
		super(SelectionQuery, self).__init__(code,latest_build)
		self.result = None
		self.alternatives = None

	handle_single._original = True
	handle_multiple._original = True

	def get_result(self):
		return self.result

	def get_alternatives(self):
		return self.alternatives

	def get_the_latest_build(self):
		return self.general_build

	def _backward_result(self,result,alternatives,build):
		if build  and  build[0]:
			m = build[2]
			atok = build[1] 
			result = m.backward(get_source_region(atok, result)) if result else None
			#self._get_selection(view_information,extra)
			alternatives = [m.backward(get_source_region(atok,x)) for x in alternatives]
			return result, alternatives
		else:
			return None,None


	def __call__(self,view_information,query_description,extra = {}):
		self.view_information = view_information
		self.query_description = query_description
		selection = self._get_selection(view_information,extra)
		if isinstance(selection,list):
			if hasattr(self.handle_multiple,"_original"):
				if hasattr(self.handle_single,"_original") or not self.multiple_in: 
					return None,None
				self.result = []
				self.alternatives = []
				for s in selection:
					temporary_extra = deepcopy(extra)
					temporary_extra["selection"] = s
					r,a = self.handle_single(view_information,query_description,temporary_extra)
					self.result.append(r)
					self.alternatives.append(a)
			else:
				self.result ,self.alternatives = self.handle_multiple(view_information,query_description, extra)
		else:
			if hasattr(self.handle_single,"_original"):
				return None,None
			self.result ,self.alternatives = self.handle_single(view_information,query_description, extra)
		return self.result,self.alternatives



