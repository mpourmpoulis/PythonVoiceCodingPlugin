""" 
this module is responsible for partially parsing user code.
In particular, while  editing   code, it is often the case
there are syntactical errors, such as missing variables
(x = [value to be completed now]) or features introduced in later versions of Python.
such errors will cause the ast parser to abort with the syntax error preventing us from 
analyze 
additionally, these module enables us to parse ( and correct ) is single
logical line.

"""
import ast 
import tokenize

from PythonVoiceCodingPlugin.third_party.asttokens import asttokens  

from PythonVoiceCodingPlugin.library import build_tree,get_source_region,nearest_node_from_offset
from PythonVoiceCodingPlugin.library.lexical import expand_to_line_or_statement
from PythonVoiceCodingPlugin.library.higher import filter_everything
from PythonVoiceCodingPlugin.library.modification import ModificationHandler
from PythonVoiceCodingPlugin.library.repair import RepairMissing


'''
these module is responsible for partially parsing the user code
For instance, it enables to ignore various syntactic errors and to compile
either fulltext or only single logical lines
'''

################################################################################################
################################################################################################

def partially_parse(code, m = None, atok = None):
	m = m if m is not None else ModificationHandler(code)
	#print(code)
	timestamp = m.get_timestamp()
	try:
		root,atok = build_tree(code) 
		r = RepairMissing(atok,m,timestamp)
		return root,atok,m,r
	except: 
		atok =  atok  if atok  else asttokens.ASTTokens(parse=False, source_text= code)
		print(m)
		m = filter_everything(atok,m, timestamp)
		m.update()
		#print("after filtering",m.history)
		atok = asttokens.ASTTokens(parse=False, source_text= m.current_code)
		r = RepairMissing(atok,m,m.get_timestamp())
		r.work()
		m.update()
		#print("she's after repair",m.history)
		try:
			root,atok = build_tree(m.current_code) 
			return root,atok,m,r
		except Exception as e:
			print(" go to the field\n",m.current_code)
			print(" error was\n",e)
			return None,None,None,None

###############################


def line_partial(code,offset):	
	print("inside bar shall align")
	atok = asttokens.ASTTokens(parse=False, source_text=code)
	print([x  for x in atok.tokens  if x.type== tokenize.NL])
	origin = atok.get_token_from_offset(offset)
	left, right = expand_to_line_or_statement(atok,origin)
	print( left, right )
	m = ModificationHandler(code)
	m.modify_from(0,(0, left.startpos),"")
	if right.string == ":":
			m.modify_from(0,(right.endpos,len(code)+1),"pass")
	else:
			m.modify_from(0,(right.endpos,len(code)+1),"")
	m.update()
	print("history  is",m.history)
	return partially_parse(m.current_code,m)

################################################################################################
################################################################################################










################################################################################################
################################################################################################
#
#
# the following functions are deprecated and will be removed in the near future
#
#
################################################################################################
################################################################################################
def parse_single_correct_line(line):
	try:
		return build_tree(line)
	except Exception as e:
		return None

def build_without_higher(code,mode = True):
	atok =  asttokens.ASTTokens(parse=False, source_text=code)
	m = ModificationHandler(code)
	m = filter_everything(m,atok)
	m.update()
	root,atok = build_tree(m.current_code) 
	return root,atok,m


def parse_line_from_offset(code, offset):
	print("\n\n hello world  here\n\n")
	atok =  asttokens.ASTTokens(parse=False, source_text= code )
	origin = atok.get_token_from_offset(offset)
	print("off their origin ")
	left, right = expand_to_line_or_statement(atok,origin)
	print("often expands the underlying ", left, right)
	area = code[left.startpos:right.endpos]

	#print("area is ",area)
	print(asttokens.ASTTokens(parse=False, source_text=area).tokens)
	return build_tree(area)


	






