import ast

from PythonVoiceCodingPlugin.library import nearest_node_from_offset,sorted_by_source_region,get_source_region,node_from_range,make_flat
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.library.partial import partially_parse, line_partial
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery
from PythonVoiceCodingPlugin.queries.tiebreak import tiebreak_on_lca
from PythonVoiceCodingPlugin.queries.strategies import adjective_strategy,decode_abstract_vertical,translate_adjective,obtain_result




class SelectPart(SelectionQuery):
	multiple_in = True
	
	

	def handle_single(self,view_information,query_description,extra = {}):
		print(" inside here selection where he parked ")
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		if selection[0]==selection[1]:
			return None,None
		second_origin = origin
		if "nth"  in query_description:
			print(" hello world  ")
			print(translate_adjective[query_description["nth"]])
			second_origin = get_sub_index(origin,translate_adjective[query_description["nth"]]-1)

		print(" just before the end",second_origin)
		result = get_sub_index(second_origin,query_description["sub_index"]-1)
		alternatives = []
		return self._backward_result(result, alternatives,build)


	




