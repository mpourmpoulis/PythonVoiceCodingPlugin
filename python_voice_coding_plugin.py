import os
import sys

import sublime
import sublime_plugin

# making sure our dependencies are in the path
sys.path.insert(0,os.path.join(os.path.dirname(__file__), 'third_party'))

from PythonVoiceCodingPlugin.interface.interface import Interface

# removing our dependencies from the path so as not to interfere with other packages
sys.path.remove(os.path.join(os.path.dirname(__file__), 'third_party'))

class PythonVoiceCodingPluginCommand(sublime_plugin.TextCommand):
	def run(self, edit,arg):
		print("Iran")
		self.action_one(edit,arg)

	def action_one(self, edit,arg):
		interface = Interface(
			sublime = sublime,
			view = self.view,
			window = sublime.active_window(),
			edit = edit
		)
		interface.respond_to_query(arg)








