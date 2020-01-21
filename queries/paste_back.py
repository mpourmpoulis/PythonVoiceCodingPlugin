from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 

def surround(surrounding,text):
	assert isinstance(surrounding,(str,tuple,list)), "Surrounding must be either a string, tuple or list not a "  + str(type(surrounding))
	if isinstance(surrounding,(tuple,list)):
		surrounding = (
			surrounding[0].replace("quotes",'"'),
			surrounding[1].replace("quotes",'"'),
		)

		return surrounding[0] + text + surrounding[1]
	if isinstance(surrounding,str):
		surrounding = surrounding.replace("quotes",'"')
		surrounding = surrounding.replace("$$",text)
		return surrounding 






@no_build_attempt
class PasteBack(InsertionQuery):
	select_insertion = True
	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		print("\ninside query ",state,"\n\n")
		history  =  extra["history"]
		candidates = result_alternatives_sequence(state,text = True)
		candidates_location = result_alternatives_sequence(state,location = True)
		surrounding = query_description.get("surrounding_punctuation",("",""))
		# surrounding = surrounding if surrounding != "quotes" else ('"','"')
		if query_description["format"]==1:
			selection = state["initial_origin"]
			if state["initial_mode"]=="multiple":
					selection = make_flat(selection)

			if state["mode"]=="single":
				output = candidates[query_description.get("color",0)]
				selection = selection if isinstance(selection,list) else [selection]				
				return [(x,surround(surrounding,output))  for x in selection]

			elif state["mode"]=="multiple":
				try : 
					output = [x[query_description.get("color",0)] for x in candidates]						
				except IndexError as  e: 
					raise Exception("tried to obtain an alternative color that is not common!")
					
				if state["initial_mode"]=="single":
					print("Output:\n",output)
					try : 
						output = make_flat(output)
					except :
						pass
					output = ",".join([surround(surrounding,x)  for x in  output])
					return [(state["initial_origin"],output)]
					# raise Exception("can't paste multiple values the same origin!")

				elif state["initial_mode"]=="multiple":
					if len(state["initial_origin"]) != len(state["origin"]):
						print("before doing anything Palenque's ",output)
						if len(output)==1  and isinstance(output[0],list):
							output = make_flat(output)
							if len(state["origin"])==1  and len(output)==len(state["initial_origin"]):
								return [(x,surround(surrounding,y))  for y,x in  zip(output,selection)]
						print("their respective lengths are",len(output),len(state["initial_origin"]),output, "\n")
						raise Exception("mismatch of things to paste and locations to place")

					if any(isinstance(x,list) for x in output):
						raise Exception("one of the results spanned over multiple selections, this is not supported!")
					return [(x,surround(surrounding,y))  for y,x in  zip(output,selection)]

		if query_description["format"]==2:
			if state["mode"]=="multiple":
				raise Exception("pasting between alternatives is possible only in single mode")
			selection = {candidates_location[query_description["color"+i]]  
							for i in ["2","3","4"] if "color"+i in query_description}
		output = candidates[query_description.get("color",0)]
		return [(x,surround(surrounding,output))  for x in selection]







