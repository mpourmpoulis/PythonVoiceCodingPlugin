import html

from itertools import zip_longest

from PythonVoiceCodingPlugin.interface.common.utility import make_region,make_sequence,all_or_nothing

class InterfaceAction():
	"""docstring for InterfaceAction"""
	def __init__(self):
		self.data = {}
	def execute(self,view):
		pass


class SelectionAction(InterfaceAction):
	"""docstring for SelectionAction"""
	def __init__(self, region):
		self.data={"region":region}

	def execute(self,view,settings,sublime,**kwargs):
		region =  self.data["region"]
		if region:
			view.sel().clear()
			if not isinstance(region,list):
				region = [region]
			for r in region:
				if isinstance(r,list):
					for x in r:
						view.sel().add(sublime.Region(x[0],x[1]))
				else:
					view.sel().add(sublime.Region(r[0],r[1]))
			if settings.get("show_invisible",False):
				try : 
					view.show(sublime.Region(region[0][0],region[0][1]))
				except :
					view.show(sublime.Region(region[0][0][0],region[0][0][1]))
				
			



class InsertAction(InterfaceAction):
	"""docstring for InsertAction"""
	def __init__(self, point,text):
		self.data = {
			"point":point,
			"text":text,
		}

	def execute(self,view,edit,**kwargs):
		view.insert(edit,self.data["point"],self.data["text"])
		
class ReplaceAction(InterfaceAction):
	"""docstring for ReplaceAction"""
	def __init__(self,region,text):
		self.data = {"region":region, "text":text}

	def execute(self,view,edit,sublime,**kwargs):
		region = self.data["region"]
		view.replace(edit,sublime.Region(region[0],region[1]),self.data["text"])

class ClearHighlightAction(InterfaceAction):
	"""docstring for ClearHighlightAction"""
	def __init__(self,name):
		self.data = {"name":name}
	def execute(self,view,**kwargs):
		index = 0
		while True:
			index+=1
			r = view.get_regions(self.data["name"]+str(index)) 
			if r:
				view.erase_regions(self.data["name"]+str(index))
			else:
				break

class HighlightAction(InterfaceAction):
	"""docstring for HighlightAction(InterfaceAction"""
	def __init__(self, region,name,color,outline):
		self.data = {"region":region, "name":name ,"color":color, "outline":outline}

	def execute(self,view,sublime,**kwargs):
		region =  self.data["region"]
		if not isinstance(region ,list):
			region = [region]
		region  = [ sublime.Region(x[0],x[1])  for x in region if x] # check added to avoid crushing by NoneType
		view.add_regions(self.data["name"],region,self.data["color"],self.data["outline"])

class HighlightManyAction(InterfaceAction):
	"""docstring for HighlightAction(InterfaceAction"""
	def __init__(self, region,name):
		self.data = {"region":region, "name":name }

	def execute(self,view,sublime,**kwargs):
		color_map = ["redish","bluish","greenish","yellowish","orangish"]
		color_map = ["region."+x  for x in color_map]
		region =  self.data["region"]
		if not isinstance(region ,list):
			region = [region]
		region  = [ sublime.Region(x[0],x[1])  for x in region if x]
		for i,x in enumerate(region):
			view.add_regions(self.data["name"]+str(i+1), [x],color_map[i%len(color_map)])
			if i==len(color_map)-1:
				break

class HighlightCleverAction(InterfaceAction):
	"""docstring for HighlightAction(InterfaceAction"""
	def __init__(self, region,name, avoid = [],colorize = False):  
		self.data = {"region":region, "name":name , "avoid":avoid,"colorize":colorize}

	def execute(self,view,sublime,**kwargs_x):
		# these are the standard color maps for highlighting using the region-ish api
		standard_color={
			"red":"redish", "blue":"bluish", "green":"greenish", "yellow":"yellowish", "orange":"orangish"
		}
		standard_color={x:"region."+standard_color[x]  for x in standard_color}

		# these are some more intense colors to be used in case of overlapping intervals
		reinforced_color ={
			"red":"keyword.control.flow.break.python",
			"blue":"variable.function.python",
			"green":"entity.name.class.python",
			"orange":"variable.parameter.python",
			"yellow":"string",
		}

		# the default color order
		color_order = ["red","blue","green","yellow","orange"]

		# transform the region variable into at list of sublime regions
		single_mode = False
		region =  self.data["region"]
		if not isinstance(region ,list):
			region = [[region]] if region else [[]]
		elif isinstance(region,list):
			assert all_or_nothing(region,isinstance,list)," singular regions and sequences of regions are mixed"
			if all(not isinstance(x,list) for x in region):
				region = [[x]  for x in region]
				single_mode = True
		region = make_region(region)

		# transform the result into a sublime region
		avoid = self.data["avoid"]
		avoid = make_region(avoid) if avoid else []
		avoid_sequence = make_sequence(avoid)
		overlapping = make_sequence(region) + make_sequence(avoid)
		# print("Regent:\n",region)
		for i,(br,c) in enumerate(zip_longest(region,color_order,fillvalue = None)):
			use_reinforced = False
			if br  is None:
				continue
			for r in br:
				use_reinforced = any(
					(x.contains(r) and x is not r) or (r.contains(x) and x in avoid_sequence)  
					for x in overlapping
				) or r.b-r.a==1 or use_reinforced
			if self.data["colorize"] and i<5:
				view.add_regions(self.data["name"]+str(i+1), br,
					  reinforced_color[c] if use_reinforced  and  single_mode else standard_color[c],"circle")
			else:
				view.add_regions(self.data["name"]+str(i+1),br)






		
