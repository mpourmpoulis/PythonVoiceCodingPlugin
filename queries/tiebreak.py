import ast

from PythonVoiceCodingPlugin.library.LCA import LCA
from PythonVoiceCodingPlugin.library.level_info import LevelVisitor





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
	k = lambda x: (-1 * lca(x, origin,True),lca.get_depth(x))
	return sorted(candidates, key = k)



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














