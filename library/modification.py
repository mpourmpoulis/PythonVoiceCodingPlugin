class ModificationHandler():
	""" This module is responsible for tracking indices off text that undergoes change.

	In particular, consider the case where we have located a region of interest in the original code but we have to
	Make changes to the code, for instance to fix some syntactic error. This module enables us to find the indices of the
	specific region of interest in the new code.

	to achieve this goal we maintain a history of all changes one by one.forever changewe store the following information:
	Origin: the original interval in the [start, end) format
	destination: the original interval in the [start, end) format



	"""
	def __init__(self, initial_code = None):	
		self.initial_code = initial_code
		self.current_code = initial_code
		self.current_time =  0
		self.history = []

	def add_modification(self, origin, destination,original_code  = None,destination_code = "", comment= None):
		"""the basic building block for adding modifications but you should probably use the modify function below
		
		Args:
		    origin (Tuple): the original interval in the [start, end) format
		    destination (Tuple): the final interval in the [start, end) format
		    original_code (str, optional): original code. Defaults to None
		    destination_code (str, optional): final code. Defaults to ""
		    comment (str, optional): extra information regarding the change made
		
		Returns:
		    int : returns the current timestamp
		"""
		assert origin[0] == destination[0], (origin, destination)
		if original_code is None and self.current_time==self.get_timestamp():
			original_code = self.current_code[origin[0]: origin[1]] if self.initial_code else None
		self.history.append((origin, destination,original_code,destination_code,comment))
		return len(self.history)


	def add_modification_from(self,timestamp,  origin, destination,original_code  = None,destination_code = "", comment= None):
		"""a variant of the brief use method that allows you to specify which time in the past the intervals were valid.
		   useful if for instance you want to push multiple regions of interest you have just located
		
		Args:
		    timestamp (int): the time intervals were valid
		    origin (Tuple): the original interval in the [start, end) format
		    destination (Tuple): the final interval in the [start, end) format
		    original_code (str, optional): original code. Defaults to None
		    destination_code (str, optional): final code. Defaults to ""
		    comment (str, optional): extra information regarding the change made
		
		Returns:
		    int : returns the current timestamp
		"""
		origin = self.forward(origin,timestamp)
		destination = self.forward(destination,timestamp)
		return self.add_modification(origin, destination, original_code, destination_code,comment)
	
	def add_modification_updated(self, origin, destination,original_code  = None,destination_code = "", comment= None):
		return self.add_modification_from(self.current_time, origin, destination,original_code ,destination_code , comment)
		
		

	def modify(self,origin,destination_code = "", comment= None):
		destination = ( origin[0], origin[0] + len(destination_code))
		original_code = None
		return self.add_modification(origin, destination, original_code, destination_code,comment)

	def modify_from(self, timestamp, origin ,destination_code = "", comment= None):
		origin = self.forward( origin, timestamp)
		return self.modify(origin, destination_code,comment)


	def modify_updated(self, origin, destination_code = "", comment= None):
		return self.modify_from(self.current_time, origin, destination_code, comment)



	def single_forward(self, value, difference):
		"""transforms an interval after applying a single modification to the future 
		
		Args:
		    value (Tuple): interval in the [start,end) format
		    difference (Tuple): Description
		
		Returns:
		    Tuple or None: Description
		"""
		if value is None:
			return None
		origin = difference[0]
		destination = difference[1]
		k = lambda x: 1 if x < origin[0] else 3 if x >= origin[1] else 2
		state = (k(value[0]),k(value[1]))
		l = destination[1]-origin[1]
		'''
			for the time being we use the following table:
				State   |   action
				--------|------------
				 (1,1)  | return interval as is
				 (1,2)  | undefined
				 (1,3)  | intervals transformed from inside, ending shifted accordingly
				 (2,2)  | undefined , probably should simply eliminate it
				 (2,3)  | undefined
				 (3,3)  | shift interval to the left or to the right
		'''
		return ( 
			value if state in [(1,1)] else
			(value[0] + l,value[1] + l) if state in [(3,3)] else 
			(value[0],value[1] + l) if state in [(1,3)] else 
			destination if state in [(2,2)] else
			(destination[0],value[1] + l) if state in [(2,3)] else
			(value[0],destination[1]) if state in [(1,2)] else None
		)

	def single_backward(self, value, difference):
		if value is None:
			return None
		origin = difference[1]
		destination = difference[0]
		k = lambda x: 1 if x < origin[0] else 3 if x >= origin[1] else 2
		state = (k(value[0]),k(value[1]))
		l = destination[1]-origin[1]
		'''
			for the time being we use the following table:
				State   |   action
				--------|------------
				 (1,1)  | return interval as is
				 (1,2)  | undefined
				 (1,3)  | undefined, probably should grow up/transform then inner interval and and shift
				 (2,2)  | undefined , probably should simply eliminate it
				 (2,3)  | undefined
				 (3,3)  | shift interval to the left or to the right
		'''
		return ( 
			value if state in [(1,1)] else
			(value[0] + l,value[1] + l) if state in [(3,3)] else 
			(value[0],value[1] + l) if state in [(1,3)] else 
			destination if state in [(2,2)] else
			(destination[0],value[1] + l) if state in [(2,3)] else
			(value[0],destination[1]) if state in [(1,2)] else None
		)

	def get_timestamp(self):
		return len(self.history)

	def forward(self,value,start_time = 0,end_time = 0):
		if value is None: 
			return None
		end_time = end_time if end_time!=0 else len(self.history)	
		for i in range(start_time,end_time):
			value = self.single_forward(value,self.history[i])
		return value

	def backward(self,value,start_time = 0,end_time = 0):
		if value is None: 
			return None
		end_time = end_time if end_time!=0 else len(self.history)	
		for i in range(end_time-1,start_time-1,-1):
			value = self.single_backward(value,self.history[i])
		return value

	def single_forward_text(self, text, difference):
		origin = difference[0]
		new_text = difference[3]
		x,y = origin[0], origin[1]
		return text[:x] + new_text + text[y:]

	def single_backward_text(self, text, difference):
		origin = difference[1]
		new_text = difference[2]
		x,y = origin[0], origin[1]
		print(x,y)
		return text[:x] + new_text + text[y:]

	def get_by_comment(self, target):
		return [(x,t)  for t,x in enumerate(self.history) if  x[4] == target]

	def update(self):
		"""applies modifications not applied to the current code to stay update
		"""
		while self.current_time<self.get_timestamp():
			x = self.history[self.current_time]
			x = x if x[2] is not None else (x[0],x[1],self.current_code[x[0][0]:x[0][1]],x[3],x[4])
			self.history[self.current_time] = x
			self.current_code = self.single_forward_text(self.current_code,x)
			self.current_time += 1



def test_one():	
	m = ModificationHandler("h")
	m.add_modification((10,12),(10,10),"cc")
	m.add_modification((10,12),(10,15))
	f = [(1,3),(13,14)]
	
	print(m.forward((14,15)))
	print(m.forward((16,17),1))
	print(m.forward((12,12),0,1))
	print(m.forward((12,13),0,1))
	print(m.backward((19,20),1))
	print(m.backward((19,20)))
	print(m.single_forward_text("aaaaabbbccccccddd",m.history[0]))
	print(m.single_backward_text("aaaaabbbccccddd",m.history[0]) == "aaaaabbbccccccddd")

def test_two():
	m = ModificationHandler("these is funny")
	m.modify((6,8),"was")
	m.modify_from(0,(12,14),"") 
	print(m.current_code,m.current_time,m.history)
	m.update()
	print(m.current_code,m.current_time,m.history)
	m.modify_from(0,(14,14),"aa")
	m.update( )
	print(m.current_code,m.current_time)
	m.modify((0,5),"that")
	m.modify_updated((6,9),"has been")
	m.update()
	print(m.current_code,m.current_time,m.history)



if __name__ == '__main__':
	test_two()



	