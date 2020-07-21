def reestablish_priority(initial,adjusted):
	output={}
	to_be_removed = {k for k,v in adjusted.items() if v<0}
	initial_order = sorted(initial.items(),key=lambda x:x[1])
	adjusted_order = sorted(adjusted.items(),key=lambda x:x[1])
	already_assigned_values = set(adjusted.values())
	for k,v in adjusted_order:
		output[k] =  v
	for k,v in initial_order:
		if k not in output:
			while v in already_assigned_values:
				v = v + 1
			output[k] = v
			already_assigned_values.add(v)

	if len(set(adjusted.keys())-to_be_removed)!=len(set(adjusted.values()))-(1 if to_be_removed else 0):
		raise Exception("you cannot assign the same priority for two strategies",adjusted)

	return output
	



class ResultAccumulator():
	"""docstring for ResultAccumulator"""
	def __init__(self,penalized=[], penalty=0):
		self.accumulator = {}
		self.penalized = set(penalized)
		self.penalty = penalty
		self.history = []

	def push(self,node,priority,penalty = 0):
		self.history.append((node,priority))
		if not node:
			return None
		if node in self.penalized:
			priority = self.penalize(priority,self.penalty)
		priority = self.penalize(priority,penalty)
		if priority < 0:
			return 
		elif priority not in self.accumulator:
			self.accumulator[priority] = [node]
		else:
			self.accumulator[priority].append(node)

	def penalize(self,priority,penalty):
		if priority<0:
			return priority
		else:
			return priority+penalty

	def get_result(self):
		visited  = set()
		finalists = []
		sorted_keys = sorted(self.accumulator.keys())
		for x in sorted_keys:
			for node in self.accumulator[x]:
				if node  not in visited:
					visited.add(node)
					finalists.append(node)
		if len(finalists)>=1:
			return finalists[0],finalists[1:]
		else:
			return None,None


		