class DisplayAction(InterfaceAction):
	"""docstring for DisplayRawAction"""
	def __init__(self, text):
		self.data = {"text":text}
	def execute(self,view,window,**kwargs):
		panel = window.create_output_panel("noob_voice_coding_plugin_panel")
		panel.set_syntax_file("Packages/Python/Python.tmLanguage")
		panel.run_command("append",{"characters":self.data["text"]})
		window.run_command("hide_panel",{"panel":"console"}) 
		window.run_command("show_panel",{"panel":"output.noob_voice_coding_plugin_panel"})


def shape_output_beautiful(variables,label):
	current = 0
	text = []
	maximum_length = max([len(variable + " " + str(index + 1) + " ") 
		for index,variable in enumerate(variables)])
	variables_per_line = min(12, 147//maximum_length)
	available = 147//variables_per_line
	for index,variable in enumerate(variables):
		if index%variables_per_line == 0:
			if index!=0 :
				text.append("\n")
			else:
				text.append(label + ":\n")
		string_index = str( index  + 1)
		value = variable.ljust(available,'.')[:-1*(len(string_index)+1)]+string_index+ " "
		text.append(value)
	return "".join(text)


class DisplayNiceAction(InterfaceAction):
	"""docstring for DisplayNiceAction"""
	def __init__(self, label,items,preserve_order):
		self.label = label
		self.items = items
		self.preserve_order = preserve_order

	def execute(self,view,window,**kwargs):
		panel = window.create_output_panel("python_voice_coding_plugin_panel")
		panel.set_syntax_file("Packages/Python/Python.tmLanguage")
		panel.run_command("append",{"characters":shape_output_beautiful(self.items,self.label)})
		window.run_command("hide_panel",{"panel":"console"}) 
		window.run_command("show_panel",{"panel":"output.python_voice_coding_plugin_panel"})

		
			
class DisplayRegionsAction(InterfaceAction):
	"""docstring for DisplayRawAction"""
	def __init__(self, name, regions, text):
		self.data = {"name":name, "regions":regions,"text":text}

	def execute(self,view,window,sublime,**kwargs):
		regions  = self.data["regions"] 
		regions = [sublime.Region(x[0],x[1])  for x in regions if x]
		panel = window.create_output_panel("python_voice_coding_plugin_panel")
		panel.set_syntax_file("Packages/Python/Python.tmLanguage")
		panel.run_command("append",{"characters":self.data["text"]})
		for i,r in enumerate(regions):
			panel.run_command("append",{  "characters": str(i+1)+" : "+ view.substr(r)+"\n" })
		window.run_command("hide_panel",{"panel":"console"}) 
		window.run_command("show_panel",{"panel":"output.python_voice_coding_plugin_panel"})
	
class PopUpErrorAction(InterfaceAction):
	"""docstring for DisplayErrorAction"""
	def __init__(self, text):
		self.text = text

	def execute(self,view,settings, sublime,**kwargs):
		if not settings.get("show_error",False):
			return 
		final_text = "<p></p><h>Something is off!</h>" + "<p>" + html.escape(self.text,quote = False) + "</p>"
		def on_hide():
			view.show_popup(final_text,max_width=1024, max_height=10000, flags= sublime.HIDE_ON_MOUSE_MOVE_AWAY)
		view.show_popup(final_text,max_width=1024, max_height=10000, 
			flags= sublime.HIDE_ON_MOUSE_MOVE_AWAY,on_hide = on_hide)
		print(view.is_popup_visible())
# hello world
#  style=\"background-color:#000080\"
		
class CopyAction(object):
	"""docstring for CopyAction"""
	def __init__(self, text):
		self.text = text

	def execute(self,view,sublime,**kw):
		sublime.set_clipboard(self.text)
		text_display = "<h>Clipboard set with:</h>" + "<p>" + html.escape(self.text,quote = False) + "</p>"
		view.show_popup(text_display,max_width=1024, max_height=10000, 
			flags= sublime.HIDE_ON_MOUSE_MOVE_AWAY)
	




























'''
class PanelAction(InterfaceAction):
	"""docstring for PanelAction"""
	def __init__(self, panel_name,text,refresh):
		super(PanelAction, self).__init__()
		self.panel_name = panel_name
		self.text = text
		self.refresh = refresh
	
	def execute(self,view):
		when = sublime.active_window()
		panel = when.find_output_panel(self.panel_name)
		if not panel or refresh:			
			panel = when.create_output_panel("my_panel")
			panel.set_syntax_file("Packages/Python/Python.tmLanguage")
		panel.run_command("append",{  "characters": self.text})
		when.run_command("hide_panel",{"panel":"console"}) 
		when.run_command("show_panel",{"panel":"output." + self.panel_name})
'''	


		









