def translate_indices(query_description,name):
	y = [name + x  for x in ["","2","3","4"]]
	return [query_description[x]-1  for x in y if x in query_description]


def decode_item_selection(items,query_description,mode,name):
	indices = translate_indices(query_description,name)
	print(indices)
	if mode == "individual":
		print([items[x]  for x in indices])
		return [items[x]  for x in indices]
	elif mode == "range":
		if len(indices)!= 1:
			return items[indices[0]:indices[1] + 1]
		else:
			return items[indices[0]:]






