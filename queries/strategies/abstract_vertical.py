import ast
from bisect import bisect_right,bisect_left

from PythonVoiceCodingPlugin.library.traverse import search_upwards,search_upwards_log, find_matching,match_node, find_all_nodes
from PythonVoiceCodingPlugin.queries.strategies.obtain import obtain_result

def decode_abstract_vertical(root,atok, target,current_line, index,direction,
	 want_node = False, selector = None, want_alternatives = False):
	nodes = find_matching(root, selector)  if  selector else  find_all_nodes(root,target)
	line_information = set()
	for n in nodes:	
		line_information.add(n.first_token.start[0])
	line_information = sorted(list(line_information))
	ll=len(line_information)
	if direction=="below":	
		i = bisect_right(line_information,current_line)
		i = min(ll-1,i+index-1)
	elif direction=="above":
		i = bisect_left(line_information,current_line)
		i  = max(0,i-index)
	else:
		return None
	if want_node:
		if want_alternatives:
			candidates = [x  for x in nodes if x.first_token.start[0] == line_information[i]]
			return obtain_result(None,candidates) 
		for n in nodes:
			if n.first_token.start[0] == line_information[i]:
				return n
		else:
			return None
	else:
		return line_information[i]



def decode_vertical_groups(atok,current_line,index,direction):
	groups = []
	written = []
	data = [not x.isspace()  for x in atok.text.splitlines()]
	if not data:
		return None , None
	l = data[0]
	for i,d in enumerate(data):
		if d != l:
			groups.append(i)
			written.append(d)
	location = bisect_right(groups,current_line) - 1
	offset = -1 if direction in ["above","up"] else 1
	if written[location]:
		potential_location = location + 2*index*offset
	else:
		potential_location = location + 2*index*offset - offset
		x = groups 

	advance = lambda x: x - 1 if direction in ["above","up"] else x+1
	pointer=current_line
	while data[pointer]  and 0<pointer<len(data)-1:
		pointer = advance(pointer)
	for i in range(0,index):
		while not data[pointer]  and 0<pointer<len(data)-1:
			pointer = advance(pointer)
			second_pointer = pointer if data[pointer] else None
		while data[pointer]  and 0<pointer<len(data)-1:
			pointer = advance(pointer)
	pointer =  pointer+1 if direction in ["above","up"] else pointer-1
	return min(pointer,second_pointer),max(pointer,second_pointer)

