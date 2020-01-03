import ast
from collections import OrderedDict

from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region,make_flat
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import CollectionQuery
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection




class CollectParameter(CollectionQuery):
	indexable = True
	label = 'Parameters'
	def handle_single(self,view_information,query_description,extra = {}):
		build, selection, origin = self._preliminary(view_information,query_description,extra)
		if not  build: 
			return None,None
		root,atok,m,r = build 
		definition_nodes = [search_upwards(origin,ast.FunctionDef)] if query_description["format"]>=2 else find_all_nodes(root,ast.FunctionDef)
		name_nodes = make_flat([get_argument_from_definition(x)  for x in definition_nodes])
		names = list(OrderedDict([(x,0)  for x in name_nodes]).keys())
		if query_description["format"]==1:
			result = None
		else:
			mode = {
				2:"individual",
				3:"range",
			}[query_description["format"]]
			result = ",".join(decode_item_selection(names,query_description,mode,"item_index"))
		return result, names



		

