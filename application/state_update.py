from copy import deepcopy

from PythonVoiceCodingPlugin.library import make_flat
from PythonVoiceCodingPlugin.queries import *
from PythonVoiceCodingPlugin.application.build_cache import BuildCache
from PythonVoiceCodingPlugin.interface.common.actions import *


#######################################################################
def check_single(*args):
	return all(not isinstance(x,list) for x in args)

def check_item_single(*args):
	return all(isinstance(x,list) and all(not isinstance(y,list) or len(y)<=1 for y in x) for x in args)

def match_length(x,y):
	if x is None:
		return y is None or y==[]
	if y is None:
		return False
	assert isinstance(x,list) and isinstance(y,list),"expecting lists but got something else"
	return [len(z)  for z in x]==[len(z) for z in y]

def function():
	pass

#######################################################################


def get_regions_while_you_still_can(view_information,name):
	i = 1
	result=[]
	while True:
		x = view_information["get_regions"](name + str(i))
		if x:
			result.append(x)
		else:
			break
		i+=1
	return result

def invert_guided(data,guide):	
	print("inside guide\n",data,guide)
	output = []
	for x in guide:
		output.append([])
		for i in range(0,len(x)):
			output[-1].append(data[i].pop(0))
	if any(len(y)!=0 for y in data):
		raise Exception("sublime day.does not months the number of alternatives")
	return output


def get_location_text(location,code):
	if location is None:
		return None
	if isinstance(location,list):
		return [get_location_text(x,code)  for x in location]
	return code[location[0]:location[1]]

def convert_single_to_multiple(state):
	for k in ["result","origin","alternatives"]:
		data = state[k]
		if data is None:
			data = []
		elif not isinstance(data,list):
			data = [[data]]
		else:
			if any(isinstance(x,list) for x in data):
				raise Exception("In single_mode "+k+" cannot be a nested list!")
			else:
				data = [data]
		state[k] = data

def convert_multiple_to_single(state):
	for k in ["result","origin","alternatives"]:
		data = state[k]
		if k not in ["alternatives"]:
			if data == []:
				data = None
			elif isinstance(data,list) and len(data)==1 and isinstance(data[0],list) and len(data[0])==1:
				data = data[0][0]
			else:
				raise Exception("when converting from multiple mode In single_mode "+k+" cannot be a nested list!")
		else:
			if isinstance(data,list) and all(isinstance(x,list)  and len(x)==1 for x in data):
				data = make_flat(data)
			else:
				raise Exception(" when converting into single mode, each of the items in the alternatives must have length of one")
		state[k] = data


def clear_state(state):
	state["result"] = None
	state["origin"] = None
	state["alternatives"] = []
	state["change_count"] = -1

def retrieve_primitive(state,sublime_data):
	output = deepcopy(state)
	output["alternatives"] = invert_guided(sublime_data["alternatives"],state["alternatives"])
	for k in ["result","origin"]:
		if not match_length(state[k],sublime_data[k]):
			raise Exception("state "+k+" does not match the sublime data")
		else:
			output[k] = sublime_data[k]
	return output


def retrieve_state(state,view_information,code):
	if state["change_count"]>=view_information["change_count"]:
		return 
	if state["change_count"]==-1:
		state["change_count"]=view_information["change_count"]
		return 
	# retrieve data from their region tracker

	try :
		convert_single_to_multiple(state)
		sublime_data = {x:get_regions_while_you_still_can(view_information,x) for x in ["result","origin","alternatives"]}
		state = retrieve_primitive(state,sublime_data)
		convert_multiple_to_single(state)
	except:
		clear_state(state)
		raise
	

	for k in ["result","origin","alternatives"]:
		state[k+"_text"] = get_location_text(state[k],code)



	

	



	def update_state(state,view_information,code):
		'''		
		normally I would like these to be implemented by means of modification handlers
		And an event listener transmitting every chains in the code. However it seems
		but the provided event listener does not provide me with the location that was changed.
		So in order to keep track over the location of important regions when the code changes,
		The current solution is to outsource everything to the sublime add_regions/get_regions 
		functionality
		'''
		state["result"] = view_information["get_regions"]("result")
		state["alternatives"] = view_information["get_regions"]("alternatives")
		state["origin"] = view_information["get_regions"]("origin")
		state["initial_origin"] = view_information["get_regions"]("initial_origin")
