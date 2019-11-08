import sublime
import sublime_plugin

from noob.interface.interface import Interface


class PythonVoiceCodingPluginCommand(sublime_plugin.TextCommand):
	def run(self, edit,arg):
		self.action_one(edit,arg)

	def action_one(self, edit,arg):
		interface = Interface(
			sublime = sublime,
			view = self.view,
			window = sublime.active_window(),
			edit = edit
		)
		interface.respond_to_query(arg)








