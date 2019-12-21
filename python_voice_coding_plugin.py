import os
import sys

import sublime
import sublime_plugin

settings = {}
# making sure our dependencies are in the path
sys.path.insert(0,os.path.join(os.path.dirname(__file__), 'third_party'))

from PythonVoiceCodingPlugin.interface.interface import Interface

# removing our dependencies from the path so as not to interfere with other packages
sys.path.remove(os.path.join(os.path.dirname(__file__), 'third_party'))


def plugin_loaded():
	global settings
	settings = sublime.load_settings("python_voice_coding_plugin.sublime-settings")

	

class PythonVoiceCodingPluginCommand(sublime_plugin.TextCommand,sublime_plugin.ViewEventListener):
	def run(self, edit,arg):
		self.action_one(edit,arg)

	def action_one(self, edit,arg):
		global settings
		print(" the counties ",self.view.change_count())
		interface = Interface(
			sublime = sublime,
			view = self.view,
			window = sublime.active_window(),
			edit = edit,
			settings = settings
		)
		interface.respond_to_query(arg)
		print(" the counties ",self.view.change_count())

	def on_modified(self):
		print(" from the event lease and their side of the plug-in",self.view.change_count())






