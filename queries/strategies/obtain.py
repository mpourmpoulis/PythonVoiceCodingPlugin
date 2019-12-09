def obtain_result(result, alternatives):
	if result:
		return result, [x  for x in  alternatives if x is not result] if alternatives is not None else []
	else:
		if alternatives is None or len( alternatives )==0:
			return None,None
		else:
			return  alternatives[0], [x  for x in alternatives[1:] if x is not alternatives[0]]

