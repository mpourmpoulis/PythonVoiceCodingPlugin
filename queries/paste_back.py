from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 

@no_build_attempt
class PasteBack(InsertionQuery):
	select_insertion = True
	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		print(" inside query",state,"\n")
		history  =  extra["history"]
		candidates = result_alternatives_sequence(state,text = True,mode = state["mode"])
		candidates_location = result_alternatives_sequence(state,location = True,mode = state["mode"])
		surrounding = query_description.get("surrounding_punctuation",("",""))
		if query_description["format"]==1:
			selection = state["initial_origin"]
			if state["initial_mode"]=="multiple":
					selection = make_flat(selection)

			if state["mode"]=="single":
				output = candidates[query_description.get("color",0)]
				selection = selection if isinstance(selection,list) else [selection]				
				return [(x,surrounding[0]+output+surrounding[1])  for x in selection]

			elif state["mode"]=="multiple":
				if state["initial_mode"]=="single":
					raise Exception("can't paste multiple values the same origin!")

				elif state["initial_mode"]=="multiple":
					if len(state["initial_origin"]) != len(state["origin"]):
						raise Exception("mismatch of things to paste and locations to place")
					try : 
						print("candidates\n",candidates)
						output = [x[query_description.get("color",0)] for x in candidates]						
					except IndexError as  e: 

						raise
						raise Exception("tried to obtain an alternative color that is not common!")
					if any(isinstance(x,list) for x in output):
						raise Exception(" one of the results spanned over multiple selections, this is not supported!")
					return [(x,surrounding[0]+y+surrounding[1])  for y,x in  zip(output,selection)]

		if query_description["format"]==2:
			selection = {candidates_location[query_description["color"+i]]  
							for i in ["2","3","4"] if "color"+i in query_description}
		output = candidates[query_description.get("color",0)]
		return [(x,surrounding[0]+output+surrounding[1])  for x in selection]







