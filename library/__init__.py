import ast 
from itertools import chain

from PythonVoiceCodingPlugin.third_party.astmonkey import transformers
from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

def make_flat(x):
	return list(chain.from_iterable(x))


def build_tree(code : str):
    atok =  asttokens.ASTTokens(parse=True, source_text= code )
    root = transformers.ParentChildNodeTransformer().visit(atok.tree)
    return root,atok

def get_source_region(atok, element):
    if element is None:
    	return None
    if isinstance(element,ast.AST):
    	return atok.get_text_range(element)         
    else:   
        regions = [atok.get_text_range(node)  for node in element]
        start = min( regions,key = lambda s: s[0])[0]
        end = max( regions,key = lambda s: s[1])[1] 
        return ( start , end) 

def sorted_by_source_region(atok, container):
	return sorted(container,key = lambda x: get_source_region(atok,x))

	


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

