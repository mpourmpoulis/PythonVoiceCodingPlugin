def result_alternatives_sequence(state,location=False,text = False,mode="single",level = False):
	result_text = state["result_text"]
	alternatives_text = state["alternatives_text"]
	if mode=="single":
		result_text = [result_text]
		candidates_text = result_text + alternatives_text if alternatives_text else result_text
	elif mode=="multiple":
		if not alternatives_text: alternatives_text = [[] for x in result_text]
		assert len(alternatives_text)==len(result_text), "lengths are presold and alternatives must match"
		candidates_text = [x+y for x,y in zip(result_text,alternatives_text)]
	result = state["result"]
	alternatives = state["alternatives"]
	if mode=="single":
		result = [result]
		candidates_location = result + alternatives if alternatives else result
	elif mode=="multiple":
		if not alternatives: alternatives = [[] for x in result]
		assert len(alternatives)==len(result), "lengths are presold and alternatives must match"
		candidates_location = [x+y for x,y in zip(result,alternatives)]
	if location and text:
		return list(zip(candidates_location,candidates_text))
	if location:
		return candidates_location
	if text:
		return candidates_text

	
