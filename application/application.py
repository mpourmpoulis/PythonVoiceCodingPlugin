from copy import deepcopy

from PythonVoiceCodingPlugin.queries import *
from PythonVoiceCodingPlugin.application.build_cache import BuildCache
from PythonVoiceCodingPlugin.application.state_update import clear_state,retrieve_state,retrieve_text,get_location_text,update_changes,update_origin
from PythonVoiceCodingPlugin.interface.common.actions import *


class Application():
	"""docstring for Application"""
	active_applications = {}
	build_cache  = BuildCache()
	global_state = {}
	
	def __init__(self,vid):
		self.history = []
		self.state = {
			"result": None,
			"origin": None,
			"initial_origin":None,
			"alternatives": [],
			"change_count":-1,
			"mode":"single",
			"initial_mode":"single",
			"initial_count":-1, 
		}
		self.ui_controller = None
		self.vid = vid

	def create_application_for_view(vid):
		if vid not in Application.active_applications:
			Application.active_applications[vid] = Application(vid)

	def get_application(vid):
		Application.create_application_for_view(vid)
		return Application.active_applications[vid]

	def update_text(self,code):
		retrieve_text(self.state,code)

	def update_locations(self,locations_text):
		update_changes(self.state,locations_text)


	def respond_to_query(self,interface,query_description,secondary=False):
		extra = {
			"state":self.state,"global_state":Application.global_state,
			"history":self.history,"secondary":secondary,
		}
		view_information  = interface.get_view_information()
		ui_information = interface.get_ui_information()

		# extract code and change count and reuse previous build if possible
		code = view_information["code"]
		change_count = view_information["change_count"]
		latest_build = Application.build_cache.get_build(self.vid,change_count)
		print("state\n\n",self.state,"\n\n")
		try:
			if not secondary:
				print("and during inside here ",query_description)
				need_update = retrieve_state(self.state,view_information,code)
				print("\n needed update: ",need_update,"\n")
				print(" after update this state ",self.state)
		except:
			clear_state(self.state)
			if False:
				raise

		# get the corresponding query and execute it
		s = get_query(query_description)(code,latest_build)
		secondary_query_description = get_secondary_query(query_description)
		if secondary_query_description:
			self.backup=[deepcopy(self.state),deepcopy(self.global_state)]

		try:
			s(view_information,query_description,extra)
		except Exception as e:
			if not s.exceptions_raised:
				print("inside exceptions raised",e)
				raise
				return False
			

		# check if there are exceptions
		if s.exceptions_raised:
			interface.clear_actions()
			interface.push_action(PopUpErrorAction(str(s.exceptions_raised)))
			return False


		# register build for later use
		b = s.get_the_latest_build()
		if b:
			Application.build_cache.register_build(self.vid,change_count,b)

		if 	secondary:
			self.state,self.global_state = self.backup


		if isinstance(s,SelectionQuery):
			result = s.result 
			alternatives  = s.alternatives
			selection = view_information["selection"]

			mode = isinstance(result,list) or isinstance(selection,list)
			update_origin(self.state,"origin",selection,mode)
			update_origin(self.state,"initial_origin",selection,mode)
			self.state["mode"] = "multiple" if mode else "single"
			if self.state["initial_count"]<view_information["change_count"]:
				self.state["initial_mode"] = "multiple" if mode else "single"
				self.state["initial_count"] = view_information["change_count"]

			names = ["result","origin", "alternatives","initial_origin"]
			for name in names:
				interface.push_action(ClearHighlightAction(name))
			if result:
				self.state["result"] = result
				self.state["alternatives"] = alternatives
				# self.state["alternatives_text"] = get_location_text(alternatives,code)
				self.update_text(code)
				interface.push_action(SelectionAction(result))
				self.history.append(("selection",view_information["change_count"],view_information["selection"],result))
				if not isinstance(result,list):
					self.state["mode"] = "single"
				else:
					self.state["mode"] = "multiple"


			
			# if alternatives:
				# interface.push_action(DisplayRegionsAction("alternatives",alternatives,"Alternatives:\n"))

				
		elif isinstance(s,InsertionQuery):
			output = s.writing_locations_text
			selections = s.optional_selection
			if output:
				for location, text in output:
					interface.push_action(ReplaceAction(location,text))
				self.history.append(("insert"))
				self.update_locations(output)

			if selections:
				interface.push_action(SelectionAction(selections))
		
		elif isinstance(s,CollectionQuery):
			result = s.result
			items = s.items
			writing_positions = s.writing_positions
			selections = s.optional_selection
			if result:
				for location in writing_positions:
					interface.push_action(ReplaceAction(location,result))
				self.update_locations([(x,result)  for x in writing_positions])
			if items:
				print(s.label,"labeling\n")
				interface.push_action(DisplayNiceAction(s.label,items,True))  
				self.state["collection"] = items
				self.global_state["collection"] = items
				self.history.append(("collect"))
			if selections:
				interface.push_action(SelectionAction(selections))

		interface.push_action(HighlightCleverAction(self.state["alternatives"],"alternatives",self.state["result"],colorize = True))
		for name in ["result","origin", "initial_origin"]:
			interface.push_action(HighlightCleverAction(self.state[name],name))				


		if secondary_query_description:
			interface.push_action(ClearHighlightAction("alternatives"))
			secondary_success = self.respond_to_query(interface,secondary_query_description,secondary=True)
			if not secondary_success:
				self.state,self.global_state = self.backup
				return False
		return True



	def respond_to_event(self,interface,event_description):
		event = event_description["event"]
		view_information  = interface.get_view_information()
		if event=="update_change_count":
			if self.state["change_count"] != event_description["change_count"]:
				retrieve_text(self.state,view_information["code"])
			self.state["change_count"] = event_description["change_count"]
	



		