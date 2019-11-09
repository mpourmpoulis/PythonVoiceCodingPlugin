import ast 
import bisect
import token

from PythonVoiceCodingPlugin.third_party.astmonkey import transformers
from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset,previous_token,next_token

class BracketMatcher():
	"""docstring for BracketMatcher"""
	def __init__(self, atok):
		self.atok = atok
		self.matching  = {}
		self.level = {}
		self.level_index = {}	
		self._match(atok)
		

	def find_enclosing(self,origin,include_self = True):
		possible = bisect.bisect_right(self.level_index[0],origin.start)
	
		if possible!=0:
			c =  self.level[0][possible-1]
			# print( origin ,c)
			# print(origin.end,c[1].end)
			if origin.end <= c[1].end :
				if origin.end==c[1].end or origin.end==c[0].end :
					if include_self:
						return c
					else:
						return None,None
				return c
		return None,None

	def _match(self,atok):
		# print("inside much mass on all bracket ")
		target = {"[":1, "]":-1 , "(":1,")":-1,"{":1,"}":-1}
		stack = []
		candidates = [x  for x in atok.tokens  if x.string in target]
		for candidate in candidates:
			# print(candidate,stack)
			if target[candidate.string] == 1:
				stack.append(candidate)
			else:
				c = stack.pop()
				self.matching[c] = candidate
				self.matching[candidate] = c
				index = len(stack)
				if index not in self.level:
					self.level[index] = []
					self.level_index[index] = []  
				self.level[index].append((c,candidate))
				self.level_index[index].append(c.start)


			














