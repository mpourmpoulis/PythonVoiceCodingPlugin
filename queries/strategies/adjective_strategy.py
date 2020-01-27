import ast

from PythonVoiceCodingPlugin.library import sorted_by_source_region,get_source_region
from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.queries.utility import ResultAccumulator,reestablish_priority
from PythonVoiceCodingPlugin.queries.strategies.primitives import root_level_order,root_lexical_order, child_level_older, root_everything

translate_adjective = {
	"first":1,"second":2,"third":3,"fourth":4,"fifth":5,
	"sixth":6, "seventh":7, "eighth":8, "ninth":9,
	"last":0,"second last":-1,"third last":-2,"fourth last":-3, 
}



def adjective_strategy(
	atok = None,	root = None,	small_root = None,
	small_special = [],	special = [],	level_nodes = [],
	information_nodes = [],	adjective_word = None,
	priority = {},	penalized = [], penalty = 2, only_information = False,
	try_alternative = False, additional_level_nodes = [], constrained_space = None,
	**kwargs):

	# we cannot operate without those parameters
	# removed  level_nodes
	if not atok  or not root  or not information_nodes  or not adjective_word:
		return None, None


	_priority = {
		"small_child_level":1,
		"child_level":2,
		"small_root_level":3,
		"root_level":4,
		"small_root_lexical_order": 5,
		"root_lexical_order": 6,
		"everything":7,
		"alternative_everything":8,
	}
	priority = reestablish_priority(_priority, priority)

	# initialize some variables and sorting the data 
	index = translate_adjective[adjective_word]-1
	accumulator = ResultAccumulator(penalized, penalty)
	level = LevelVisitor(root,level_nodes,atok,information_nodes)
	lca = LCA(root)
	if small_root:
		small_level = LevelVisitor(small_root,level_nodes,atok,information_nodes)
	special = sorted_by_source_region(atok, special)
	small_special = sorted_by_source_region(atok, small_special)
	level_nodes = sorted_by_source_region(atok, level_nodes)
	information_nodes = sorted_by_source_region(atok,information_nodes)
	# print("information_nodes",information_nodes,"\n")
    ################################################################
	# small root level and lexical order strategy
	################################################################
	if small_root:
		root_level_order(accumulator,small_root,
			small_level,index,
			only_information = only_information,
			priority = priority["small_root_level"],
			penalty = 2
		)

		root_lexical_order(accumulator,small_root,
			level_nodes,information_nodes,index,
			only_information=only_information,
			priority = priority["small_root_lexical_order"],
			penalty = 2,
			lca = lca,
			constrained_space = constrained_space
		)
	# print("small_root",small_root)
	
    ################################################################
	# root level and lexical order strategy
	################################################################
	# print("\nDEBUGGING after wrote stuf 0f\n", accumulator.history)
	root_level_order(accumulator,root,
		level,index,
		only_information = only_information,
		priority = priority["root_level"],
		penalty = 2
	)
	# print("\nDEBUGGING after wrote stuff 1\n", accumulator.history)
	root_lexical_order(accumulator,root,
		level_nodes,information_nodes,index,
		only_information=only_information,
		priority = priority["root_lexical_order"],
		penalty = 2,
		lca = None,
		constrained_space = constrained_space
	)
	# print("\nDEBUGGING after wroteup 20\n", accumulator.history)
	################################################################
	#  strategies for spacial and very special
	################################################################
	if small_special:
		child_level_older(accumulator,small_special,small_level,index,only_information=only_information,priority = priority["small_child_level"])
	if special:
		child_level_older(accumulator,special,level,index,only_information=only_information,priority = priority["child_level"])

	################################################################
	# just_throw_everything_inside
	################################################################
	root_everything(accumulator,level,set(information_nodes),index,priority["everything"],False)
	if try_alternative:
		alternative_level = LevelVisitor(root,set(level_nodes).union(set(additional_level_nodes)),atok,level_nodes)
		root_everything(accumulator,alternative_level,set(information_nodes), index, priority["alternative_everything"],True)


	# print("\nDEBUGGING\n", accumulator.history)
	return accumulator.get_result()




	
	






