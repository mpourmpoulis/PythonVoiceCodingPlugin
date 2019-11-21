import ast

from PythonVoiceCodingPlugin.library import nearest_node_from_offset,sorted_by_source_region,get_source_region,node_from_range,make_flat
from PythonVoiceCodingPlugin.library.info import identity,get_argument_from_call, make_information ,correspond_to_index_in_call
import PythonVoiceCodingPlugin.library.info as info
from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.library.partial import partially_parse, line_partial
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes,search_upwards_for_parent

from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery
from PythonVoiceCodingPlugin.queries.tiebreak import tiebreak_on_lca
from PythonVoiceCodingPlugin.queries.strategies import adjective_strategy,decode_abstract_vertical,translate_adjective,obtain_result

# 
# a lot of this code needs rewriting at some point
# it is a mess indeed but it works, mostly :)
#





class SelectArgument(SelectionQuery):
	"""docstring for SelectArgument"""
	# def __init__(self):
		# super(SelectArgument, self).__init__()


	def process_line(self,q, root ,atok, origin  = None, select_node = None,tiebreaker = lambda x: x, 
					line = None, transformation = None,inverse_transformation = None, priority = {}, 
					constrained_space = (),
		):
		result = None
		alternatives = None
		additional_parameters = {"priority":priority}
		if constrained_space:
			additional_parameters["constrained_space"] = constrained_space


		information = make_information(get_argument_from_call,q["argument_index"]-1)
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
		if q["adjective"] == "None":
			if origin  and calling_node:
				result = calling_node if calling_node in information_nodes else None
				information_nodes = [x  for x in tiebreaker(information_nodes) if x != calling_node]
			else:
				result = None
				information_nodes = [x for x in tiebreaker(information_nodes)]
			result,alternatives = obtain_result(result,information_nodes)


		################################################################
		# adjective is given
		################################################################
		if q["adjective"] != "None":
			additional_parameters["small_root"] = select_node			
			if origin  and calling_node:
				additional_parameters["penalized"] = [calling_node] if calling_node else []
				additional_parameters["special"] = [calling_node]
			result, alternatives = adjective_strategy(
				atok=atok,
				root = root,
				adjective_word = q["adjective"],
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
			temporary = make_flat([tiebreaker(inverse_transformation(x))  for x in helpful])
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
			




		result = information(result) if result else None
		alternatives  =[ information(x)  for x in alternatives] if alternatives else []
		return result, alternatives
		


	def handle_single(self,view_information,query_description,extra = {}):
		f = query_description["format"]
		possibilities = {
			1: self.case_one,2: self.case_two,3: self.case_three,4: self.case_four,
		}
		return  possibilities[f](view_information,query_description, extra)



	def case_one(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> argument <argument_index> 
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = search_upwards(origin,ast.stmt)
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x)
		)
		return self._backward_result(result, alternatives,build)


	def case_two(self,view_information,query_description, extra = {}):
		################################################################	
		#		<vertical_direction> <ndir> <adjective> argument <argument_index>
		###############################################################	
		selection = self._get_selection(view_information,extra)
		vertical_direction = query_description["vertical_direction"]
		ndir = query_description["ndir"]

		if vertical_direction in ["up","down"]:
			row, column = view_information["rowcol"](selection[0])
			nr = max(0,row + ndir if vertical_direction=="down" else row - ndir)
			t = view_information["text_point"](nr,0)
			selection = (t,t)

		build = self.general_build if self.general_build else line_partial(selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)

		if vertical_direction in ["above","below"]:
			row, column = view_information["rowcol"](selection[0])
			nr = decode_abstract_vertical(root,atok,ast.Call,row+1, ndir,vertical_direction)-1
			t = view_information["text_point"](nr,0)
			selection = (t,t)
			selection = m.forward(selection)		

		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = search_upwards(origin,ast.stmt)
		priority = {"root_lexical_order":1} if statement_node.first_token.start[0] != origin.first_token.start[0] else {}
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = None,
			select_node = None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x),
			line = nr+1,
			priority = priority,
			constrained_space = (view_information["text_point"](nr,0),view_information["text_point"](nr + 1,0))
		)
		return self._backward_result(result, alternatives,build)

		

	def case_three(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> inside <level_index> argument <argument_index> 
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = search_upwards(origin,ast.stmt)

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
			if correspond_to_index_in_call(calling_parent,query_description["level_index"]-1,field,field_index):
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
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x),
			transformation = transformation,
			inverse_transformation = inverse_transformation

		)
		return self._backward_result(result, alternatives,build)

	def case_four(self,view_information,query_description, extra = {}):
		################################################################	
		#		<adjective> inside <level_index> argument <argument_index> 
		###############################################################	
		selection = self._get_selection(view_information,extra)
		build = self.general_build if self.general_build else line_partial(selection[0])
		if not build  or not build[0] :
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)
		origin = nearest_node_from_offset(root,atok, selection[0]) if selection[0]==selection[1] else node_from_range(root,atok, selection)
		statement_node = search_upwards(origin,ast.stmt)

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
			if correspond_to_index_in_call(calling_parent,query_description["level_index"]-1,field,field_index):
				adj = translate_adjective[query_description["adjective"]]-1
				n = level(node, 3,adj)
				return node if n is node else None
			else:
				return None

		def inverse_transformation(node):
			return [node]														

			
		result, alternatives = self.process_line(
			q = query_description,
			root = statement_node,
			atok = atok,
			origin = origin,
			select_node = origin if selection[0]!=selection[1] else None,
			tiebreaker = lambda x: tiebreak_on_lca(statement_node,origin,x),
			transformation = transformation,
			inverse_transformation = inverse_transformation

		)
		return self._backward_result(result, alternatives,build)


	



