import ast

from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region,make_flat
from PythonVoiceCodingPlugin.library.selection_node import nearest_node_from_offset,node_from_range
from PythonVoiceCodingPlugin.library.info import *
from PythonVoiceCodingPlugin.library.partial import partially_parse, line_partial
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery
from PythonVoiceCodingPlugin.queries.tiebreak import tiebreak_on_lca
from PythonVoiceCodingPlugin.queries.strategies import translate_adjective,obtain_result




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

		if query_description["format"]==1:
			if "nth2"  in query_description:
				second_origin = get_sub_index(second_origin,translate_adjective[query_description["nth2"]]-1)
			result = get_sub_index(second_origin,query_description["sub_index"]-1)
			alternatives = []
		elif query_description["format"]==2:
			if "nth2"  in query_description:
				second_origin = get_sub_index(second_origin,translate_adjective[query_description["nth2"]]-1)
			result = [
				get_sub_index(second_origin,query_description["sub_index"]-1),
				get_sub_index(second_origin,query_description.get("sub_index2",0)-1)
			]
			alternatives=[]
		elif query_description["format"]==3 or query_description["format"]==4:
			intermediate = get_sub_index(second_origin,None)
			if "nth2"  in query_description:
				intermediate = [get_sub_index(x,translate_adjective[query_description["nth2"]]-1) for x in intermediate]
				intermediate = [x  for x in intermediate if x]
			candidates = [get_sub_index(x,query_description["sub_index"]-1) for x in intermediate]
			candidates = [x  for x in candidates if x]
			if query_description["format"]==3:
				result,alternatives = obtain_result(None, candidates)
			elif query_description["format"]==4:
				result = candidates if candidates else None
				alternatives=[]
		return self._backward_result(result, alternatives,build,individually=query_description["format"]==4)


	




