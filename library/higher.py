import ast
import token

from PythonVoiceCodingPlugin.third_party.asttokens import asttokens

from PythonVoiceCodingPlugin.library import previous_token,next_token
from PythonVoiceCodingPlugin.library.modification import ModificationHandler





def filter_asynchronous(atok,m = None, timestamp  = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if x.string=="async"]
	for c in candidates:
		y = next_token(atok,c)
		# async_stmt: 'async' (funcdef | with_stmt | for_stmt)
		if y  and y.string in ["def","for","with"]:
			m.modify_from(timestamp,(c.startpos,y.startpos),"","async_"+y.string)
	return m


def filter_await(atok,m = None, timestamp  = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if  x.string=="await"]
	for c in candidates:
		y = previous_token(atok,c)
		z = next_token(atok,c)
		if  y   and not y.string.isspace():
			m.modify_from(timestamp,(c.startpos,c.endpos),"","await")
		else:
			if z:
				m.modify_from(timestamp,(c.startpos,z.startpos),"yield from ","await")
			else:
				m.modify_from(timestamp,(c.startpos,c.endpos),"","await")
	return m

def filter_fstrings(atok,m = None, timestamp = 0):
	m = m if m else ModificationHandler(atok.text)
	candidates = [x  for x in atok.tokens  if x.string=="f"]
	for c in candidates:
		y = next_token(atok,c)
		if y and y.type==token.STRING:
			m.modify_from(timestamp,(c.startpos,y.endpos),y.string,"fstring")
	return m

def filter_everything(atok, m = None, timestamp = 0):
	m = m if m else ModificationHandler(atok.text)
	m = filter_asynchronous(atok,m, timestamp)
	m = filter_fstrings(atok,m,  timestamp)
	m = filter_await(atok,m, timestamp)
	return m









