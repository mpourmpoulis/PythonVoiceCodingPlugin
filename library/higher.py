import ast
import token

from asttokens import PythonVoiceCodingPlugin.third_party.asttokens as asttokens

from PythonVoiceCodingPlugin.library import previous_token,next_token
from PythonVoiceCodingPlugin.library.modification import ModificationHandler





def filter_asynchronous(atok,m = None, timestamp  = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if x.type== 52 and x.string=="async"]
	for c in candidates:
		y = next_token(c)
		# async_stmt: 'async' (funcdef | with_stmt | for_stmt)
		if y and y.type==52 and y.string in ["def","for","with"]:
			m.modify_from(timestamp,(c.startpos,y.startpos),"","async_"+y.string)
	return m


def filter_await(atok,m = None, timestamp  = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if x.type== 52 and x.string=="await"]
	for c in candidates:
		m.modify_from(timestamp,(c.startpos,c.endpos),"yield from","await")
	return m

def filter_fstrings(atok,m = None, timestamp = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if x.type== 52 and x.string=="f"]
	for c in candidates:
		y = next_token(c)
		if y and y.type==token.STRING:
			m.modify_from(timestamp,(c.startpos,c.endpos),"","fstring")
	return m

def filter_everything(atok, m = None, timestamp = 0):
	print(m)
	m = m if m else ModificationHandler(atok.text)
	print(" inside everything after initialization",m)
	m = filter_asynchronous(atok,m, timestamp)
	print("1",m)
	m = filter_fstrings(atok,m,  timestamp)
	print("2",m)
	m = filter_await(atok,m, timestamp)
	print(m)
	return m









