class ViewInformation():
	def __init__(self, view, sublime):
		self.view = view
		self.sublime = sublime
	def __getitem__(self, value):
		if value == "selection":
			intermediate = self.view.sel()
			temporary = [(x.begin(),x.end()) for x in intermediate]
			return temporary if len(temporary)!=1 else temporary[0]
		elif value == "change_count":
			return self.view.change_count()
		elif value == "id":
			return self.view.id()
		elif value == "code":
			return self.view.substr(self.sublime.Region(0, self.view.size()))
		elif value == "rowcol":
			return self.view.rowcol
		elif value == "text_point":
			return self.view.text_point
		else:
			return None

		
		











