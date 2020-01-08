import ast
import inspect
import re
import tokenize

from itertools import chain 
from urllib.parse import urlparse

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,make_flat,previous_token,next_token
from PythonVoiceCodingPlugin.library.traverse import match_node, find_all_nodes, match_parent,search_upwards_log
from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

################################################################
'''
a little bit about this module
This module contains functions that enable us to extract information from nodes.
it is split into four sections

1) some generic functors:
	These enable usto build new information functions while hiding the whole lambda syntax
2) fake creators(introduced in 0.1.0) enable us to play around with fake nodes!
3) checkers check if a node satisfies a property(say if its context is store) 
4) getters:
	these enable us to "get" information from nodes on a higher level ,
	while trying to minimize exposure to the underlying syntax tree implementation.

5) validators confirm if other root satisfy some property with respect to a given node
6) fixers (introduced in 0.1.0) responsible for fixing the first token/last token attributes of nodes and also 
adding some nodes here and there

'''
################################################################


################################################################################################
################################################################################################
#
# first some funtcors 
#
################################################################################################
################################################################################################

def make_information(information,*arg,**kwargs):
	signature = inspect.signature(information)
	if not any(x.kind==x.VAR_KEYWORD  for x in signature.parameters.values()):
		temporary = {x.name  for x in signature.parameters.values()}
		kwargs = {k:v for k,v in kwargs.items() if k in temporary}
	return lambda root: information(root,*arg,**kwargs)


def identity(information, *arg,**kwargs):
	signature = inspect.signature(information)
	if not any(x.kind==x.VAR_KEYWORD  for x in signature.parameters.values()):
		temporary = {x.name  for x in signature.parameters.values()}
		kwargs = {k:v for k,v in kwargs.items() if k in temporary}
	return lambda root: root if information(root,*arg,**kwargs) else None


################################################################################################
################################################################################################
#
# some tools to create fake nodes 
#
################################################################################################
################################################################################################



def create_fake(root,node_type,*,text = "",start_position = 0,
	parent = None,parent_field = None, parent_field_index = None, 
	real_tokens = None, **kwargs):
	if real_tokens  and not isinstance(real_tokens,list):
		real_tokens = [real_tokens]
	if not real_tokens:
		fake_token = asttokens.Token(0,text,0,0,0,
			root.first_token.index,start_position,start_position + len(text))
	fake_node = node_type(**kwargs) 
	fake_node.parent = root.parent if parent is None else parent
	fake_node.parent_field = root.parent_field if parent_field is None else parent_field
	fake_node.parent_field_index = root.parent_field_index if parent_field_index is None else parent_field_index
	fake_node.first_token = fake_token if not real_tokens else real_tokens[0]
	fake_node.last_token = fake_token if not real_tokens else real_tokens[-1] 
	fake_node.fake = True
	return fake_node

def empty_fake(root,start_position):
	return create_fake(root,ast.Name, text = "",start_position = start_position,
		id = "",ctx = ast.Load())

def set_fake(root,name,fake_node):
	fake_name = name + "_fake"
	setattr(root,fake_name,fake_node)
	fields = list(root._fields)
	index = fields.index(name)
	fields.insert(index,fake_name)
	root._fields = tuple(fields)


	
def get_fake(root,name):
	return getattr(root,name + "_fake",None)

def fake_attribute_from_tokens(root,tokens,**kwargs):
	print("entering fake attributes from tokens ",root,tokens,kwargs)
	if len(tokens)==1:
		return create_fake(root,ast.Name ,real_tokens = tokens[-1],
			 id = tokens[-1].string, ctx = ast.Load(),**kwargs)
	top_fake = create_fake(root,ast.Attribute,real_tokens = tokens,ctx = ast.Load(),**kwargs)
	fake_name = create_fake(root,ast.Name ,real_tokens = tokens[-1], 
		parent = top_fake,parent_field = "attr",
		id = tokens[-1].string, ctx = ast.Load())
	set_fake(top_fake,"attr", fake_name)
	top_fake.attr = tokens[-1].string
	top_fake.value = fake_attribute_from_tokens(top_fake,tokens[:-1],
		parent = top_fake,parent_field = "value")
	return top_fake
		


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

