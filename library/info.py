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
		fake_token = asttokens.Token(0,text,(0,0),(0,0),"",
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

def check_fake(root):
	return getattr(root,"fake",False)
	
def get_fake(root,name):
	return getattr(root,name + "_fake",None)

def fake_attribute_from_tokens(root,tokens,**kwargs):
	if not tokens:
		return None
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
	return match_parent(root,(),ast.Attribute)

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

def is_default_value(root):
	return getattr(root,"parent_field","") in ["kw_defaults","defaults"] and root  is  not None

def is_method(root):
	if match_node(root,ast.FunctionDef) and match_parent(root,ast.ClassDef):
		return root
################################################################################################
################################################################################################
#
# information extraction function
#
################################################################################################
################################################################################################
def get_decorator_text(root,atok,everything):
	if not is_decorator(root):
		return None
	if everything:
		return  atok.get_text(root)
	else:
		if match_node(root,ast.Call):
			return atok.get_text(root.func)




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

def get_weak_header(root,atok):
	return (
		root.test if match_node(root,(ast.While,ast.If)) else
		root.arguments if match_node(root,(ast.FunctionDef)) else
		[root.target,root.iter] if match_node(root,(ast.For)) else 
		root.bases + root.keywords if match_node(root,(ast.ClassDef)) else 
		root.items if match_node(root,(ast.With)) else 
		root.type if match_node(root,(ast.ExceptHandler)) else None
	)
	


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
		root.elts if hasattr(root,"elts") else None
	)

