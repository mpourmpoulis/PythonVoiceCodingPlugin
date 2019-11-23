import os
import subprocess

from yapsy.IPlugin import IPlugin

enabled =  True

def python_voice_coding_plugin_aenea_send_sublime(c,data):
    x =  str(data).replace('\'','\\\"')
    x = x.replace("u\\","\\")
    y = "subl --command \"" + c + "  " + x + "\""
    print(y)
    subprocess.call(y, shell = True)
    subprocess.call("subl", shell = True)

class PythonVoiceCodingPluginAenea(IPlugin):
	"""docstring for PythonVoiceCodingPluginAena"""
	def register_rpcs(self,server):
		server.register_function(python_voice_coding_plugin_aenea_send_sublime)
		








