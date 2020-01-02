def result_alternatives_sequence(state,location=False,text = False):
	result_text = state["result_text"]
	alternatives_text = state["alternatives_text"]
	candidates_text = [result_text]+alternatives_text if alternatives_text else [result_text]
	result_location = state["result"]
	alternatives_location = state["alternatives"]
	candidates_location =   [result_location] + alternatives_location if alternatives_location else [result_location]
	if location and text:
		return list(zip(candidates_location,candidates_text))
	if location:
		return candidates_location
	if text:
		return candidates_text

	
