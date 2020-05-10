import ast

from PythonVoiceCodingPlugin.third_party.asttokens import asttokens


from PythonVoiceCodingPlugin.library import get_source_region,previous_token,next_token 
from PythonVoiceCodingPlugin.library.info import generic_fix,get_sub_index 
from PythonVoiceCodingPlugin.library.traverse import match_node 

def nearest_node_from_offset(root,atok,offset,special=False):
    converter = atok._line_numbers 
    original_token = atok.get_token_from_offset(offset)
    token = original_token
    while token.string.isspace() or not token.string:
        token = previous_token(atok,token)
    if converter.offset_to_line(offset)[0] != converter.offset_to_line(token.startpos)[0]:
        following = next_token(atok,original_token)
        while following  and following.string.isspace():
            token = following
            following = next_token(atok,token)
        if following:
            token = following
    s = token.startpos
    r = node_from_range(root,atok,(s,s),special= special,lenient = True)
    return r

def node_from_range_old(root,atok, r ):
	inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1])
	candidates =([(node,atok.get_text_range(node)) for node in ast.walk( root ) if not isinstance(node,ast.Module) 
    	and  inside(r,atok.get_text_range(node))])
	print("inside note from range \n")
	for x in candidates:
		print(x,atok.get_text_range(x))
	print("outside note from range \n",min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0])

	return min( candidates , key= lambda y :(y[1][1]-y[1][0]) )[0]


def node_from_range_new(root,atok,r,special = False,lenient = False):
    # notes like ast.Store result in (0,0) with atok.get_text_range() 
    # which causes problems if the cursor is right at the beginning of the file  
    inside = lambda x,y: (y[0]<=x[0]<y[1] and y[0]<x[1]<=y[1] and not y[0]==y[1]==0)
    if lenient:
        inside = lambda x,y: (y[0]<=x[0]<=y[1] and y[0]<=x[1]<=y[1] and not y[0]==y[1]==0)
    generic_fix(root,atok)
    # print(" the fields are now",root._fields)
    for child in ast.iter_child_nodes(root):
        # print(" just to check something out",child,atok.get_text_range(child))
        # print(" and the child fields are ",child._fields)
        if inside(r,atok.get_text_range(child)):
            # print(" success with",child,"special = ",special)
            return node_from_range_new(child,atok,r,special,lenient)
    if special:
        # print("Special:\n",ast.dump(root))
        if match_node(root,(ast.Tuple,ast.List,ast.Set,ast.Dict,ast.DictComp)):
            # print("Inside Here After Special")
            temporary = get_sub_index(root,None)

            l = [x  for x in temporary for y in [get_source_region(atok,x)] 
                if inside((r[0],r[0]),y) or inside((r[1],r[1]),y) or inside(y,r)]
            # print("temporary:\n",temporary)
            # print("L:\n",l)
            if l  and l!=temporary:
                return l


    return root


def node_from_range(root,atok, r,special = False,lenient = False):
    # return node_from_range_old(root,atok,r)
    return node_from_range_new(root,atok,r,special,lenient)








