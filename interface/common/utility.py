import sublime
from itertools import chain

def make_region(r):
	if isinstance(r,tuple):
		return sublime.Region(r[0],r[1])
	elif isinstance(r,list):
		return [make_region(x)  for x in r if x]
	else:
		raise Exception("the maker region function was given an incorrect argument"+str(r))

def all_or_nothing(r,check,*arguments):
	return all(check(x,*arguments) for x in r) or not any(check(x,*arguments) for x in r)


def make_sequence(r):
	if not isinstance(r ,list):
		return [r]
	elif isinstance(r,list):
		try : 
			return list(chain.from_iterable(r))
		except :
			print("Gold Inside Here")
			return r
	
