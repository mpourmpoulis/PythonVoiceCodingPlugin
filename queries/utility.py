import ast

def reestablish_priority(initial,adjusted):
	z = {initial[v]:v for v in initial}
	w = {adjusted[v]:v for v in adjusted}
	x = sorted(z.keys())
	y = sorted(w.keys())
	s = set(y)
	if len(y)!=len(s):
		return initial
	output=adjusted
	index = 1
	for i in x:
		if z[i] not in output:
			while index in s:
				index += 1
			output[z[i]] = index
			s.add(index)
	return output
	



class ResultAccumulator():
	"""docstring for ResultAccumulator"""
	def __init__(self,penalized=[], penalty=0):
		self.accumulator = {}
		self.penalized = set(penalized)
		self.penalty = penalty
		self.history = []

	def push(self,node,priority):
		self.history.append((node,priority))
		# print(" pushing", priority )
		# if not isinstance( node,ast.AST ) and not node is None:
			# for x in node:
				# print(ast.dump(x))
		if not node:
			return None
		if node in self.penalized:
			priority = priority + self.penalty
		if priority not in self.accumulator:
			self.accumulator[priority] = [node]
		else:
			self.accumulator[priority].append(node)

	def get_result(self):
		visited  = set()
		finalists = []
		sorted_keys = sorted(self.accumulator.keys())
		for x in sorted_keys:
			for node in self.accumulator[x]:
				# print(" baggie note")
				# print( node )
				if node  not in visited:
					visited.add(node)
					finalists.append(node)
		if len(finalists)>=1:
			return finalists[0],finalists[1:]
		else:
			return None,None


		