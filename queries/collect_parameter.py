import ast
from collections import OrderedDict

from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region,make_flat
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import CollectionQuery
from PythonVoiceCodingPlugin.queries.strategies import decode_item_selection
from PythonVoiceCodingPlugin.queries.strategies import decode_abstract_vertical



class CollectParameter(CollectionQuery):
	indexable = True
	label = 'Parameters'
	def handle_single(self,view_information,query_description,extra = {}):
		build, selection, origin = self._preliminary(view_information = view_information,query_description = query_description,extra = extra)
		if not  build: 
			return None,None
		root,atok,m,r = build 
		definition_nodes = [search_upwards(origin,ast.FunctionDef)] if query_description["format"]>=2 else find_all_nodes(root,ast.FunctionDef)
		if query_description["format"]>=2:
			if "vertical_direction"  in query_description:
				definition_node = definition_nodes[0]
				temporary_information = lambda x: match_node(x,ast.FunctionDef) 
				direction = query_description["vertical_direction"]
				ndir = query_description["ndir"]
				row = view_information["rowcol"](m.backward(selection)[0])[0] + 1 if definition_node is None else definition_node.first_token.start[0]
				bonus = 1 if definition_node.first_token.startpos > selection[1]  else 0
				t = decode_abstract_vertical(root,atok,(),row, ndir + bonus,direction,True,temporary_information)
				definition_nodes = [t]

		name_nodes = make_flat([get_argument_from_definition(x)  for x in definition_nodes])
		names = list(OrderedDict([(x,0)  for x in name_nodes]).keys())
		if "experimental"  in query_description:
			names = [x + "=" + x  for x in names] 
		if query_description["format"]==1:
			result = None
		else:
			mode = {
				2:"individual",
				3:"range",
			}[query_description["format"]]
			result = ",".join(decode_item_selection(names,query_description,mode,"item_index"))
		return result, names



		