def get_context(root):
	return (
		root.ctx if hasattr(root,"ctx") else None
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

#########################################################################
# stuff for small regions
#########################################################################

# Extracting things from subscript
def get_subscript_body(root):
	return  root.value if match_node(root,ast.Subscript) else None

def get_subscript_key(root):
	return (
		root.slice if match_node(root,ast.Subscript) else None
	)

def get_slice_lower(root):
	return root.lower if match_node(root,ast.Slice) else None


def get_slice_upper(root):
	return root.upper if match_node(root,ast.Slice) else None

def get_slice_step(root):
	return root.step if match_node(root,ast.Slice) else None





# Extracting Member And Container
def get_member_check(root):
	return root.left if match_node(root,ast.Compare)  and all([match_node(x,(ast.In,ast.NotIn)) for x in root.ops]) else None

def get_container_check(root):
	return root.comparators[-1] if match_node(root,ast.Compare)  and all([match_node(x,(ast.In,ast.NotIn)) for x in root.ops]) else None

def get_membership(root):
	return root if match_node(root,ast.Compare)  and all([match_node(x,(ast.In,ast.NotIn)) for x in root.ops]) else None


# Extracting Identity Left And Right
def get_identity_check_left(root):
	return root.left if match_node(root,ast.Compare)  and all([match_node(x,(ast.Is,ast.IsNot)) for x in root.ops]) else None

def get_identity_check_right(root):
	return root.comparators[-1] if match_node(root,ast.Compare)  and all([match_node(x,(ast.Is,ast.IsNot)) for x in root.ops]) else None

def get_identity_check(root):
	return root if match_node(root,ast.Compare)  and all([match_node(x,(ast.Is,ast.IsNot)) for x in root.ops]) else None

# Extract Left Middle And Right from numerical comparisons
def get_comparison_left_side(root):
	return root.left if match_node(root,ast.Compare) else None

def get_comparison_right_side(root):
	return root.comparators[-1] if match_node(root,ast.Compare) else None

def get_comparison_middle(root):
	return root.comparators[0] if match_node(root,ast.Compare) and len(root.comparators)==2 else None


# Extract Left Middle and Right from arithmetical operations

def get_arithmetic(root):
	if not match_node(root,ast.BinOp)  or match_parent(root,ast.BinOp):
		return None
	return root
	
def get_arithmetic_left(root):
	if not match_node(root,ast.BinOp)  or match_parent(root,ast.BinOp):
		return None
	items = get_sub_index(root,None)
	if len(items)>=1:
		return items[0]
	return None

def get_arithmetic_right(root):
	if not match_node(root,ast.BinOp) or match_parent(root,ast.BinOp):
		return None
	items = get_sub_index(root,None)
	if len(items)>=2:
		return items[-1]
	return None

def get_arithmetic_middle(root):
	if not match_node(root,ast.BinOp) or match_parent(root,ast.BinOp):
		return None
	items = get_sub_index(root,None)
	if len(items)==3:
		return items[1]
	return None


# Extract Left Middle Right from Boolean expressions
def get_boolean(root):
	if not match_node(root,ast.BoolOp)  or match_parent(root,ast.BoolOp):
		return None
	return root


def get_boolean_left(root):
	if not match_node(root,ast.BoolOp)  or match_parent(root,ast.BoolOp):
		return None
	items = root.values
	if len(items)>=1:
		return items[0]
	return None

def get_boolean_right(root):
	if not match_node(root,ast.BoolOp)  or match_parent(root,ast.BoolOp):
		return None
	items = root.values
	if len(items)>=2:
		return items[-1]
	return None

def get_boolean_middle(root):
	if not match_node(root,ast.BoolOp)  or match_parent(root,ast.BoolOp):
		return None
	items = root.values
	if len(items)==3:
		return items[1]
	return None

def get_boolean_and(root):
	return root if match_node(root,ast.BoolOp) and match_node(root.op,ast.And) else None


def get_boolean_or(root):
	return root if match_node(root,ast.BoolOp) and match_node(root.op,ast.Or) else None

##########################################################################
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
	return get_fake(root,"name")

def get_exception_handler(root,atok):
	if not match_node(root,ast.ExceptHandler):
		return None
	fix_exception_handler(root,atok)
	output = [x  for x in [root.type,get_fake(root,"name")] if x]
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
	if temporary:
		try : 
			return temporary[index]
		except (IndexError,TypeError): 
			return temporary
	# return (
	# 	(temporary[index] if index and len(temporary)>index else temporary) 
	# 		if  temporary else None
	# )

def get_keyword_argument(root,index = None,only_value = True,only_keyword = False):
	temporary =  root.keywords if match_node(root,(ast.Call )) else None
	if only_value and not only_keyword:	
		temporary = [x.value  for x in temporary] if temporary else None
	elif only_keyword:
		temporary = [get_fake(x,"arg")  for x in temporary if generic_fix(x,None)] if temporary else None
	if temporary:
		try : 
			return temporary[index]
		except (IndexError,TypeError): 
			return temporary

	# return (
	# 	(temporary[index] if index is not None and len(temporary)>index else temporary) 
	# 		if  temporary else None
	# )

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
	try : 
		return temporary[index]
	except :
		return None
	# return temporary[index] if temporary and len(temporary)>index else None



def get_caller(root):
	return root.func if match_node(root,(ast.Call)) else None

def get_argument_from_empty_call(root):
	if  not match_node(root,(ast.Call)):
		return None

	if get_argument_from_call(root,0):
		return None 
	return create_fake(root,ast.Name,
		text = "",start_position = root.last_token.startpos,
		parent = root,parent_field = "args"
	)

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
	if not already_fixed(root):
		generic_fix(root,atok)	
	assert already_fixed(root),"Definition has not been fixed"
	return get_fake(root,"name")




def get_definition_parameter_name(root,atok):
	if not match_node(root,ast.arg):
		return None 	
	if not already_fixed(root):
		generic_fix(root,atok)	
	assert already_fixed(root),"Arg has not been fixed"
	return get_fake(root,"arg")


	
def get_class_name(root,atok):
	if not match_node(root,ast.ClassDef):
		return None
	if not already_fixed(root):
		generic_fix(root,atok)	
	assert already_fixed(root),"Class Name has not been fixed"
	return get_fake(root,"name")


def get_arg_from_definition(root, atok):
	if not match_node(root,ast.arg):
		if match_node(root,ast.FunctionDef):
			fix_definition(root,atok)
		return None
	if match_parent(root,ast.FunctionDef):
		fix_definition(root.parent,atok)
	elif match_parent(root.parent,ast.FunctionDef):
		fix_definition(root.parent.parent,atok)
	else:
		return None
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
	return root.names
	

def get_module(root,atok):
	if not match_node(root,(ast.Import,ast.ImportFrom)):
		return None
	if not already_fixed(root):
		fix_import(root,atok)
	assert already_fixed(root),"inside get_module I received an node that is not fixed" 
	return get_fake(root,"module")


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
		return second_attempt
	# https://stackoverflow.com/questions/29916065/how-to-do-camelcase-split-in-python answer from Jossef Harush 
	third_attempt = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', s)).split()
	if len(third_attempt) > 1:
		return third_attempt

	return list(s) if even_letters else [s]

	

def get_subparts_of_string(root,name_mode = False):
	output = []
	if name_mode:
		start_position = 0
	else:
		start_position = 1
		if not check_fake(root):
			x = root.first_token.string
			y1 = x.find("'")
			y2 = x.find("\"")
			if y1>=0 and y2>=0:
				z = min(y1,y2)
			elif y1>=0:
				z = y1
			elif y2>=0:
				z = y2
			else:
				raise Exception("problem with splitting a string , there is no beginning!")
			try : 
				if x[z]==x[z+1]==x[z+2]:
					z = z + 2
			except :
				pass
			start_position += z
	start_position += root.first_token.startpos
	original  = root.s if not name_mode else root.id
	try :
		splitted = split_string(root.s if not name_mode else root.id,even_letters = False if name_mode else True) 
	except :
		print(" exceptions were thrown")
	index = 0
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
	assert already_fixed(root)," I received an node that needs fixing " + ast.dump(root)
	names = get_fix_data(root).get("name")
	if not names:
		return []
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
			# root = root[0]
			return get_sub_index(root[0],index)
	
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
		if root.name is not None and get_fake(root,"name"):
			candidates = [root.type,get_fake(root,"name")]
		else:
			candidates = [root.type]
	elif match_node(root,(ast.keyword)):
		candidates = [get_fake(root,"arg"), root.value]
	elif match_node(root,(ast.FunctionDef)):
		candidates = root.body


	
	
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
	if match_node(root,(ast.arg )):
		if root.annotation:
			candidates = [get_fake(root,"arg"), root.annotation]
		else:
			return get_sub_index(get_fake(root,"arg"),index)




	if index is None:
		return candidates
	else:
		try : 
			return candidates[index]
		except IndexError:
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
	if not x:
		return False
	if x.parent_field=="value":
		x = x.parent
	# print("inside checking for index ",(x.parent_field,x.parent_field_index),(field,field_index))
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
	if root:
		root._has_been_fixed = True

def mark_under_fixing(root):
	if root:
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
	token = root.first_token
	data["module"] = []
	if match_node(root,ast.ImportFrom):
		starting_token = token
		if root.module  is not None:
			for s in split_string(root.module,only_first = True):
				token = atok.find_token(token,tokenize.NAME,s)
				data["module"].append(token)
	for name in root.names:
		if name.name=="*":
			i = atok.find_token(root.first_token,tokenize.NAME,"import")
			name.first_token = next_token(atok,i)
			name.last_token = next_token(atok,i)
			# fake_name = create_fake(name, ast.Name,real_tokens = root.first_token,
			# 	parent = name,parent_field = "name"
			# 	id = root.first_token.string,ctx = ast.Load()
			# )
			mark_fixed(name)
			# set_fake()
		else:
			stack = []
			local_data = {}
			for s in split_string(name.name,only_first = True):
				token = next_token(atok,token)
				token = atok.find_token(token,tokenize.NAME,s)
				stack.append(token)
			local_data["elements"] = stack
			name.first_token = stack[0]			
			if name.asname:
				token = next_token(atok,token)
				token = atok.find_token(token,tokenize.NAME,name.asname)
			name.last_token = token
			store_fix_data(name,{"name":stack})
			fix_pipeline(name,atok)
	store_fix_data(root,data)
	if match_node(root,ast.ImportFrom):
		if data["module"]:
			fake_module = fake_attribute_from_tokens(root,data["module"],parent = root,parent_field="module")
			set_fake(root,"module",fake_module)
			def update_first(root,token):
				if match_node(root,ast.Attribute):
					root.first_token = token
					update_first(root.value,token)
			update_first(fake_module,next_token(atok,starting_token))
			mark_fixed(fake_module)
		else:
			fake_module = create_fake(root,ast.Name,
				text = "." * root.level,start_position = next_token(atok,starting_token).startpos,
				parent = root,parent_field="module",
				id = "." * root.level,ctx=ast.Load() 
			)
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
		return True
	else:
		return False


def fix_argument(root,atok,token = None):
	if already_fixed(root):
		return token
	# the following check was introduced to work around issue #17
	if not match_node(root.parent.parent,ast.FunctionDef):
		return None
	if token is None:
		fix_definition(root.parent.parent,atok)
		if not already_fixed(root):
			raise Exception("these ARG node has not been marked as fixed")
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

def fix_argument_list(root,atok):
	if not  match_node(root,ast.arguments):
		return False
	if already_fixed(root) or match_node(root.parent,(ast.FunctionDef)) and fix_definition(root.parent,atok):
		return True
	return False


def fix_definition(root,atok):
	if already_fixed(root):
		return True
	# there is a discrepancy between the 3.3 and 3.4 versions of the abstract syntax tree
	# in 3.3 the variable arguments and the variable keyboard arguments are stored in a little bit differently
	x = root.args

	if x.vararg and not get_fake(x,"vararg"):
		fake_node = create_fake(x,ast.arg,text = "",start_position = 0,
			parent = x,parent_field = "vararg", 
			arg=x.vararg,annotation=x.varargannotation)
		set_fake(x,"vararg",fake_node)
	if x.kwarg and not get_fake(x,"kwarg"):
		fake_node = create_fake(x,ast.arg,text = "",start_position = 0,
			parent = x,parent_field = "kwarg", 
			arg=x.kwarg,annotation=x.kwargannotation)
		set_fake(x,"kwarg",fake_node)
	
	# I think the following might be done easier with more iter tools library
	token = root.first_token
	token = atok.find_token(token,tokenize.NAME,"def")
	token = next_token(atok,token )

	name_token = token
	if match_node(root,ast.FunctionDef):
		fake_node = create_fake(root,ast.Name,real_tokens = token,
			parent = root,parent_field = "name", 
			id= token.string,ctx = ast.Load())
		set_fake(root,"name",fake_node)

	for i,j in zip(x.args,[None]*(len(x.args)-len(x.defaults))+x.defaults):
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)
		if j:
			token = j.last_token
	if x.vararg:
		i=get_fake(x,"vararg")
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)

	for i,j in zip(x.kwonlyargs,x.kw_defaults):
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)
		if j:
			token = j.last_token
	if x.kwarg:
		i=get_fake(x,"kwarg")
		token = next_token(atok,token)
		token = atok.find_token(token,tokenize.NAME,i.arg)
		fix_argument(i,atok,token)

	# fixing x, the arguments
	temporary =[getattr(x,"first_token") for x in ast.iter_child_nodes(x)] + [getattr(x,"last_token") for x in ast.iter_child_nodes(x)] 
	temporary = sorted([x  for x in temporary if x],key=lambda x: x.index)
	if temporary:
		x.first_token = temporary[0]
		x.last_token = temporary[-1]
	else:
		token = next_token(atok,name_token)
		x.first_token = x.last_token = asttokens.Token(0,"",(token.start[0],token.start[1]+1),(token.start[0],token.start[1]+1),"",
			token.index,token.startpos+1,token.startpos+1)
	mark_fixed(root)
	return True

