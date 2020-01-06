import ast

from PythonVoiceCodingPlugin.third_party.asttokens import asttokens
from PythonVoiceCodingPlugin.library.info import generic_fix 

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

def node_from_range_old(root,atok, r ):
	inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1])
	candidates =([(node,atok.get_text_range(node)) for node in ast.walk( root ) if not isinstance(node,ast.Module) 
    	and  inside(r,atok.get_text_range(node))])
	print("inside note from range \n")
	for x in candidates:
		print(x,atok.get_text_range(x))
	print("outside note from range \n",min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0])

	return min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0]


def node_from_range_new(root,atok,r):
    print(" inside the new note from range\n",root)
    inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1])
    generic_fix(root,atok)
    for child in ast.iter_child_nodes(root):
        if inside(r,atok.get_text_range(child)):
            return node_from_range_new(child,atok,r)
    return root


def node_from_range(root,atok, r ):
    # return node_from_range_old(root,atok,r)
    return node_from_range_new(root,atok,r)








