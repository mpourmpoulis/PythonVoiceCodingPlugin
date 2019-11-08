import ast

from PythonVoiceCodingPlugin.library import sorted_by_source_region

PARENT = 1
PARENT_FIELD = 2
PARENT_FIELD_INDEX = 3

class LevelVisitor():
	"""docstring for LevelVisitor
	
	Attributes:
	    atok (TYPE): Description
	    data (dict[int,dict[tuple,list]]): Description
	    local_data (dict[ast.AST, tuple[ast.AST,str,int]]): Description
	    parent (TYPE): Description
	    root (TYPE): Description
	    special (TYPE): Description
	    level_defining(set[ast.AST]): nodes that define the level
	    stack (TYPE): Description
	"""
	def __init__(self, root,level_defining,atok  = None,special_nodes = []):
		self.atok  = atok 
		self.root = root
		self.level_defining = set(level_defining)
		self.special = set(special_nodes)
		self.flag = self.special.issubset(self.level_defining)

		self.data = {1:{},2:{},3:{}}
		self.local_data = {}

		# stock and parent initialization before recursion
		self.stack = [(root,None,None)]
		self.parent = (root,None,None)
		self.visit(root)


	def _insert_primitive(self,h,k,v):
		if k not in h:
			h[k] = []
		h[k].append(v)

	def insert(self,k,v):
		self.local_data[v] = k
		self._insert_primitive(self.data[1],(k[0],),v)
		self._insert_primitive(self.data[2],(k[0],k[1]),v)
		self._insert_primitive(self.data[3],(k[0],k[1],k[2]),v)
		
	def visit(self,node):
		self.insert(self.parent,node)
		success = node in self.level_defining
		for child in ast.iter_child_nodes(node):
			if success:
				self.stack.append(self.parent)
				self.parent = (node,child.parent_field,getattr(child,"parent_field_index",None))
			self.visit(child)
			if success:
				self.parent =self.stack.pop()

	def __getitem__(self,key):
		return self.local_data[key]

	def __call__(self, node, level_desc, index = None, only_special = False):
		# we determine how strict our level hierarchy will be 
		guide = tuple(list(self.local_data[node])[:level_desc])

		# and we retrieve all spatial nodes in the same hierarchy as "node"
		# we may optionally return only nodes that are special
		result = [
			x for x in self.data[level_desc][guide] 
			if ((x in self.level_defining and self.flag) or x in self.special) and 
			(not only_special or not self.special or x in self.special)
		]

		# we optionally sort the list positionally +and pick the specified index
		if self.atok :
			result = sorted_by_source_region(self.atok, result)
			if index is not None:
				if len(result)>index  and len(result) >= -1*index:
					result = result[index]
				else:
					result = None
		return result



	def everything(self, level_desc, index = None, only_special = False):
		result =  self.data[level_desc].values() # type: List[List[ast.AST]]
		

		# Allow only level defining  or  special nodes
		result = [ 
			[
				y  for y in x 
				if ((y in self.level_defining and self.flag) or y in self.special) and 
				(not only_special or not self.special or y in self.special)
			]  
			for x in result
		]
		print("\nresume\n",result,"\n\n")
		# optionally pick specific element from each list
		if self.atok:
			result = [sorted_by_source_region(self.atok,x)  for x in result]
			if index is not None:
				result = [x[index]  for x in result if  len(x)>index  and len(x) >= -1*index]
		return result

	
	
		

	

			
			
		
		