def is_decorator(root):
	return getattr(root,"parent_field","")=="decorator_list"

def is_base(root):
	return (
		(
			getattr(root,"parent_field","") == "bases" and match_parent(root,ast.ClassDef)
		)
		or 
		(
		    match_parent(root,ast.keyword)  and match_parent(root.parent,ast.ClassDef)
		)
	)




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

def get_header(root):
	return (
		root.test if match_node(root,(ast.While,ast.If)) else
		root.arguments if match_node(root,(ast.FunctionDef)) else
		root.target if match_node(root,(ast.For)) else None


	)
def get_body(root):
	return root.body if match_node(root,(ast.IfExp, ast.If ,ast.For,ast.While, ast.Try)) else None
	


###############################
def get_condition(root):
	return (
		root.test if match_node(root,(ast.If,ast.IfExp,ast.While,ast.Assert)) else None
	)

def get_else(root):
	return root.orelse if match_node(root,(ast.If,ast.IfExp)) else None

def get_pure_if_condition(root):
	return (
		root.test 
		if match_node(root,(ast.If))  and root.first_token.string=="if"
		else None		
	)

def get_elif_condition(root,atok):
	print("wtf\n",ast.dump(root),[root.first_token.string])
	return (
		root.test 
		if match_node(root,(ast.If))  and root.first_token.string!="if"
		else None		
	)

def get_comprehension_condition(root):
	return (
		root.ifs  if match_node(root,(ast.comprehension)) else None		
	)

def get_comprehension_value(root):
	return (
		root.elt  if match_node(root,(ast.ListComp,ast.SetComp,ast.GeneratorExp)) else 
		[root.key,root.value] if match_node(root,ast.DictComp) else None
	)


