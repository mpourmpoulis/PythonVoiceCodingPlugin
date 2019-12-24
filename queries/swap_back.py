from PythonVoiceCodingPlugin.queries.abstract import InsertionQuery,no_build_attempt
from PythonVoiceCodingPlugin.queries.strategies import result_alternatives_sequence 

def overlap_regions(x,y):
	return y[0]<=x[0]<y[1] or x[0]<=y[0]<x[1]

@no_build_attempt
class SwapBack(InsertionQuery):
	select_insertion = True
	multiple_in = True

	def handle_single(self,view_information,query_description,extra = {}):
		state = extra["state"]
		# history  =  extra["history"]
		# index = len(history)
		# while history[index-1][0]=="selection"  and index>=1 and history[index-1][1]  == view_information["change_count"]:
			# index -=1
		# if index==len(history) or history[index][1] != view_information["change_count"]:
			# return []
		candidates = result_alternatives_sequence(state,location = True,text = True)
		if query_description["format"]==1:
			if extra["secondary"]:
				for location,t in candidates:
					if not overlap_regions(location,state["origin"]):
						decision = (location,t)
						break
				else:
					raise Exception("Swamp cannot swap regions of overlap!!!")
			else:
				decision = candidates[query_description["color"]]
			location_text = [(state["origin"],state["origin_text"]),decision]
		if query_description["format"]==2:
			location_text = [candidates[query_description["color"+i]]  
							for i in ["","2","3","4"] if "color"+i in query_description]
		output = []  
		for j in range(0,len(location_text)):
			x = location_text[j]
			y = location_text[j-1]
			if overlap_regions(x[0],y[0]):
				raise
			output.append((x[0],y[1]))

		return output






