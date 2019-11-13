import token
import tokenize

from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

from PythonVoiceCodingPlugin.library import previous_token,next_token
from PythonVoiceCodingPlugin.library.BracketMatcher import BracketMatcher
from PythonVoiceCodingPlugin.library.modification import ModificationHandler
from PythonVoiceCodingPlugin.library.lexical import LineInfo,expand_to_line_or_statement


def get_dummy(atok):
	dummy_name = "the_dummy_name_is_really_dummy"
	forbidden = {x.string for x in atok.tokens  if x.type == token.NAME}
	while dummy_name in forbidden:
		dummy_name = dummy_name + "even_more"
	return dummy_name

def neighbors(atok,t):
	x = next_token(atok,t)
	y =  next_token(atok,x) if x else None
	z = previous_token(atok,t)
	w =  previous_token(atok,z) if z else None
	return [t,x,y,w,z]



#######################################################################################
#######################################################################################

''' keywords taken from 3.7.4 '''
KEYWORDS = {
	'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 
	'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from',
	'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or',
	'pass', 'raise', 'return', 'try', 'while', 'with', 'yield'
}


OPERATORS = {
    ':', ',', ';', '+', '-', '*', '/', '|', '&', '<', '>', '=', '%', '~', '^',  '@',
      '==','!=','<=','>=','<<','>>','**','+=','-=','*=','/=','%=','&=','|=', 
    '^=', '<<=', '>>=', '**=', '//', '//=',
}


###############################
UNARY = {
	"assert","del","elif","for","global","if","import","nonlocal","raise",
	"while","with","yield","else",
	'+', '-', '~', '@', 'not', ('not','in') , 
	"is",
}


STARTING_UNARY = {
	'+', '-', '~', '@', 'not', ('not','in') , "*", "**", ("else",":"),"is",("yield","from"),
}

BOTH_SIDES  = {
	'/', '|', '&', '<', '>', '=', '%', '^',  
     '==','!=','<=','>=','<<','>>','+=','-=','*=','/=','%=','&=','|=', 
    '^=', '<<=', '>>=', '**=', '//', '//=',
    'and', 'as','or', 'in',
}	

#######################################################################################
#######################################################################################
def start_atom(t):
	return (
		(
			t.type in [token.NAME, token.NUMBER, token.STRING] and 
			(t.string not in KEYWORDS  or t.string in ["True","False","None","lambda"])
		)  or 
		t.string in ["(","[","{","..."]
	)

def finish_atom(t):
	return (
		(
			t.type in [token.NAME, token.NUMBER, token.STRING] and 
			(t.string not in KEYWORDS  or t.string in ["True","False","None"])
		)  or 
		t.string in [")","]","}","..."]
	)


def before_star(t):
	# of these does not check all cases
	return t[-1] is None  or  not (
		finish_atom(t[-1]) or t[-1].string in ["(","[","{",",","import","for"] or t[-1].type in [token.INDENT]
	)


def after_star(t):
	# of these does not check all cases
	return 	t[1] is None  or not (
		start_atom(t[1])   or	t[-1] is not None and (
				(t[-1].string,t[1].string) in [('(',','),(',',","),(",",")")]  or 
				t[-1].string in ["import"]

		)
	)


'''

def after_star(t):
	# of these does not check all cases
	return not (
		t[-1] is None 
		finish_atom(t[-1]) or t[-1].string in ["(","[","{","import"] or t[-1].type in [token.INDENT]
		or (
			t[1] is not None and 
			(t[-1].string,t[1].string) in [('(',','),(',',","),(",",")")]
		)
	)'''
def after_both_sides(t):
	return t[1] is None or not(
		start_atom(t[1]) or 
		t[1].string in STARTING_UNARY or 
		(t[1].string,t[2].string) in STARTING_UNARY
	)

def before_both_sides(t):
	return t[-1] is None  or not(
		finish_atom(t[-1]) or
		(t[-2] is not None and finish_atom(t[-2]) and (t[-1].string,t[0].string) in STARTING_UNARY) 
	)


def before_unary(t):
	return False

def after_unary(t):
	return t[1] is None  or not(
		start_atom(t[1]) or 
		t[1].string in STARTING_UNARY or 
		(t[0].string,t[1].string) in STARTING_UNARY
	)

def after_comma(t):
	return t[1] is None  or t[1].string ==","
def before_comma(t):
	return t[ -1] is None  or t[-1].string in ["(","[","{"]
	
def after_bracket(t):
	return t[1] is None  or t[1].string in ["for","if","while","with"]


def before_dot(t):
	# return t[ - 1] is None  or not t[-1].string in ["from",".","import"]
	return False

