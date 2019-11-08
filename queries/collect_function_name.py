import ast
from collections import OrderedDict

from PythonVoiceCodingPlugin.library import nearest_node_from_offset,sorted_by_source_region,get_source_region,node_from_range,make_flat
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import CollectionQuery





class CollectFunctionName(CollectionQuery):
	indexable = True
	def handle_single(self,view_information,query_description,extra = {}):
		build, selection, origin = self._preliminary(view_information,query_description,extra)
		if not  build: 
			return None,None
		root,atok,m,r = build 
		definition_nodes = find_all_nodes(root,(ast.FunctionDef))
		name_nodes = [x.name  for x in definition_nodes]
		names = list(OrderedDict([(x,0)  for x in name_nodes]).keys())
		result = names[query_description["collect_index"] - 1] if query_description["format"]==2 else None
		return result, names



		

