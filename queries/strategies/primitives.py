def _get(l,n,d):
	return l[n] if len(l)>n and len(l) >= -1*n else d


def root_level_order(accumulator,root,level,index,only_information,priority,penalty):
	first_option   = level(root,1, index,False)
	second_option  = level(root,1, index,True)
	print(first_option,second_option,"from root level order ")
	if first_option in level.special and only_information==False: 	
		accumulator.push(first_option,priority)
	else:
		first_option = None
	if not only_information or True:
		accumulator.push(second_option,priority if not first_option else priority + penalty)
	
def root_lexical_order(accumulator,root,level_nodes,information_nodes,index,
		only_information,priority,penalty,lca = None,constrained_space = None):
	# print(" I entered a roach lexical order")
	if  lca:
		level_nodes = [x  for x in level_nodes if lca.is_child(x,root)]
		information_nodes = [x  for x in information_nodes if lca.is_child(x,root)]
	# print("inside Drew's lexical order",level_nodes,information_nodes)
	if constrained_space:
		level_nodes = [x  for x in level_nodes if constrained_space[0]<x.first_token.startpos<constrained_space[1]]
		information_nodes = [x  for x in information_nodes 
			if constrained_space[0]<x.first_token.startpos<constrained_space[1]]
	first_option = _get(level_nodes,index,None)
	second_option  = _get(information_nodes,index,None)
	if first_option in information_nodes and not information_nodes:	
		accumulator.push(first_option,priority)
	else:
		first_option = None
	if not only_information or True:
		accumulator.push(second_option,priority if not first_option else priority + penalty)


def child_level_older(accumulator,child_list,level,index,only_information,priority):
	for i, child in enumerate(child_list) :
		counter = 0
		for x,y in [(3,False),(3,True),(1, False),(1,True)]:
			candidate = level(child,x, index, y)
			# print("rejected_candidate", candidate, "from child", child)
			if candidate in level.special  and (only_information == False or y==True):
				# from 
				accumulator.push(candidate,priority + i + counter)
				counter += 1



def root_everything(accumulator,level,information_nodes, index, priority, only_information):
	for x in level.everything(2,index,only_information):
		if x in information_nodes:
			accumulator.push(x,priority)

