import os
import sys

import sublime
import sublime_plugin

greeting = '''
Thanks for trying out PythonVoiceCodingPlugin!  

To complete your installation, you need to copy the bundled grammar for your version of Caster into your appropriate Caster user directory. Afterwards reboot Caster  and if needed enable the grammar by saying

enable python voice coding plugin

You can retrieve those grammars under

Preferences > Package Settings > PythonVoiceCodingPlugin

where you will also find links to documentation with lots of examples and my gitter chatroom for questions and troubleshooting.

To make your life easier with the copy pasting, if you're on windows and using Caster 1.x.x, there is also utility to handle this process automatically for you! Do you want to run it?
'''


def plugin_loaded():
	window = sublime.active_window()
	try :
		from package_control import events
		if events.install("PythonVoiceCodingPlugin"):	 
			if sublime.yes_no_cancel_dialog(greeting)!=sublime.DIALOG_YES:
				return
			window.run_command("quick_install_python_voice_coding_plugin",{})
	except :
		pass



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
			sublime.error_message("No Caster 1.x.x user directory was found! Are you sure you have it installedand you are not using an older version?")
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
			sublime.error_message("Grammar successfully copied!")
		self.window.show_quick_panel(candidates,on_done)		