def after_dot(t):
	# return t[1] is None  or not (
		# t[1].string in ["."] and 
		# t[-1] is not None and
		# t[-1].string in ["from",".","import"]
	# )
	return False

def handle_empty_compound(atok ,t,l,b,dummy):
	n = neighbors(atok, t)
	left,right = expand_to_line_or_statement(atok,t, l, b)
	if token.DEDENT==left.type:
		left = next_token(atok,left)
	# print("empty compound ",left,right)
	if t.string=="elif":
		left = next_token(atok,left)
	if left is t  and right.string == ":" :
		rh = next_token(atok,right)
		# print("rh is",[rh])
		while rh and (rh.line.isspace() or rh.line == right.line):
			# print("rh is",[rh])
			rh = next_token(atok, rh)
		temporary = left.line
		ls = temporary[:len(temporary) - len(temporary.lstrip())]
		temporary = rh.line if rh else ""
		rs = temporary[:len(temporary) - len(temporary.lstrip())]
		# (print("\nstarting new variation\n",[t],"\n",ls,rs,"these are the indentations",len(ls),len(rs),[left,rh]))
		if len(ls)>=len(rs):
			return True , right.endpos," pass ", False
		else:
			return (False,)
	elif t.string=="if" and right is t:
		return True , right.endpos, " " + dummy + " else " + dummy,True
	else:

		return (False,)


# empty []
def process_token(atok,t,l,b ):
	n = neighbors(atok, t)
	s = t.string
	p = t.type
	if s in ["*","**"]:
		before = before_star(n)
		before_space = False
		after = after_star(n)
		after_space = False
	elif s in [","]:
		before = before_comma(n)
		before_space = False
		after = after_comma(n)
		after_space = False
	elif s in ["(","[","{"]:
		before = False
		before_space = False
		after = after_bracket(n)
		after_space = False
	elif s in ["."]:
		before = before_dot(n)
		before_space = False
		after = after_dot(n)
		after_space = False
	elif s in BOTH_SIDES:
		before = before_both_sides(n)
		before_space = True
		after = after_both_sides(n)
		after_space = True
	elif s in UNARY:
		before = before_unary(n)
		before_space = True
		after = after_unary(n)
		after_space = True
	else:
		before = False
		before_space = False
		after = False
		after_space = False
	return ((before,before_space),(after,after_space))




#######################################################################################
#######################################################################################
#######################################################################################

class RepairMissing():
	def __init__(self, atok,  m  = None, timestamp = None):
		self.m = m if m else ModificationHandler(atok.text)
		self.start_time = timestamp if timestamp else m.get_timestamp()
		self.after = set()
		self.before = set()
		self.d = get_dummy(atok)
		self.atok = atok  

	def insert_before(self, token, space):
		index = token.index
		value = self.d if not space else self.d + " "
		if not index in self.before  and not index-1 in self.after:
			self.before.add(index)
			# print("inserting before",[token])
			self.m.modify_from(self.start_time,(token.startpos,token.startpos),value) 

	def insert_after(self, token, space):
		index = token.index
		value = self.d if not space else " " + self.d
		if not index+1 in self.before  and not index in self.after:
			self.after.add(index)
			# print("inserting off their",[token])
			self.m.modify_from(self.start_time,(token.endpos,token.endpos),value)

	def work(self):
		l = LineInfo(self.atok)
		b = BracketMatcher(self.atok)
		k = 0
		for t in self.atok.tokens:
			if t.string in ["if","for","while","with","def","elif","else"]:
				if t.string == "elif":
					k = k + 1
				z = handle_empty_compound(self.atok,t,l,b ,self.d)
				if z[0]:
					self.m.modify_from(self.start_time,(z[1],z[1]),z[2])
					if z[3]:
						continue
			x,y = process_token(self.atok,t,l,b)
			if x[0]:
				self.insert_before(t,x[1])
			if y[0]:
				self.insert_after(t,y[1])
		print("\nk",k)

	










def repair_operator(atok,m,d= None,timestamp = 0):
	correct_right = [token.NAME, token.NUMBER, token.STRING]
	# operators=["=","==","!=","<","<=",">",">=","+","-","*","**","/","//","%","@","+=","-=","*=","**=",]
	operators = set(tokenize.EXACT_TOKEN_TYPES.keys()) - {"(",")","[","]","{","}",".",",",":",";"}
	d = d  if d is not None else get_dummy(atok)
	for x in atok.tokens :
		if x.type == token.OP  and x.string in operators:
			y = next_token(atok,x)
			if  y and not (y.type in correct_right or y.string in ["(","[","{","*","**"]):
				m.modify_from(timestamp,(x.endpos,x.endpos),d)		
	return m














# print(("not","in") in STARTING_UNARY)







