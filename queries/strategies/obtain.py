def obtain_result(result, alternatives):
	if result:
		return result, alternatives if alternatives is not None else []
	else:
		if alternatives is None or len( alternatives )==0:
			return None,None
		else:
			return  alternatives[0], alternatives[1:]

# bug if result is in alternatives