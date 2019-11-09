import ast

from PythonVoiceCodingPlugin.library import nearest_node_from_offset,sorted_by_source_region,get_source_region,node_from_range
from PythonVoiceCodingPlugin.library.info import identity,get_argument_from_call 
import PythonVoiceCodingPlugin.library.info as info
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.library.partial import partially_parse, line_partial
from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes

from PythonVoiceCodingPlugin.queries.abstract import SelectionQuery
from PythonVoiceCodingPlugin.queries.tiebreak import tiebreak_on_lca
from PythonVoiceCodingPlugin.queries.strategies import adjective_strategy

def obtain_result(result, alternatives):
	if result:
		return result, alternatives if alternatives is not None else []
	else:
		if alternatives is None or len( alternatives )==0:
			return None,None
		else:
			return  alternatives[0], alternatives[1:]




class SelectArgument(SelectionQuery):
	"""docstring for SelectArgument"""
	# def __init__(self):
		# super(SelectArgument, self).__init__()



	def handle_single_point(self,view_information,query_description):
		f = query_description["format"]
		possibilities = {
			1: self.case_one,
		}
		return possibilities[f](view_information,query_description)

	def case_one(self,v,q):
		"""	
				<adjective> argument <argument_index> 
		"""		
		selection = v["selection"]
		build = self.general_build if self.general_build else line_partial(selection[0])
		print(build)
		if not build:
			return None,None
		root,atok,m,r  = build 
		selection = m.forward(selection)

		# after build we set up some variables
		result = None
		alternatives = None

		origin = nearest_node_from_offset(root,atok, selection[0])
		calling_node = search_upwards(origin,ast.Call)
		statement_node, callers = search_upwards_log(origin,ast.stmt,log_targets = ast.Call)
		information = lambda x: info.get_argument_from_call(x,q["argument_index"]-1)
		candidates = sorted_by_source_region(atok, find_matching(statement_node, info.identity(information)))
		every_caller = find_all_nodes(statement_node,(ast.Call))
		

		
		################################################################
		# if no adjective is given
		################################################################
		if q["adjective"] == "None":
			if calling_node:
				result = information(calling_node)
			candidates = [information(x)  for x in tiebreak_on_lca(statement_node,origin, candidates) if x != calling_node]
			result,alternatives = obtain_result(result,candidates)

		################################################################
		# adjective is even
		################################################################
		if q["adjective"] != "None":
			additional_parameters = {}
			if selection[0]!=selection[1]:
				small_root = node_from_range(root,atok,selection)
				additional_parameters["small_root"]=small_root
				print("dumping the small root\n",ast.dump(small_root))
			additional_parameters["special"] = [calling_node]
			if calling_node:
				print(ast.dump(calling_node))
				additional_parameters["penalized"] = [calling_node]
			result, alternatives = adjective_strategy(
				atok=atok,
				root = root,
				adjective_word = q["adjective"],
				level_nodes = every_caller,
				information_nodes = candidates,
				**additional_parameters
			)
			result = information(result) if result else m.forward(v["selection"])
			alternatives  =[ information(x)  for x in alternatives] if alternatives else []



		# translate those nodes back to offsets and forward them through the modification under
		print("\n\nnow finally printing result and alternatives\n\n")
		print( result )
		print(ast.dump( result ) if isinstance( result, ast.AST ) else " not known node")
		print( alternatives )
		result = m.backward(get_source_region(atok, result))
		alternatives = [m.backward(get_source_region(atok,x)) for x in alternatives]
		return result,alternatives




	


		
		

