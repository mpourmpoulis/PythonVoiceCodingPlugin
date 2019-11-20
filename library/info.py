import ast
from itertools import chain 

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset,make_flat
from PythonVoiceCodingPlugin.library.traverse import match_node, find_all_nodes, match_parent


################################################################
'''
a little bit about this module
This module contains functions that enable us to extract information from nodes.
it is split into four sections

1) some generic functors:
	These enable usto build new information functions while hiding the whole lambda syntax 
2) getters:
	these enable us to "get" information from nodes on a higher level ,
	while trying to minimize exposure to the underlying syntax tree implementation.
3) checkers check if a node satisfies a property(say if its context is store)
4) validators confirm if other root satisfy some property with respect to a given node


'''
################################################################


################################################################################################
################################################################################################
#
# first some funtcors 
#
################################################################################################
################################################################################################

def make_information(c,*arg):
	if arg:
		return lambda x: c(x,*arg)
	return lambda x: c(x)

def identity(information, parameter = None):
	if parameter:
		return lambda x: x if information(x,parameter) else None
	return lambda x: x if information(x) else None


################################################################################################
################################################################################################
#
# some basic checkers 
#
################################################################################################
################################################################################################

def is_store(root):
	return match_node(root,ast.Store)  or (match_node(root,ast.Name) and match_node(root.ctx,ast.Store))
def single(root):
	return match_parent(node,(),ast.Attribute)

def name(root):
	return match_node(root,ast.Name)



################################################################################################
################################################################################################
#
# information extraction function
#
################################################################################################
################################################################################################

def get_name(root):
	return (root if match_node(root,(ast.Name)) else 
	get_name(root.value) if match_node(root,(ast.Attribute )) else None
	)
	
def get_left(root):
	h = {
		ast.BinOp:"left", 
		ast.Compare :"left", 
		ast.Assign  :"targets", 
		ast.AugAssign  :"target", 
		ast.Slice :"lower", 
	}
	return getattr( root ,h[type( root)]) if type( root) in h else None


def get_right(root):
	h = {
		ast.BinOp:"right", 
		ast.Compare :"comparetors", 
		ast.Assign  :"value", 
		ast.AugAssign  :"value", 
		ast.Slice :"upper", 
	}
	return getattr( root ,h[type( root)]) if type( root) in h else None

def get_body(root):
	return root.attribute if match_node(root,(ast.IfExp, ast.If ,ast.For,ast.While, ast.Try)) else None
	


###############################
def get_condition(root):
	return (
		root.test if match_node(root,(ast.If,ast.IfExp,ast.While)) else None
	)

def get_pure_if_condition(root):
	return (
		root.test 
		if match_node(root,(ast.If))  and not (match_parent(root,(ast.If)) and root.parent_field == "orelse")
		else None		
	)

def get_elif_condition(root):
	return (
		root.test 
		if match_node(root,(ast.If))  and match_parent(root,(ast.If)) and root.parent_field == "orelse"
		else None		
	)

def get_comprehension_condition(root):
	return (
		root.ifs  if match_node(root,(ast.comprehension)) else None		
	)

def get_return_value(root):
	return (
		root.value if match_node(root,(ast.Return, ast.Yield,ast.YieldFrom )) else None
	)

# need to revisit
def get_elements(root):
	return (
		root.elts if hasattr(root,elts) else None
	)

def get_context(root):
	return (
		root.ctx if hasattr(root,ctx) else None
	)

def get_key_value(root):
	return (
		zip(root.key,root.value) if match_node(root,(ast.Dict)) else 
		(root.key,root.value) if match_node(root,( ast.DictComp)) else None		
	)

def get_iterable(root):
	return (
		root.iter if match_node(root,(ast.For,ast.comprehension)) else None
	)

def get_iterator(root):
	return (
		root.target if match_node(root,(ast.For,ast.comprehension)) else None
	)


# need to revisit this
def get_body(root):
	return (
		root.body if match_node(root,(ast.Lambda,ast.If,ast.While,ast.With,ast.For,   )) else None
	)


def get_decorator(root):
	return (
		root.decorator_list if match_node(root,(ast.FunctionDef )) else None
	)

def get_item_as(root):
	return (
		root.optional_vars if match_node(root,(ast.withitem)) else 
		[x.optional_vars  for x in root.items] if match_node(root,(ast.With)) else None
		
	)
def get_message(root):
	root.msg if match_node(root,(ast.Assert)) else None
	


################################################################
# 	 arguments from   functional calls
################################################################

#
# we use the version 3.3 of the abstract syntax tree. in version 3.5
# *args,**kwargs do not have fields of their own
#

def get_positional_argument(root,index = None):
	temporary =  root.args if match_node(root,(ast.Call )) else None	
	return (
		(temporary[index] if index and len(temporary)>index else temporary) 
			if  temporary else None
	)

