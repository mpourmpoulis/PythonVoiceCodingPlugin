import ast
from collections import OrderedDict

from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region,make_flat
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import CollectionQuery





class CollectModule(CollectionQuery):
	indexable = False
	label = "Modules"
	def handle_single(self,view_information,query_description,extra = {}):
		build, origin, selection = self._preliminary(view_information,query_description,extra)
		if not  build: 
			return None,None
		root,atok,m,r = build 
		definition_nodes = find_all_nodes(root,(ast.Import,ast.ImportFrom))
		name_nodes = make_flat([get_module_names(x)  for x in definition_nodes])
		for name in name_nodes:
			smaller = name.split(".")
			if len( smaller)>1:
				name_nodes.append(".".join(smaller[:-1]))
		names = list(OrderedDict([(x,0)  for x in name_nodes]).keys())
		result = None
		return  names



		

