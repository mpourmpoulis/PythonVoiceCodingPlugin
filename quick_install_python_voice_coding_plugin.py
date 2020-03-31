import os
import sys

import sublime
import sublime_plugin




class QuickInstallPythonVoiceCodingPluginCommand(sublime_plugin.WindowCommand):
	def run(self):
		if sublime.platform()!="windows":
			sublime.error_message("Quick install has only meaning in windows")
			return 
		candidates = []
		for user in os.listdir("C:\\Users"):
			for x in [".caster\\rules","AppData\\Local\\caster\\rules"]:
				if os.path.isdir(os.path.join("C:\\Users",user,x)):
					candidates.append(os.path.join("C:\\Users",user,x))
		if not candidates:
			return 
		def on_done(index):
			if index==-1: 
				return 
			c = candidates[index]
			name = "python_voice_coding_plugin_caster_v1-0-0.py"
			if os.path.exists(os.path.join(c,name)):
				if sublime.yes_no_cancel_dialog("The grammar file already exists, surely you want to replace it")!=sublime.DIALOG_YES:
					return

			with open(os.path.join(sublime.packages_path(),"PythonVoiceCodingPlugin\\bundles\\Caster",name),"r") as f:
				s = f.read()
			with open(os.path.join(c,name),"w") as f:
				f.write(s)

		self.window.show_quick_panel(candidates,on_done)		








