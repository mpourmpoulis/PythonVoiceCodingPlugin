import ast

from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor
from PythonVoiceCodingPlugin.library.traverse import match_node




def tiebreak_on_lca(root,origin,candidates):
	"""ranks nodes based on the depth of their lowest_common_ancestor 
	With origin (the deeper the better). In case of ties the note
	Closer to the LCA is preferred.
	
	Args:
	    root (TYPE): Description
	    origin (TYPE): Description
	    candidates (TYPE): Description
	
	Returns:
	    TYPE: Description
	"""
	lca  = LCA(root)
	def tiebreaker(x):
		depth,node = lca(x, origin,node_and_depth = True)
		v = 3
		if match_node(node,ast.Dict):
			if node is not x and node is not origin:
				field,field_index = lca.get_field_with_respect_to(x,node)
				ofield,ofield_index = lca.get_field_with_respect_to(origin,node)
				v = abs(field_index - ofield_index)
				v = v if v<3 else 3
		return (-1 * depth,v,lca.get_depth(x),abs(x.first_token.start[0] - origin.first_token.start[0]))
	
	return sorted(candidates, key = tiebreaker)



def tiebreak_on_visual(original_line,result,alternatives):
	if result:
		if original_line:
			k = lambda x: (
				abs(x.first_token.start[0] - result.first_token.start[0]) + 
				( 
					10 if (					 
					x.first_token.start[0]<=original_line<=result.first_token.start[0] or
					x.first_token.start[0]>=original_line>=result.first_token.start[0]
					) else 0
				)
			)
		else:
			k = lambda x: abs(x.first_token.start[0] - result.first_token.start[0])
		if alternatives:
			return sorted(alternatives, key = k)
	return alternatives














