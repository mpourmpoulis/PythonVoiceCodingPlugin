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

class SelectBigRoi(SelectionQuery):
	"""docstring for BigRoi"""
	
	def handle_single(self,view_information,query_description,extra = {}):
		f = query_description["format"]
		possibilities = {
			1: self.case_one,2: self.case_two,3: self.case_three,4: self.case_four,
		}
		return  possibilities[f](view_information,query_description, extra)

	def preliminary(self,view_information,query_description, extra = {}):
		selection = self._get_selection(view_information,extra)
		build = self.general_build 
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		definition_node = search_upwards(origin,ast.FunctionDef) # need to change that in the future 
		# in order to find the outermost function.
		definition_node  = ( definition_node 
			if definition_node  and query_description["big_roi"] not in ["import statement"]
			else root
		)
		return build, selection, origin, definition_node

	def decode(self,query_description):
		standard = lambda x:x
		possibilities = {
			"return value": ((ast.Return,ast.Yield,ast.YieldFrom),(),get_return_value),
			"pass":(ast.Pass,(),standard),
			"break":(ast.Break,(),standard),
			"continue":(ast.Continue,(),standard),
			"if condition":(ast.If,(),get_pure_ifcondition),
			"else if condition":(ast.If,(),get_elif_condition),
			"while condition":(ast.While,(),get_condition),
			"if expression":(ast.IfExp,(),standard),
			"if expression condition":(ast.IfExp,(),get_condition),
			"if expression body":(ast.IfExp,(),get_body),
			"assertion message":(ast.Assert,(), get_message),
			"assertion condition":(ast.Assert,(), get_condition),
			"assignment left":((ast.Assign,ast.AugAssign),(),get_left),
			"assignment right":((ast.Assign,ast.AugAssign),(),get_right),
			"assignment full":((ast.Assign,ast.AugAssign),(),standard),
			"expression statement":(ast.Expr,(),standard),
			"iterable":((ast.For,ast.comprehension),(),get_iterable),
			"iterator":((ast.For,ast.comprehension),(),get_iterator),
			
			"import statement":((ast.Import,ast.ImportFrom),(),standard),
		}
		temporary  = possibilities[query_description["big_roi"]]
		if "big_roi_sub_index" in query_description:
			if query_description["big_roi_sub_index"] == 0:
				return  possibilities[query_description["big_roi"]]
			else:
				index = query_description["big_roi_sub_index"]
				def modified_information(x, information,index):
					data  = information(x)
					if isinstance(data,list):
						if len(data)!=1:
							return data[index]
						else:
							data = data[0]
					if match_node(data,(ast.List,ast.Tuple,ast.Set)):
						if index<len(data.elts):
							return data.elts[index]
					elif match_node(data,(ast.Dict)):
						if index<len(data.keys):
							return [data.keys[index], data.values[index]]
					else:
						return None
				return (temporary[0],temporary[1], lambda x: modified_information(x,temporary[2],index-1))


	def case_one(self,view_information,query_description, extra = {}):
		################################################################	
		#		<big_roi>
		###############################################################	
		build, selection, origin, definition_node = self.preliminary(view_information, query_description,extra)
		targets, exclusions, information  =  self.decode(query_description)
		candidates = tiebreak_on_lca(definition_node,origin,find_all_nodes(definition_node, targets, exclusions))
		candidates = [information(x)  for x in candidates if information(x)]
		result, alternatives = obtain_result(None, candidates)
		return  self._backward_result(result, alternatives,build)


	def case_two(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> <big_roi>
		###############################################################	
		build, selection, origin, definition_node = self.preliminary(view_information, query_description,extra)
		targets, exclusions, information  =  self.decode(query_description)
		temporary_information = lambda x: information(x) if match_node(x,targets,exclusions) else None
		additional_parameters = {}
		root,atok,m,r  = build 

		if selection[0]!=selection[1]:
			additional_parameters["small_root"] = origin
		additional_parameters["only_information"] = True
		# just looking on the shape of this code you know there's a bug in here somewhere:)
		result, alternatives = adjective_strategy(
				atok=atok,
				root = definition_node,
				adjective_word = query_description["adjective"],
				level_nodes = find_all_nodes(definition_node,(ast.If,ast.While,ast.For,ast.Try,ast.With,ast.FunctionDef)),
				information_nodes = find_matching(definition_node,temporary_information),
				**additional_parameters
		)
		print(result,alternatives)
		result = information(result) if result else None
		alternatives  =[ information(x)  for x in alternatives] if alternatives else []
		return  self._backward_result(result, alternatives,build)


	def case_three(self,view_information,query_description, extra = {}):
		################################################################	
		# <vertical_abstract_only_direction> [<ndir>] <big_roi> [<big_roi_sub_index>]
		###############################################################	
		build, selection, origin, definition_node = self.preliminary(view_information, query_description,extra)
		targets, exclusions, information  =  self.decode(query_description)
		temporary_information = lambda x: information(x) if match_node(x,targets,exclusions) else None
		root,atok,m,r  = build

		direction = query_description["vertical_abstract_only_direction"]
		ndir = query_description["ndir"]
		row, column = view_information["rowcol"](m.backward(selection)[0])
		print("is going to be a really good",selection,row)
		result = decode_abstract_vertical(root,atok,targets,row+1, ndir,direction,True,temporary_information)
		alternatives = []

		if result:
			new_definition_node = search_upwards(result,ast.FunctionDef)
			if definition_node is not new_definition_node:
				alternatives  = tiebreak_on_lca(new_definition_node,result,find_all_nodes(new_definition_node,targets , exclusions))

		result, alternatives = obtain_result(result, alternatives)
		result = information(result) if result else None
		alternatives  = [information(x)  for x in alternatives] if alternatives else []
		return  self._backward_result(result, alternatives,build)


	def case_four(self,view_information,query_description, extra = {}):
		################################################################	
		# [smart] <vertical_abstract_only_direction> [<ndir>] <block> [<adjective>] <big_roi> [<big_roi_sub_index>]
		###############################################################	
		build, selection, origin, definition_node = self.preliminary(view_information, query_description,extra)
		targets, exclusions, information  =  self.decode(query_description)
		temporary_information = lambda x: match_node(x,ast.FunctionDef) 
		root,atok,m,r  = build
		
		direction = query_description["vertical_abstract_only_direction"]
		ndir = query_description["ndir"]
		row = view_information["rowcol"](selection[0])[0] + 1 if definition_node is root else definition_node.first_token.start[0]
		bonus = 1 if definition_node.first_token.startpos > selection[1] else 0

		t = decode_abstract_vertical(root,atok,targets,row, ndir + bonus,direction,True,temporary_information)
		print(ast.dump(definition_node))
		if query_description["adjective"]=="None":
			candidates = tiebreak_on_lca(root,definition_node,find_all_nodes(t, targets, exclusions))
			candidates = [information(x)  for x in candidates if information(x)]
			result, alternatives = obtain_result(None, candidates)
			return  self._backward_result(result, alternatives,build)
		else:
			additional_parameters = {}
			result, alternatives = adjective_strategy(
				atok=atok,
				root = t,
				adjective_word = query_description["adjective"],
				level_nodes = find_all_nodes(t,(ast.If,ast.While,ast.For,ast.Try,ast.With,ast.FunctionDef)),
				information_nodes = find_matching(t,lambda x: information(x) if match_node(x,targets,exclusions) else None),
				**additional_parameters
			)
			result = information(result) if result else None
			alternatives  =[ information(x)  for x in alternatives] if alternatives else []
			return  self._backward_result(result, alternatives,build)
















