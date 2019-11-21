class InterfaceAction():
	"""docstring for InterfaceAction"""
	def __init__(self):
		self.data={}
	def execute(self,view):
		pass


class SelectionAction(InterfaceAction):
	"""docstring for SelectionAction"""
	def __init__(self, region):
		self.data={"region":region}

	def execute(self,view,sublime,**kwargs):
		region =  self.data["region"]
		if region:
			view.sel().clear()
			if not isinstance(region,list):
				region = [region]
			for r in region:
				view.sel().add(sublime.Region(r[0],r[1]))
			view.show(sublime.Region(region[0][0],region[0][1]))



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
	def __init__(self, region,name, result):  
		self.data = {"region":region, "name":name , "result":result}

	def execute(self,view,sublime,**kwargs):
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
		region =  self.data["region"]
		if not isinstance(region ,list):
			region = [region]
		region  = [ sublime.Region(x[0],x[1])  for x in region if x]

		# transform the result into a sublime region
		result = self.data["result"]
		result = sublime.Region(result[0],result[1])

		for i,(r,c) in enumerate(zip(region,color_order)):
			use_reinforced = False
			# we use reinforced color if the region is contained within another 
			for x,y in zip(region,color_order):
				if x.contains(r) and x is not r:
					use_reinforced = True

			# to avoid foreground background problems if the region contains the selection it will not be reinforced
			if r.contains(result):
				use_reinforced = False
			# however if the region is contained within the selection it must be reinforced
			elif result.contains(r):
				use_reinforced = True
			if r.b-r.a==1:
				use_reinforced = True
			# we add the region alongside with an index
			view.add_regions(self.data["name"]+str(i+1), [r], reinforced_color[c] if use_reinforced else standard_color[c],
				"circle")





		
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


		









