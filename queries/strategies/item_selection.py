from copy import deepcopy

def translate_indices(query_description,name,decrement):
	y = [name + x  for x in ["","2","3","4"]]
	value = 1 if decrement else 0
	return [query_description[x]-value  for x in y if x in query_description]


def decode_item_selection(items,query_description,mode,name,decrement=True):
	indices = translate_indices(query_description,name,decrement)
	print("Indices:\n",indices)
	print("Items:\n",items)
	if mode == "individual":
		print([items[x]  for x in indices])
		return [items[x]  for x in indices]
	elif mode == "range":
		if len(indices) == 2:
			return items[indices[0]:indices[1] + 1]
		elif len(indices) == 1:
			return items[indices[0]:]
		else: 
			return deepcopy(items)






