from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 


@no_build_attempt
class DeleteAlternatives(InsertionQuery):
	select_insertion = True
	multiple_in = True
	def handle_single(self,view_information,query_description,extra = {}):
		candidates = result_alternatives_sequence(extra["state"],location= True)
		if query_description["format"] == 1:
			selection = {candidates[query_description["color"+i]]  
							for i in ["","2","3","4"] if "color"+i in query_description}
		return [(x,"")  for x in selection]

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)

	# def handle_single(self,view_information,query_description,extra = {}):
		# state = extra["state"]
		# candidates = result_alternatives_sequence(state,location = True,mode = state["mode"])
		# if query_description["format"]==1:
			# if state["mode"]=="single":
				# selection = candidates[query_description.get("color",0)]
				# selection = selection if isinstance(selection,list) else [selection]				
				# return [(x,"")  for x in selection]
			# elif state["mode"]=="multiple":
				# try :
					# selection = [x[query_description.get("color",0)] for x in candidates]						
				# except IndexError as  e:						
						# raise Exception("tried to obtain an alternative color that is not common!")
				# if any(isinstance(x,list) for x in selection):
					# print("inside here the selection has become ",selection)
					# selection = make_flat([x if isinstance(x,list) else [x]   for x in selection])
					# print("inside here the selection has become after wardsit's",selection)
		# print("selection is ",selection,"\n")
		# return [(x,"")  for x in selection]






