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
	print( candidates )
	k = lambda x: (-1 * lca(x, origin,True),lca.get_depth(x))
	return sorted(candidates, key = k)
