def fix_exception_handler(root,atok):
	if already_fixed(root):
		return  True
	if not root.type or not root.name:
		mark_fixed(root)
		return True
	
	token = root.type.last_token
	token = atok.find_token(next_token(atok,token),tokenize.NAME, root.name)
	f = root.type.first_token
	f = atok.find_token(previous_token(atok,f),tokenize.NAME, "except",reverse = True)
	fake_name_node = create_fake(root,ast.Name,real_tokens =  token,id = token.string,ctx = ast.Load(),
		parent = root,parent_field = "name")
	set_fake(root,"name",fake_name_node)
	# root.first_token=root.type.first_token
	# root.last_token = token
	mark_fixed(root)
	return True

def fix_attribute(root,atok):
	if already_fixed(root):
		return True
	l = root.last_token
	fake_node = create_fake(root,ast.Name,real_tokens = l,
		parent = root,parent_field = "attr",
		id = l.string,ctx = root.ctx)
	set_fake(root,"attr",fake_node)
	if match_node(root.value,ast.Attribute):
		fix_attribute(root.value,atok)
	mark_fixed(root)


def fix_keyword(root,atok):
	if not already_fixed(root):
		set_fake(root,"arg",create_fake(root,ast.Name,real_tokens=root.first_token,
			parent = root,parent_field = "arg",
			id=root.first_token.string ,ctx = ast.Load())
		)
	mark_fixed(root)


def fix_class(root,atok):
	if already_fixed(root):
		return True
	d = atok.find_token(root.first_token,tokenize.NAME,"class") 
	x = next_token(atok,d)	
	if x:
		fake_node  = create_fake(root,ast.Name,real_tokens = x,
			parent = root,parent_field = "name",
			id = x.string,ctx = ast.Store())
		set_fake(root,"name",fake_node)
		mark_fixed(root)
	else:
		return None
	

fixable = {
	ast.Import:fix_import,
	ast.ImportFrom:fix_import,
	ast.alias: fix_alias,
	ast.ExceptHandler: fix_exception_handler,
	ast.Attribute:fix_attribute, 
	ast.FunctionDef:fix_definition,
	ast.arg:fix_argument, 
	ast.arguments:fix_argument_list,  
	ast.keyword:fix_keyword,
	ast.ClassDef:fix_class, 
}


def generic_fix(root,atok = None):
	fixer = fixable.get(type(root))
	if not fixer:
		return True
	try :
		fixer(root,atok)
	except :
		raise
		return False
	return True




def dummy():
	pass


########################################