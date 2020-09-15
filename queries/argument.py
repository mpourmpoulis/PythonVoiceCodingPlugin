import ast

from copy import deepcopy



from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region,make_flat
from PythonVoiceCodingPlugin.library.selection_node import nearest_node_from_offset,node_from_range
from PythonVoiceCodingPlugin.library.info import (
	identity,get_argument_from_call,get_keyword_argument, make_information ,
	correspond_to_index_in_call,get_caller,get_sub_index,get_weak_header,get_argument_from_empty_call,
	get_return_value,generic_fix,get_pure_if_condition,get_elif_condition,get_condition,
	is_decorator,get_with_items,get_body,get_arithmetic,get_boolean,get_iterable
)
from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.library.partial import partially_parse, line_partial
from PythonVoiceCodingPlugin.library.traverse import (
	search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent
)

from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery
from PythonVoiceCodingPlugin.queries.tiebreak import tiebreak_on_lca,tiebreak_on_visual
from PythonVoiceCodingPlugin.queries.strategies import (
	adjective_strategy,decode_abstract_vertical,translate_adjective,obtain_result,
	decode_item_selection,result_alternatives_sequence
)

# a lot of this code needs rewriting at some point
# it is a mess indeed but it works, mostly :)
#





class SelectArgument(SelectionQuery):
	multiple_in = True

	external_constrained_space = ()

	def get_information(self,query_description):
		# print(self,query_description)
		def decrement_positive(x):
			return x-1 if x>0 else x

		if "argument_index" in query_description:
			if query_description["argument_index"]==0:
				return make_information(get_argument_from_empty_call)
			else:
				return make_information(get_argument_from_call,decrement_positive(query_description["argument_index"]))
		elif "keyword_index" in query_description:
			return make_information(get_keyword_argument,decrement_positive(query_description["keyword_index"]),only_keyword=True)
		elif "keyword_value_index" in query_description:
			return make_information(get_keyword_argument,decrement_positive(query_description["keyword_value_index"]),only_value=True)
		elif "entire_keyword_index" in query_description:
			return make_information(get_keyword_argument,decrement_positive(query_description["entire_keyword_index"]),only_keyword=False,only_value = False)
		elif "caller" in query_description:
			if "sub_index" not in query_description:
				return get_caller
			else:
				i = decrement_positive(query_description["sub_index"])
				return lambda x:get_sub_index(get_caller(x),i)
		else:
			return identity(match_node,ast.Call)
	
	def get_statement(self,origin,atok):
		self.global_constrained_space = None
		candidate_statement = search_upwards(origin,ast.stmt)
		big = (ast.If,ast.While,ast.For,ast.FunctionDef,ast.With,ast.ClassDef,ast.Try,ast.ExceptHandler)
		if match_node(candidate_statement,big):
			candidate_statement = search_upwards_for_parent(origin,ast.stmt)
			candidate_statement = candidate_statement if candidate_statement else search_upwards(origin,ast.stmt)
			if match_node(candidate_statement,big):
				region = get_source_region(atok,get_weak_header(candidate_statement,atok))
				if region:
					self.global_constrained_space = region
		return candidate_statement

	def process_line(self,q, root ,atok, origin  = None, select_node = None,tiebreaker = lambda x: x, 
					line = None, transformation = None,inverse_transformation = None, priority = {}, 
					constrained_space = (), second_tiebreaker = None,invert_then_tiebreak  = True
		):
		"""
		
		Args:
		    q (dict): the query description
		    root (ast.AST): root of the area to search
		    atok (TYPE): Description
		    origin (ast.AST , optional): origin of the query
		    select_node (ast.AST , optional): the node that is currently selected
		    tiebreaker (TYPE, optional): Description
		    line (None, optional): Description
		    transformation (None, optional): Description
		    inverse_transformation (None, optional): Description
		    priority (dict, optional): Description
		    constrained_space (tuple, optional): Description
		    second_tiebreaker (None, optional): Description
		    invert_then_tiebreak (bool, optional): Description
		
		Returns:
		    TYPE: Description
		"""
		result = None
		alternatives = None
		additional_parameters = {"priority":priority}
		if constrained_space:
			additional_parameters["constrained_space"] = constrained_space


		information = self.get_information(q)
		information_nodes = sorted_by_source_region(atok, find_matching(root, information))

		if origin:
			calling_node = search_upwards(origin,ast.Call)
			statement_node, callers = search_upwards_log(origin,ast.stmt,log_targets = ast.Call)


		every_caller = find_all_nodes(root,(ast.Call))
		additional = find_all_nodes(root,(ast.Tuple,ast.List,ast.ListComp))
		if additional:
			additional_parameters["additional_level_nodes"] = additional
			additional_parameters["try_alternative"] = True

		################################################################
		# go to handle the special Casey's
		################################################################
		if transformation:
			temporary = {transformation(x) for x in information_nodes}
			information_nodes = sorted_by_source_region(atok,[x  for x in temporary if x])

		
		################################################################
		# if no adjective is given
		################################################################
		if "nth" not in q:
			if origin  and calling_node:
				result = calling_node if calling_node in information_nodes else None
				information_nodes = [x  for x in tiebreaker(information_nodes) if x is not calling_node]
			else:
				result = None
				information_nodes = [x for x in tiebreaker(information_nodes)]
			result,alternatives = obtain_result(result,information_nodes)



		################################################################
		# adjective is given
		################################################################
		if "nth" in q:
			additional_parameters["small_root"] = select_node			
			if origin  and calling_node:
				additional_parameters["penalized"] = [calling_node] if calling_node else []
				additional_parameters["special"] = [calling_node]
			result, alternatives = adjective_strategy(
				atok=atok,
				root = root,
				adjective_word = q["nth"],
				level_nodes = every_caller,
				information_nodes = information_nodes,
				**additional_parameters
			)

		##############################################################
		# reverse transformation if any
		##############################################################
		if transformation:
			helpful = [result] if result else []
			if alternatives:	 
				helpful.extend(alternatives)
			if invert_then_tiebreak:
				temporary = make_flat([tiebreaker(inverse_transformation(x))  for x in helpful])
			else:
				temporary = tiebreaker(make_flat([inverse_transformation(x)  for x in helpful]))
			result, alternatives = obtain_result(None,temporary)
		
		################################################################
		# Extract information
		################################################################
		if line  and result  and alternatives:
			temporary = [result] + alternatives
			temporary = [(i,x)  for i,x in enumerate(temporary)]
			temporary = sorted(temporary, key=lambda x: (atok._line_numbers.offset_to_line(get_source_region(atok,x[1])[0])[0] != line,x[0]))
			temporary = [x[1]  for x in temporary]
			result,alternatives = obtain_result(None,temporary)
			
		if result and second_tiebreaker:
			alternatives = second_tiebreaker(result,alternatives)

		if self.global_constrained_space or self.external_constrained_space:
			inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1])
			print("alternative",alternatives)
			def valid_region(x):
				r = get_source_region(atok,x)
				try :
					return (
						(not self.global_constrained_space or inside(r,self.global_constrained_space))
						and
						(not self.external_constrained_space or inside(r,self.external_constrained_space))
					)
				except:
					print(self.global_constrained_space,self.external_constrained_space,r,x)
					raise
			result = result if result and valid_region(result) else None
			alternatives = alternatives and [x  for x in alternatives if valid_region(x)]
			result,alternatives = obtain_result(result,alternatives)




		result = information(result) if result else None
		alternatives  =[ information(x)  for x in alternatives] if alternatives else []
		return result, alternatives
		


	def handle_single(self,view_information,query_description,extra = {}):
		f = query_description["format"]
		possibilities = {
			1: self.case_one,2: self.case_two,3: self.case_three,
			4: self.case_four,5:self.case_five,6:self.case_six,
			7: self.case_seven,8: self.case_eight,9:self.case_nine,
		}
		return  possibilities[f](view_information,query_description, extra)



	def case_one(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> argument <argument_index> 
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build
		
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x),
		)
		return self._backward_result(result, alternatives,build)


	def case_two(self,view_information,query_description, extra = {}):
		################################################################	
		#		<vertical_direction> <ndir> <adjective> argument <argument_index>
		###############################################################	
		selection = self._get_selection(view_information,extra)
		if "vertical_direction" in query_description:
			vertical_direction = query_description["vertical_direction"]
			ndir = query_description["ndir"]
		else:
			vertical_direction = "upwards"
			ndir = 0


		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)

		# this is the wrong but for some reason it is working:)
		if vertical_direction in ["upwards","downwards"]:
			row, column = view_information["rowcol"](m.backward(selection)[0]) 
			nr = decode_abstract_vertical(root,atok,ast.Call,row+1, ndir,vertical_direction)-1
			t = view_information["text_point"](nr,0)
			selection = (t,t)
			selection = m.forward(selection)		

		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)


		# 
		alternative_logical_lines = find_all_nodes(statement_node.parent,selector = lambda x:match_node(x,ast.stmt) and x.first_token.start[0]==origin.first_token.start[0]
			,visit_all_levels=False)
		sharing_physical = alternative_logical_lines not in [[] ,[statement_node]]

		priority = {"root_lexical_order":1} if ( statement_node.first_token.start[0] != origin.first_token.start[0]
									or sharing_physical or ndir) else {}
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node if not sharing_physical else statement_node.parent,
			atok = atok,
			origin = None,
			select_node = None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node if not sharing_physical else statement_node.parent,origin,x),
			line = nr+1,
			priority = priority,
			constrained_space = m.forward((view_information["text_point"](nr ,0),view_information["text_point"](nr + 1,0))),
			second_tiebreaker = lambda x,y : tiebreak_on_visual(row + 1,x,y)
		)
		if sharing_physical:
			if alternatives:
				alternatives = [x  for x in alternatives if  x.first_token.start[0]==origin.first_token.start[0]]
			if result and result.first_token.start[0]!=origin.first_token.start[0]:
				result, alternatives = obtain_result(result, alternatives)
		return self._backward_result(result, alternatives,build)

		

	def case_three(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> inside <level_index> argument <argument_index> 
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)

		###############################################################
		# transformations
		################################################################
		temporary = {}
		lca = LCA(statement_node)


		def transformation(node):
			calling_parent = search_upwards_for_parent(node,ast.Call)
			calling_parent  = calling_parent.parent if calling_parent else None

			if  not calling_parent:
				return None
			field,field_index = lca.get_field_with_respect_to(node,calling_parent)
			if query_description["level_index"]== 0 or correspond_to_index_in_call(calling_parent,query_description["level_index"]-1,field,field_index):
				if calling_parent not in temporary:
					temporary[calling_parent] = []
				temporary[calling_parent].append(node)
				return calling_parent
			else:
				return None

		def inverse_transformation(node):
			if node in temporary:
				return temporary[node]
			else:
				return None



		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x,lca),
			transformation = transformation,
			inverse_transformation = inverse_transformation,

		)
		return self._backward_result(result, alternatives,build)

	def case_four(self,view_information,query_description, extra = {}):
		################################################################	
		#		<level> [<level_index>] <adjective> (argument <argument_index>|caller [<sub_index>])
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)

		###############################################################
		# transformationszooming
		################################################################
		every_caller = find_all_nodes(root,(ast.Call))
		level = LevelVisitor(root,every_caller,atok)
		lca = LCA(statement_node)


		def transformation(node):
			calling_parent, field,field_index = level[node] 
			if  not calling_parent or calling_parent is level.root:
				return None
			if query_description["level_index"]== 0 or correspond_to_index_in_call(calling_parent,query_description["level_index"]-1,field,field_index):
				adj = translate_adjective[query_description["nth"]]-1
				n = level(node, 3,adj)
				return node if n is node else None
			else:
				return None

		def inverse_transformation(node):
			return [node]	





		q = deepcopy(query_description); del q["nth"] 
		result, alternatives = self.process_line(
			q = q,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x,lca),
			transformation = transformation,
			inverse_transformation = inverse_transformation,
			invert_then_tiebreak = False
		)	
		return self._backward_result(result, alternatives,build)


	

	def case_five(self,view_information,query_description, extra = {}):
		################################################################	
		#		<level> [<level_index>] <adjective> (argument <argument_index>|caller [<sub_index>])
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)
		priority = {}
		if query_description["level_index"]==0:
			query_description["level_index"] = -1
		_,calling_parents = search_upwards_log(origin,targets=ast.stmt,log_targets=(ast.Call))
		index = query_description["level_index"]
		if index<len(calling_parents):
			priority["child_level"] = 1
			origin = calling_parents[index]
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x),
			priority = priority

		)	
		return self._backward_result(result, alternatives,build)

	def get_colorful(self,view_information,query_description, extra = {}):
		state = extra["state"]
		index = extra.get("index",0)
		candidates = result_alternatives_sequence(state,location=True)
		if state["mode"]=="single":
			colorful_region = decode_item_selection(candidates,query_description,"individual","color",decrement=False)
		else:
			colorful_region = decode_item_selection(candidates[index],query_description,"individual","color",decrement=False)
		return colorful_region[0]
		
	def case_six(self,view_information,query_description, extra = {}):
		################################################################	
		#		<color> [<adjective>] argument <argument_index> 
		###############################################################	
		selection = self.get_colorful(view_information,query_description,extra)
		new_extra = extra.copy()
		new_extra.update(dict(selection=selection))
		self.external_constrained_space = selection
		return self.case_one(view_information,query_description,new_extra)

	def case_seven(self,view_information,query_description, extra = {}):
		################################################################	
		#		<color> [<adjective>] argument <argument_index> 
		###############################################################	
		selection = self.get_colorful(view_information,query_description,extra)
		new_extra = extra.copy()
		new_extra.update(dict(selection=selection))
		self.external_constrained_space = selection
		return self.case_four(view_information,query_description,new_extra)


	def case_eight(self,view_information,query_description, extra = {}):
		################################################################	
		#		<color> [<adjective>] argument <argument_index> 
		###############################################################	
		selection = self.get_colorful(view_information,query_description,extra)
		new_extra = extra.copy()
		new_extra.update(dict(selection=selection))
		self.external_constrained_space = selection
		return self.case_three(view_information,query_description,new_extra)

	def case_nine(self,view_information,query_description, extra = {}):
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(self.code,selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build
		
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = self.get_statement(origin,atok)


		definition_node = search_upwards(origin,(ast.FunctionDef,ast.ClassDef,ast.Module)) 
		standard = lambda x:x
		targets, exclusions, information  =  {
			"return": ((ast.Return,ast.Yield,ast.YieldFrom),(),get_return_value),
			"if":(ast.If,(),get_pure_if_condition),
			"else if":(ast.If,(),get_elif_condition),
			"while":(ast.While,(),get_condition),
			"decorator":((ast.AST),(),identity(is_decorator)),
			"assignment":((ast.Assign,ast.AugAssign),(),standard),
			"expression":(ast.Expr,(),standard),
			"comprehension":((ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp),(),standard),
			"assert":(ast.Assert,(),standard),
			"with":(ast.With,(),get_with_items),
			"lambda":((ast.Lambda),(),get_body),
			"if expression":(ast.IfExp,(),standard),
			"comparison":((ast.Compare),(),standard),
			"arithmetic":((ast.BinOp),(),get_arithmetic),
			"boolean":((ast.BoolOp),(),get_boolean),
			"iterable":((ast.For,ast.comprehension),(),get_iterable),

			# lambda,with,comprehension if,indexed,raise,assert,dictionary,iterable,initialization,if expression
		}[query_description["small_block"]]
		selector = lambda x:match_node(x,targets,exclusions) and generic_fix(x,build[1])
		candidates = tiebreak_on_lca(definition_node,origin,find_all_nodes(definition_node, selector = selector))
		candidates = [information(x)  for x in candidates if information(x)]
		# result, alternatives = obtain_result(None, candidates)
		candidate_results = []
		for c in candidates:
			new_extra = extra.copy()
			new_extra["selection"] = self.external_constrained_space = get_source_region(atok, c)
			print(new_extra)
			result,alternatives = self.case_one(view_information,query_description,new_extra)
			if result:
				candidate_results.extend([result])
				candidate_results.extend(alternatives or [])
				if len(candidate_results)>6:
					break

		return obtain_result(None,candidate_results)










	