import ast 
from itertools import chain

from astmonkey import transformers
from asttokens import PythonVoiceCodingPlugin.third_party.asttokens as asttokens  

def make_flat(x):
	return list(chain.from_iterable(x))


def build_tree(code : str):
    atok =  asttokens.ASTTokens(parse=True, source_text= code )
    root = transformers.ParentChildNodeTransformer().visit(atok.tree)
    return root,atok

def get_source_region(atok, element):
    if isinstance(element,ast.AST):
        return atok.get_text_range(element)         
    else:
        regions = [atok.get_text_range(node)  for node in element]
        start = min( regions,key = lambda s: s[0])[0]
        end = max( regions,key = lambda s: s[1])[1] 
        return ( start , end) 

def sorted_by_source_region(atok, container):
	return sorted(container,key = lambda x: get_source_region(atok,x))

def nearest_node_from_offset(root,atok,offset):
    converter = atok._line_numbers 
    inside = lambda x,y: (y[0]<=x<y[1])
    orig_token = atok.get_token_from_offset(offset)
    token = orig_token
    while token.string.isspace():
        token = atok.prev_token( token )
    if converter.offset_to_line(offset)[0] != converter.offset_to_line(token.startpos)[0]:
        token = atok.next_token(orig_token)
        while token.string.isspace():
            token = atok.next_token( token )
    s = token.startpos
    candidates =([(node,atok.get_text_range(node)) for node in ast.walk( root ) if not isinstance(node,ast.Module) 
    	and  inside(s,atok.get_text_range(node))])
    return min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0]

def node_from_range(root,atok, r ):
	inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1])
	candidates =([(node,atok.get_text_range(node)) for node in ast.walk( root ) if not isinstance(node,ast.Module) 
    	and  inside(r,atok.get_text_range(node))])
	for x in candidates:
		print(x,atok.get_text_range(x))
	return min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0]
	


def previous_token(atok, origin,extra = False):
	"""returns the preview stoking 
	
	Args:
	    atok (TYPE): Description
	    origin (TYPE): Description
	    extra (bool, optional): Description
	
	Returns:
	    TYPE: Description
	"""
	if not origin:
		return None
	result = atok.prev_token(origin,extra)
	return result if result.index < origin.index else None

def next_token(atok, origin,extra = False):
	if not origin:
		return None
	try:
		result = atok.next_token(origin,extra)
	except:
		result = None
	return result