def get_keyword_argument(root,index = None,only_value = True):
	temporary =  root.keywords if match_node(root,(ast.Call )) else None	
	temporary = [x.value  for x in temporary if only_value] if temporary else None
	return (
		(temporary[index] if index and len(temporary)>index else temporary) 
			if  temporary else None
	)

def get_star_argument(root,index = None):
	temporary =  root.starargs if match_node(root,(ast.Call )) else None
	return (
		(temporary[index] if index and len(temporary)>index else temporary) 
			if  temporary else None
	)

def get_keyword_star_argument(root,index = None):
	temporary =  root.kwargs if match_node(root,(ast.Call )) else None
	return (
		(temporary[index] if index and len(temporary)>index else temporary) 
			if  temporary else None
	)


def get_argument_from_call(root, index):
	if  not match_node(root,(ast.Call)):
		return None
	temporary = [
		get_positional_argument(root,None),
		get_keyword_argument(root,None, True),
		[get_star_argument(root,None)],
		[get_keyword_star_argument(root,None)]
	]
	temporary = make_flat([x  for x in temporary if x])
	temporary = [x  for x in temporary if x]
	temporary = sorted(temporary,key= lambda x:x.first_token.startpos)
	# print(" I would regret face", temporary)
	return temporary[index] if temporary and len(temporary)>index else None

################################################################
# 	 arguments from   function definitions
################################################################
def get_argument_from_definition(root,raw = True,index = None):
	if not match_node(root,ast.FunctionDef):
		return None
	x= root.args
	temporary = x.args  + [x.vararg] + x.kwonlyargs + [x.kwarg]
	temporary = [y  for y in temporary if y]
	if raw:
		temporary = [(y.arg if isinstance(y,ast.AST) else y) for y in temporary]
	return temporary[index] if (index is not None) and len(temporary)>index else temporary



def get_sub_index(root,index):
	candidates = []
	if isinstance(root,list):
		if len(root)!=1:
			candidates =  root
		else:
			root = root[0]

	if match_node(root,(ast.List,ast.Tuple,ast.Set)):
		candidates =  root.elts
	elif match_node(root,(ast.Dict)):
		candidates = list(zip(root.keys,root.values))
	elif match_node(root,(ast.BoolOp)) :
		candidates =  root.values
	elif match_node(root,(ast.Compare)) :
		candidates = [root.left] + root.comparators
	elif match_node(root,(ast.Index)):
		candidates = [root.value] 
		if match_node(root.value,(ast.List,ast.Tuple,ast.Set)):
			candidates =  root.value.elts
	elif match_node(root,(ast.Slice)):
		candidates = [root.lower,root.upper, root.step]
	elif match_node(root,(ast.ExtSlice)):
		candidates = root.dims
	
	# in the following cases we Certs deeper in the tree
	if match_node(root,(ast.Subscript)):
		return get_sub_index(root.slice,index)
	if match_node(root,(ast.Expr)):
		return get_sub_index(root.value,index)
	if match_node(root,(ast.UnaryOp)):
		return get_sub_index(root.operand,index)
	if match_node(root,(ast.UnaryOp)):
		return get_sub_index(root.operand,index)

	if index<len(candidates):
		return candidates[index]
	else:
		return None



################################################################
# extracting raw information
################################################################

def get_id(root):
	return (
		root.id if match_node(root,(ast.Name )) else 
		root.attr if match_node(root,(ast.Attribute )) else None		
	)


def get_module_names(root):
	return (
		[root.module] if match_node(root,(ast.ImportFrom)) else 
		[(x.asname if x.asname else x.name)  for x in root.names] if match_node(root,(ast.Import)) else None
	)

def get_imported_value_names(root):
	return (
		[(x.asname if x.asname else x.name)  for x in root.names] if match_node(root,(ast.Import,ast.ImportFrom)) else None
	)


#
def get_raw(root):
	return (
		root.n if match_node(root,(ast.Num)) else 
		root.s if match_node(root,(ast.Str,ast.Bytes )) else 
		root.value if match_node(root,(ast.NameConstant)) else 
		root.id if match_node(root,(ast.Name )) else 
		get_raw(root.func) if match_node(root,(ast.Call )) else 
		root.arg if match_node(root,(ast.keyword)) else 
		root.attr+"."+get_raw(root.value) if match_node(root,(ast.Attribute )) else 
		get_raw(root.value) if match_node(root,(ast.Subscript,ast.Index	)) else 
		(get_raw(root.type),root.name) if match_node(root,(ast.ExceptHandler)) else 
		root.name if match_node(root,(ast.FunctionDef)) else None
						
	)


#################################################################################
#
# validators
#
#################################################################################


################################################################
# validator's concerning function calls
################################################################

def correspond_to_index_in_call(root, index,field,field_index):
	x = get_argument_from_call(root,index)
	print("entering index taking \n",ast.dump(x))
	if not x:
		return False
	if x.parent_field=="value":
		x = x.parent
	print("inside checking for index ",(x.parent_field,x.parent_field_index),(field,field_index))
	return (field, field_index)==(x.parent_field,x.parent_field_index) if x else False