def get_return_value(root):
	return (
		(root.value if root.value else empty_fake(root,root.last_token.endpos+1)) if match_node(root,(ast.Return, ast.Yield,ast.YieldFrom )) else None
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

def get_with_items(root):
	return (
		root.items if match_node(root,ast.With) else None
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
	return root.msg if match_node(root,(ast.Assert)) else None

def get_raise_exception(root):
	return root.exc if match_node(root,(ast.Raise)) else None

def get_raise_cause(root):
	return root.cause if match_node(root,(ast.Raise)) else None


def get_exception(root,atok):
	if not match_node(root,ast.ExceptHandler):
		return None
	fix_exception_handler(root,atok)
	return root.type if match_node(root,ast.ExceptHandler) else None

def get_exception_name(root,atok):
	if not match_node(root,ast.ExceptHandler):
		return None
	fix_exception_handler(root,atok)
	data = get_fix_data(root) 
	return data.get("node")

def get_exception_handler(root,atok):
	if not match_node(root,ast.ExceptHandler):
		return None
	fix_exception_handler(root,atok)
	output = [x  for x in [root.type,get_fix_data(root).get("node")] if x]
	print("Output\n\n",output,"\n")
	# print(ast.dump()) 	
	return output if output else empty_fake(root,root.first_token.endpos)


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

def get_keyword_argument(root,index = None,only_value = True,only_keyword = False):
	temporary =  root.keywords if match_node(root,(ast.Call )) else None
	if only_value and not only_keyword:	
		temporary = [x.value  for x in temporary] if temporary else None
	elif only_keyword:
		temporary = [get_fake(x,"arg")  for x in temporary if generic_fix(x,None)] if temporary else None
	return (
		(temporary[index] if index is not None and len(temporary)>index else temporary) 
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
		
	x = root.args
	temporary = x.args  + [x.vararg] + x.kwonlyargs + [x.kwarg]
	temporary = [y  for y in temporary if y]
	if raw:
		temporary = [(y.arg if isinstance(y,ast.AST) else y) for y in temporary]
	return temporary[index] if (index is not None) and len(temporary)>index else temporary

def get_definition_name(root,atok):
	if not match_node(root,ast.FunctionDef):
		return None
	d = atok.find_token(root.first_token,tokenize.NAME,"def") 
	x = next_token(atok,d)	
	if x:
		return create_fake(root,ast.Name,text = x.string,start_position=x.startpos,
			id = x.string,ctx = ast.Store())
	else:
		return None

def get_definition_parameter_name(root,atok):
	if not match_node(root,ast.arg):
		return None 	
	x = root.first_token
	print([x])
	return create_fake(root,ast.Name,start_position = x.startpos,text = x.string,
		id = x.string,ctx = ast.Store())


	
def get_class_name(root,atok):
	if not match_node(root,ast.ClassDef):
		return None
	d = atok.find_token(root.first_token,tokenize.NAME,"class") 
	x = next_token(atok,d)	
	if x:
		return create_fake(root,ast.Name,real_tokens = x,
			id = x.string,ctx = ast.Store())
	else:
		return None


def get_arg(root, atok):
	print("inside get argument ",ast.dump(root) if isinstance(root,ast.AST) else "")
	if not match_node(root,ast.arg):
		if match_node(root,ast.FunctionDef):
			fix_definition(root,atok)
		return None
	if match_parent(root,ast.FunctionDef):
		fix_definition(root.parent,atok)
	elif match_parent(root.parent,ast.FunctionDef):
		fix_definition(root.parent.parent,atok)
	return root

################################################################
# 	 import staff
################################################################

def get_fixed_import(root,atok):
	if not match_node(root,(ast.Import,ast.ImportFrom)):
		return None
	fix_import(root,atok)
	return root

def get_fixed_import_value(root,atok):
	if not match_node(root,(ast.Import,ast.ImportFrom)):
		return None
	fix_import(root,atok)
	print(" siding board value stuff ",ast.dump(root))
	return root.names
	

def get_module(root,atok):
	if not match_node(root,(ast.Import,ast.ImportFrom)):
		return None
	if not already_fixed(root):
		fix_import(root,atok)
	data = get_fix_data(root)
	m = data["module"]
	print("inside get a module date days ",m,"\n")
	output = None
	for t in m:
		if not output:
			output  = create_fake(root,ast.Name,real_tokens=[t,t],
				id=t.string,ctx=ast.Load())
		else:
			output  = create_fake(root,ast.Attribute,real_tokens=[m[0],t],
				value=output,attr=t.string,ctx=ast.Load())

	print("exiting get a module function ",output,"\n")
	return output
	

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


def split_string(s :str ,even_letters = True,only_first = False):
	s = s.strip()
	y = urlparse(s)
	if  not (y.scheme=="" and y.netloc==""):
		return [z  for z in make_flat( [split_string(x,False)  for x in y ]) if z]
	first_attempt = [x  for x in re.split("[., :/]",s) if not x.isspace()]
	if len(first_attempt) > 1:
		return first_attempt
	if only_first:	
		return [s]
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
		if not s:
			continue
		index = original.find(s,index)
		if name_mode:
			fake_node = create_fake(root,ast.Name,start_position = start_position + index,text = s,
				id = s,ctx = root.ctx)
		else:
			fake_node = create_fake(root,ast.Str,start_position = start_position + index,text = s,s = s)
		output.append(fake_node)
		index += len(s)
	return output if name_mode or len(output)>1 else []

def get_subparts_of_attribute(root):
	if not match_node(root,ast.Attribute):
		return None
	l = root.last_token
	if already_fixed(root):
		fake_node = get_fake(root,"attr") 
	else:
		fake_node = create_fake(root,ast.Name,text = l.string,start_position = l.startpos,
		id = l.string,ctx = root.ctx)
	if  match_node(root.value,ast.Attribute):
		return get_subparts_of_attribute(root.value) + [fake_node]
	else:
		return [root.value,fake_node]

def get_subparts_of_alias(root):
	assert already_fixed(root)," I received an node that needs fixing "
	names = get_fix_data(root)["name"]
	print("names",names,"\n")
	left_side =[create_fake(root,ast.Name,real_tokens=x,id=x.string,ctx=ast.Load())  for x in names]
	if root.asname: 
		x = root.last_token
		right_side = create_fake(root,ast.Name,real_tokens=x,id=x.string,ctx=ast.Load())
		return [left_side,right_side]
	else:
		return get_sub_index(left_side,None)
	


def get_sub_index(root,index):
	candidates = []
	if isinstance(root,tuple):
		root = list(root)
	if isinstance(root,list):
		if len(root)!=1:
			candidates =  root
		else:
			root = root[0]
	
	if match_node(root,(ast.List,ast.Tuple,ast.Set)):
		candidates =  root.elts
	elif match_node(root,(ast.Dict)):
		candidates = list(zip(root.keys,root.values))
		if len(candidates)==1:
			candidates = list(candidates[0])
	elif match_node(root,(ast.BoolOp)) :
		candidates =  root.values
	elif match_node(root,(ast.BinOp)) :
		candidates = get_subparts_of_binary_operation(root)
	elif match_node(root,(ast.Compare)) :
		candidates = [root.left] + root.comparators
	elif match_node(root,(ast.Subscript)):
		candidates = [root.value,root.slice]
	elif match_node(root,(ast.Slice)):
		candidates = [root.lower,root.upper, root.step]
	elif match_node(root,(ast.ExtSlice)):
		candidates = root.dims
	elif match_node(root,(ast.Str)):
		candidates = get_subparts_of_string(root)
	elif match_node(root,(ast.Name)):
		candidates = get_subparts_of_string(root,name_mode = True)
	elif match_node(root,ast.Attribute):
		candidates = get_subparts_of_attribute(root)
	elif match_node(root,ast.IfExp):
		candidates = [root.body,root.test,root.orelse]
	elif match_node(root,ast.withitem):
		candidates = [root.context_expr,root.optional_vars]
	elif match_node(root,(ast.ListComp,ast.SetComp,ast.GeneratorExp)):
		candidates = [root.elt] + root.generators
	elif match_node(root,ast.DictComp):
		candidates = [[root.key,root.value]] + root.generators
	elif match_node(root,ast.alias):
		candidates = get_subparts_of_alias(root)
	elif match_node(root,ast.withitem):
		candidates = [root.context_expr,root.optional_vars] if root.optional_vars else [root.context_expr]
	elif match_node(root,ast.With):
		candidates = root.items
	elif match_node(root,(ast.ExceptHandler)):
		if root.name is not None and get_fix_data(root).get("node"):
			candidates = [root.type,get_fix_data(root).get("node")]
		else:
			candidates = [root.type]

	
	# in the following cases we Certs deeper in the tree
	if match_node(root,(ast.Index)):
		return get_sub_index(root.value,index)
	if match_node(root,(ast.Expr)):
		return get_sub_index(root.value,index)
	if match_node(root,(ast.UnaryOp)):
		return get_sub_index(root.operand,index)
	if match_node(root,(ast.Lambda)):
		return get_sub_index(root.body,index)
	if match_node(root,(ast.Call)):
		return get_sub_index(root.func,index)
	if match_node(root,(ast.ExceptHandler)):
		if root.name is None:
			return get_sub_index(root.type,index)
	if match_node(root,(ast.Import,ast.ImportFrom)):
		candidates = root.names
		if len(candidates)==1:
			temporary = get_sub_index(candidates[0],index)
			print(temporary)
			if temporary:
				return temporary



	if index is None:
		return candidates
	elif index<len(candidates):
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


#################################################################################
#
# fixers
#
#################################################################################

################################################################
# first some general-purpose functions regarding fixing
################################################################

def mark_fixed(root):
	root._has_been_fixed = True

def mark_under_fixing(root):
	root._is_under_fixing = True

def needs_fix(root):
	pass

def already_fixed(root):
	return hasattr(root,"_has_been_fixed")

def under_fixing(root):
	return hasattr(root,"_is_under_fixing")

def fix_pipeline(root,atok):
	mark_under_fixing(root)
	if generic_fix(root,atok):
		mark_fixed(root)
		return True
	else:
		return False

def store_fix_data(root,data):
	root._fix_metadata = data

def get_fix_data(root):
	return getattr(root,"_fix_metadata",{})

################################################################
# some fixers concerning imports
################################################################


def fix_import(root,atok):
	if already_fixed(root):
		return True
	data = {}
	print("\n\n enduring fixing board statement\n")
	token = root.first_token
	data["module"] = []
	if match_node(root,ast.ImportFrom):
		if root.module  is not None:
			for s in split_string(root.module,only_first = True):
				token = atok.find_token(token,tokenize.NAME,s)
				data["module"].append(token)
	for name in root.names:
		if name.name=="*":
			i = atok.find_token(root.first_token,tokenize.NAME,"import")
			name.first_token = next_token(atok,i)
			name.last_token = next_token(atok,i)
		else:
			stack = []
			local_data = {}
			for s in split_string(name.name,only_first = True):
				token = next_token(atok,token)
				token = atok.find_token(token,tokenize.NAME,s)
				stack.append(token)
			local_data["elements"] = stack
			name.first_token = stack[0]			
			print("matching name ",name.name," into ",token.string,"\n")
			if name.asname:
				token = next_token(atok,token)
				token = atok.find_token(token,tokenize.NAME,name.asname)
			name.last_token = token
			store_fix_data(name,{"name":stack})
			fix_pipeline(name,atok)
	store_fix_data(root,data)
	if match_node(root,ast.ImportFrom) and data:
		print("I made up to hear with tokens",data["module"])
		fake_module = fake_attribute_from_tokens(root,data["module"],parent = root,parent_field="module")
		set_fake(root,"module",fake_module)
		mark_fixed(fake_module)
	mark_fixed(root)
	return True

def fix_alias(root,atok):
	if already_fixed(root):
		return True
	if under_fixing(root) or  fix_import(root.parent,atok):
		names = get_fix_data(root)["name"]
		name_nodes = [
			create_fake(root,ast.Name,real_tokens=x,
				parent = root,parent_field="name",parent_field_index = i,
				id=x.string,ctx=ast.Load())  
			for i,x in enumerate(names)]
		set_fake(root,"name",name_nodes)
		mark_fixed(name)
		print("field",root._fields)
		return True
	else:
		return False


def fix_argument(root,atok,token = None):
	print("enduring fix argument ",root,root.parent_field,atok,[token])
	if already_fixed(root):
		return token
	if token is None:
		return None
	mark_fixed(root)

	root.first_token = token

	fake_node = create_fake(root,ast.Name, real_tokens=token,id = token.string,ctx = ast.Load())
	set_fake(root,"arg",fake_node)
	if getattr(root,"annotation",False):
		root.last_token = root.annotation.last_token
		return root.annotation.last_token
	else:
		root.last_token = token
		return token


def fix_definition(root,atok):
	print("enduring fix definition ",root,atok,get_fake(root.args,"kwarg"))
	if already_fixed(root):
		print(" already fixed")
		return True

	# there is a discrepancy between the 3.3 and 3.4 versions of the abstract syntax tree
	# in 3.3 the variable arguments and the variable keyboard arguments are stored in a little bit differently
	x = root.args
	print([x.first_token,x.last_token])

	if x.vararg and not get_fake(x,"vararg"):
		print(" I am in the process of fixing the viable arguments ",x.vararg,x.varargannotation)
		fake_node = create_fake(x,ast.arg,text = "",start_position = 0,
			parent = x,parent_field = "vararg", 
			arg=x.vararg,annotation=x.varargannotation)
		set_fake(x,"vararg",fake_node)
	if x.kwarg and not get_fake(x,"kwarg"):
		print(" I am in the process of fixing the keyword viable arguments ",x.kwarg,x.kwargannotation)
		fake_node = create_fake(x,ast.arg,text = "",start_position = 0,
			parent = x,parent_field = "kwarg", 
			arg=x.kwarg,annotation=x.kwargannotation)
		set_fake(x,"kwarg",fake_node)
	
	# I think the following might be done easier with more iter tools library
	token = root.first_token
	token = atok.find_token(token,tokenize.NAME,"def")
	token = next_token(atok,token )
	print("token ",[token])
	for i,j in zip(x.args,[None]*(len(x.args)-len(x.defaults))+x.defaults):
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)
		if j:
			token = j.last_token
		print("token ",[token])
	if x.vararg:
		i=get_fake(x,"vararg")
		print("viable argument problem ")
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)

	for i,j in zip(x.kwonlyargs,x.kw_defaults):
		print("you word only problem")
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)
		if j:
			token = j.last_token
	if x.kwarg:
		i=get_fake(x,"kwarg")
		print("keyword viable arguments problem",[token],"\n\n")
		token = next_token(atok,token)
		print("before searching for the argument that Tolkien was \n",[token],"\n")
		token = atok.find_token(token,tokenize.NAME,i.arg)
		print("After that Tolkien was \n",[token],"\n")
		fix_argument(i,atok,token)

	# fixing x, the arguments
	temporary =[getattr(x,"first_token") for x in ast.iter_child_nodes(x)] + [getattr(x,"last_token") for x in ast.iter_child_nodes(x)] 
	temporary = sorted([x  for x in temporary if x],key=lambda x: x.index)
	if temporary:
		x.first_token = temporary[0]
		x.last_token = temporary[-1]
	mark_fixed(root)
	return True

