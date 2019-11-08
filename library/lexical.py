import ast 
import token

from astmonkey import transformers
from asttokens import PythonVoiceCodingPlugin.third_party.asttokens as asttokens  

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset,previous_token,next_token
from PythonVoiceCodingPlugin.library.BracketMatcher import BracketMatcher

'''
attention: when this module was written I was unaware of the fact that the tokenize module contains the NL
token even in version 3.3. By contrast, the token module only introduced it in version 3.7
this could most likely significantly redo use the amount and for complexity of this module




'''





def extract_all_function_names(code):
	atok = asttokens.ASTTokens(parse=False, source_text=code) 
	return [(atok.next_token(x).string,x.type)  for x in atok.tokens if x.type == 1 and x.string =="def"]


def extract_all_class_names(code):
	atok = asttokens.ASTTokens(parse=False, source_text=code) 
	return [(atok.next_token(x).string,x.type)  for x in atok.tokens if x.type == 1 and x.string =="class"]


def line_continues(line):
	x = line.rfind("\\")
	if x==-1:
		return False
	return line[x+1:].isspace()  or line[x+1:] == ""

def leftmost(x,t):
	return x if x.start<t.start else t
def rightmost(x,t):
	return t if x.start<t.start else x

class LineInfo():
	"""docstring for LineInfo"""
	def __init__(self, atok ):	
		self.atok = atok
		self.first = {}
		self.last = {}
		self.breakpoint = {}
		# print(atok.text.splitlines(),1,atok.text )
		self.continuation = list(map(line_continues,atok.text.splitlines()))
		for t in atok.tokens :
			if t.type not in [token.NEWLINE, token.INDENT]:
				l = t.start[0]
				if l not in self.first:
					self.first[l] = t
				self.last[l] = t
				m = t.end[0]
				if m!=l:
					if m not in self.first:
						self.first[m] = t
					self.last[m] = t
					self.continuation[l-1] = True #here 
				if t.string==";":
					if t.start[0] not in self.breakpoint:
						self.breakpoint[t.start[0]] = []
					self.breakpoint[t.start[0]].append(t)





	def find_breakpoint(self,t,go_left):
		if t.start[0] not in self.breakpoint:
			return None
		else:
			right_direction = lambda x: x.start<=t.start if go_left else x.start>=t.start
			choice = max if go_left else min
			candidates = [(x.startpos,x)  for x in self.breakpoint[t.start[0]] if right_direction(x)]
			return choice(candidates)[1] if candidates else None

	def get_first(self,t):
		# print("get_first in",t,t.start)
		bp = self.find_breakpoint(t,True)
		# print("breakpoint {} ",bp)
		if bp:
			return next_token(self.atok,bp),False
		x = t.start[0]
		#print("why not x-ray",x)
		# print(self.first)
		y = self.first[x]
		

		return self.first[x],self.continuation[x-2]  or y.start[0] <x
	def get_first_down(self,t):
		x = max(t.start[0]+1,t.end[0])
		return self.first[x]
	def get_last(self,t):
		bp = self.find_breakpoint(t,False)
		if bp:
			return previous_token(self.atok,bp),False
		x = t.end[0]
		return self.last[x], self.continuation[x-1]
	def get_last_up(self,t):
		x = min(t.start[0],t.end[0]-1)
		print(x)
		print(self.last[x]) 
		return self.last[x]
			

def expand_to_line_or_statement(atok, origin,l = None,b=None):
	# print( list(filter(lambda x:x.type == 5,atok.tokens )))
	# print(" explant line")
	l = LineInfo(atok) if not l else l
	# print(" off their lining")
	b = BracketMatcher(atok) if not b else b
	origin = previous_token(atok,origin) if origin.string == ";" else origin
	# print("out of her+e rocket matching ")
	left, right = b.find_enclosing(origin)
	# print("found stuff",left,right) 
	left = left if left else origin
	right = right if right else origin 
	# move_left =True
	# move_right = True
	left,move_left=l.get_first(left)
	right,move_right=l.get_last(right)
	####
	move_left=True
	move_right = True
	i=0
	while move_left:
		# print("entering left loop we ", left )
		# left = l.get_last_up(left)
		# left,move_left  = l.get_first(left)print()
		# new_left,_ = b.find_enclosing(left)
		# print("matched Tolkien ",left,new_left)
		# left = new_left if new_left else left
		# left,move_left  = l.get_first(left)
		# print(left,new_left,move_left)
		# print("entering left loop we ", left )
		new_left = left
		while new_left:
			left,move_left  = l.get_first(new_left)
			# print( left,move_left,new_left)
			new_left,_ = b.find_enclosing(left,False)
			i=i+1
			if i>5:return None
		left = l.get_last_up(left) if move_left else left
	# print("entering right loop we ",right)
	while move_right:
		new_right = right
		while new_right:
			right,move_right  = l.get_last(new_right)
			# print( right,move_right,[new_right],right.type)
			_,new_right = b.find_enclosing(right,False) 
			# there was a bug where we would get in a fit loopif the last token was a closing bracket or parentheses
			i=i+1
			if i>5:return None,None
		right = l.get_first_down(right) if move_right else right

	# while move_right:
		# right = l.get_first_down(right)
		# _,new_right = b.find_enclosing(right)
		# right = new_right if new_right else right
		# right,move_right  = l.get_last(right)
		# print(move_right)
	# print("none")
	return left, right


	







