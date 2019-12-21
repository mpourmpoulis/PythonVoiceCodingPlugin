from PythonVoiceCodingPlugin.application.application import Application
from PythonVoiceCodingPlugin.interface.view_info import ViewInformation


class Interface():
	"""docstring for Interface"""
	def __init__(self,view,window,edit,sublime,settings):
		self.view = view
		self.window = window
		self.edit = edit
		self.sublime = sublime
		self.actions = []
		self.settings = settings

	def get_view_information(self):
		return ViewInformation(self.view,self.sublime)

	def get_ui_information(self):
		return None

	def push_action(self,item):
		self.actions.append(item)

	def respond_to_query(self,query_description):
		application = Application.get_application(self.view.id())
		application.respond_to_query(self,query_description)
		parameters = {
			"view":self.view,"window":self.window,"edit":self.edit,"sublime":self.sublime,"settings":self.settings,
		}
		for action in self.actions:
			action.execute(**parameters)

	def respond_to_event(self,event_description):
		self.actions = []
		application = Application.get_application(self.view.id())
		application.respond_to_query(self,query_description)
		parameters = {
			"view":self.view,"window":self.window,"edit":self.edit,"sublime":self.sublime,"settings":self.settings,
		}
		for action in self.actions:
			action.execute(**parameters)


	def clear_actions(self):
		self.actions = []



		

		