import ast
import inspect
import re
from itertools import chain 
from urllib.parse import urlparse

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset,make_flat,previous_token,next_token
from PythonVoiceCodingPlugin.library.traverse import match_node, find_all_nodes, match_parent,search_upwards_log
from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

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

def make_information(c,*arg,**kwargs):
	signature = inspect.signature(c)
	if not any(x.kind==x.VAR_KEYWORD  for x in signature.parameters.values()):
		temporary = {x.name  for x in signature.parameters.values()}
		kwargs = {k:v for k,v in kwargs.items() if k in temporary}
	return lambda x: c(x,*arg,**kwargs)


def identity(information, parameter = None):
	if parameter:
		return lambda x: x if information(x,parameter) else None
	return lambda x: x if information(x) else None


def create_fake(root,text,start_position,node_type, **kwargs):
 
	fake_token = asttokens.Token(0,text,0,0,0,
		root.first_token.index,start_position,start_position + len(text))
	fake_node = node_type(**kwargs) 
	fake_node.parent = root.parent
	fake_node.parent_field = root.parent_field
	fake_node.parent_field_index = root.parent_field_index
	fake_node.first_token = fake_token
	fake_node.last_token = fake_token
	fake_node.fake = True
	return fake_node


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
		root.body if match_node(root,(ast.Lambda,ast.If,ast.While,ast.With,ast.For, ast.IfExp)) else None
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

def get_caller(root):
	return root.func if match_node(root,(ast.Call)) else None


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

def get_definition_name(root,atok):
	pass
	




################################################################
# 	 sub indexing functions
################################################################

# https://docs.python.org/3/reference/expressions.html#operator-precedence
def is_of_higher_priority(parent_node,child_node):
	operator_priority = [
		ast.BitOr,ast.BitXor, ast.BitAnd,
		(ast.LShift,ast.RShift),(ast.Add,ast.Sub),
		(ast.Mult, ast.Div, ast.FloorDiv, ast.Mod)   ,
		ast.Pow, 
	]
	print(ast.dump(parent_node),parent_node.op)
	for operator in operator_priority:
		p = match_node(parent_node.op, operator)
		c = match_node(child_node.op, operator)
		print("\ntesting operator ",operator,p,c,"\n")
		if p and not c:
			return True
	return False


def get_subparts_of_binary_operation(root):
	left = (
		[root.left] 
		if not match_node(root.left,ast.BinOp)  or is_of_higher_priority(root,root.left)  
		else get_subparts_of_binary_operation(root.left)
	)
	right = [root.right]
	return left + right


def split_string(s,even_letters = True):
	s = s.strip()
	y = urlparse(s)
	if  not (y.scheme=="" and y.netloc==""):
		return [z  for z in make_flat( [split_string(x,False)  for x in y ]) if z]
	first_attempt = [x  for x in re.split("[., :/]",s) if not x.isspace()]
	if len(first_attempt) > 1:
		return first_attempt
	second_attempt = [x  for x in re.split("[_]",s) if not x.isspace()]
	if len(second_attempt) > 1:
		print(" from second attempt")
		return second_attempt
	# https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python answer from Jossef Harush 
	third_attempt = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
	if len(third_attempt) > 1:
		return third_attempt

	return list(s) if even_letters else [s]

	

def get_subparts_of_string(root,name_mode = False):
	output = []
	start_position = root.first_token.startpos + ( 1 if not name_mode else 0) 
	original  = root.s if not name_mode else root.id
	try :
		splitted = split_string(root.s if not name_mode else root.id,even_letters = False if name_mode else True) 
	except :
		print(" exceptions were thrown")
	index = 0
	print("splitted ",splitted)
	for s in splitted:
		index = original.find(s,index)
		if name_mode:
			fake_node = create_fake(root,s,start_position + index,ast.Name,id = s,ctx = root.ctx)
		else:
			fake_node = create_fake(root,s,start_position + index,ast.Str,s = s)
		output.append(fake_node)
		index += len(s)
	return output if name_mode or len(output)>1 else []




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
	elif match_node(root,(ast.BinOp)) :
		candidates = get_subparts_of_binary_operation(root)
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
	elif match_node(root,(ast.Str)):
		candidates = get_subparts_of_string(root)
	elif match_node(root,(ast.Name)):
		print("whatever ")
		candidates = get_subparts_of_string(root,name_mode = True)
		print("candidates",candidates)
	
	# in the following cases we Certs deeper in the tree
	if match_node(root,(ast.Subscript)):
		return get_sub_index(root.slice,index)
	if match_node(root,(ast.Expr)):
		return get_sub_index(root.value,index)
	if match_node(root,(ast.UnaryOp)):
		return get_sub_index(root.operand,index)
	if match_node(root,(ast.Lambda)):
		return get_sub_index(root.body,index)
	if match_node(root,(ast.Call)):
		return get_sub_index(root.func,index)

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



