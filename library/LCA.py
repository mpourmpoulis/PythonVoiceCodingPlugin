import ast 
import bisect
 
from PythonVoiceCodingPlugin.third_party.segment_tree import SegmentTree
from PythonVoiceCodingPlugin.third_party.segment_tree.operations import min_operation

class LCA():
	"""docstring for LCA"""
	def __init__(self, root):
		self.sequence = []
		self.field_history = {}
		self.visits = {}
		self.cycle = 0
		self.depth = 0
		self.visit(root)
		self.tree = SegmentTree(self.sequence,[min_operation])


	def visit(self, node):
		self.depth+=1 
		if node not in self.visits:
			self.visits[node] = (self.cycle,self.cycle) # can probably omitted the ifprint()
			self.field_history[node] = []
		self.sequence.append((self.depth, node))
		self.cycle+=1
		for child in ast.iter_child_nodes(node):
			if not hasattr(child,"parent"):
				continue
			self.field_history[node].append((self.cycle,child.parent_field,getattr(child,"parent_field_index",None)))
			self.visit(child)
			first, last = self.visits[node]
			self.visits[node] = (first,self.cycle)
			self.sequence.append((self.depth, node))
			self.cycle+=1			
		self.depth-=1

	def get_depth(self, node):
		return self.sequence[self.visits[node][0]][0]

	def __call__(self,first_node,second_node,only_depth = False,node_and_depth = True):
		try : 
			x,y = self.visits[first_node]
			w,v = self.visits[second_node]
		except :
			print(ast.dump(first_node),"\n")
			print(second_node,ast.dump(second_node),"\n")
			raise

		
		
		l = min(x,w)
		r = max(y,v)

		ancestor = self.tree.query(l,r,"min")
		if node_and_depth:
			return ancestor
		elif only_depth:
			return  ancestor[0]
		else:
			return ancestor[1]

	def get_field_with_respect_to(self,node,parent_node):
		index = bisect.bisect_left(self.field_history[parent_node],(self.visits[node][0],))
		index = index if index < len(self.field_history[parent_node])  and \
				self.field_history[parent_node][index][0] == self.visits[node][0] else index-1 
		y = self.field_history[parent_node][index]
		return (y[1],y[2])

	def visit_time(self, node):
		return self.visits[node]

	def is_child(self,child, parent):
		x = self.visits[child]
		y = self.visits[parent]
		return x[0] > y[0]

		






