"""
interfaces.py
-------------
A set of parent classes to structure the flow through
the network stack.
"""

class StackLayer:
	"""
	A parent class for stack layers which establishs
	a common interface to pass messages through a
	layer.
	Parameters:
		- up_queue: a queue to which incoming messages
			will be passed in order to move up the stack
		- down_queue: a queue to which higher up stack
			layers can pass a message in order to have
			it send downwards through the stack
			and eventually sent.
	"""

	def __init__(self):
		self._up_queue = queue.Queue()
		self._down_queue = queue.Queue()

	def passDown (self, msg):
		self._down_queue.put(msg)

	def passUp (self, msg):
		self._up_queue.put(msg)