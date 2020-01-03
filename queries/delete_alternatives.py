from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 


@no_build_attempt
class DeleteAlternatives(InsertionQuery):
	select_insertion = True
	multiple_in = True
	# def handle_single(self,view_information,query_description,extra = {}):
		# candidates = result_alternatives_sequence(extra["state"],location= True)
		# if query_description["format"] == 1:
			# selection = {candidates[query_description["color"+i]]  
							# for i in ["","2","3","4"] if "color"+i in query_description}
		# return [(x,"")  for x in selection]
# 

	def filter_overlapping(self,selection):

		if selection:
			selection = sorted(selection)
			result = [selection[0]]
			print(type(result))
			for s in selection:
				print(type(s))
				if s[1]<result[-1][1]:
					continue
				else:
					if s[0]<result[-1][1]:
						result[-1] = (result[-1][0],s[1])
					else:
						result.append(s)
		return result

	def handle_multiple(self,view_information,query_description,extra = {}):
		return self.handle_single(view_information,query_description,extra)

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		candidates = result_alternatives_sequence(state,location = True)
		if query_description["format"]==1:
			if state["mode"]=="single":
				selection = [candidates[query_description["color"+i]]  
							for i in ["","2","3","4"] if "color"+i in query_description]
				selection = selection if isinstance(selection,list) else [selection]	
			elif state["mode"]=="multiple":
				try :
					print("candidates",	candidates,"\n")
					selection = [x[query_description["color"+i]] for x in candidates for i in ["","2","3","4"] if "color"+i in query_description]						
				except IndexError as  e:						
						raise Exception("tried to obtain an alternative color that is not common!")
				if any(isinstance(x,list) for x in selection):
					print("inside here the selection has become ",selection)
					selection = make_flat([x if isinstance(x,list) else [x]   for x in selection])
					print("inside here the selection has become after wardsit's",selection)
		selection = self.filter_overlapping(selection)
		print("selection is ",selection,"\n")
		return [(x,"")  for x in selection]






