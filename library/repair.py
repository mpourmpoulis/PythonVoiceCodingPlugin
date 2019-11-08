import token
import tokenize

from asttokens import asttokens  

from noob.library import previous_token,next_token
from noob.library.modification import ModificationHandler



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
}

STARTING_UNARY = {
	'+', '-', '~', '@', 'not', ('not','in') , "*", "**", ("else",":")
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

def process_token(atok,t ):
	n = neighbors(atok, t)
	s = t.string
	p = t.type
	if s in ["*","**"]:
		before = before_star(n)
		before_space = False
		after = after_star(n)
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
			print("inserting before",[token])
			self.m.modify_from(self.start_time,(token.startpos,token.startpos),value) 

	def insert_after(self, token, space):
		index = token.index
		value = self.d if not space else " " + self.d
		if not index+1 in self.before  and not index in self.after:
			self.after.add(index)
			print("inserting off their",[token])
			self.m.modify_from(self.start_time,(token.endpos,token.endpos),value)

	def work(self):
		for t in self.atok.tokens:
			x,y = process_token(self.atok,t)
			if x[0]:
				self.insert_before(t,x[1])
			if y[0]:
				self.insert_after(t,y[1])

	










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














print(("not","in") in STARTING_UNARY)