def fix_exception_handler(root,atok):
	if already_fixed(root):
		return  True
	if not root.type or not root.name:
		mark_fixed(root)
		return True
	token = root.type.last_token
	print(" inside fixing before finding the token",[token,root.type.first_token])
	token = atok.find_token(next_token(atok,token),tokenize.NAME, root.name)
	f = root.type.first_token
	f = atok.find_token(previous_token(atok,f),tokenize.NAME, "except",reverse = True)
	print(" in the exception Hunter token",[token])
	fake_name_node = create_fake(root,ast.Name,real_tokens =  token,id = token.string,ctx = ast.Load())
	store_fix_data(root,fake_name_node)
	set_fake(root,"name",fake_name_node)
	root.first_token=root.type.first_token
	root.last_token = token
	mark_fixed(root)
	return True

def fix_attribute(root,atok):
	l = root.last_token
	fake_node = create_fake(root,ast.Name,real_tokens = l,
		parent = root,parent_field = "attr",
		id = l.string,ctx = root.ctx)
	print("I failed test here \n\nself.man")
	set_fake(root,"attr",fake_node)
	if match_node(root.value,ast.Attribute):
		fix_attribute(root.value,atok)
	mark_fixed(root)


def fix_keyword(root,atok):
	set_fake(root,"arg",create_fake(root,ast.Name,real_tokens=root.first_token,
		parent = root,parent_field = "arg",
		id=root.first_token.string ,ctx = ast.Load()))
	mark_fixed(root)


def generic_fix(root,atok):
	temporary = {
		(ast.Import,ast.ImportFrom):fix_import,
		ast.alias: fix_alias,
		ast.ExceptHandler: fix_exception_handler,
		ast.Attribute:fix_attribute, 
		ast.FunctionDef:fix_definition,
		ast.arg:fix_argument,  
		ast.keyword:fix_keyword,
	}
	print(type(root),root,match_node(root,ast.FunctionDef))
	try:
		print("")
		fixer = next(v for k,v in temporary.items() if match_node(root,k))
	except:
		print("I failed with",root)
		return False
	fixer(root,atok)
	return True




def dummy():
	pass


########################################