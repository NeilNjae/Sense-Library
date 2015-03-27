from threading import Thread
import time
class my_thread(Thread()):
	"""docstring for my_thread"""
	def __init__(self):
		pass
	def run():
		for i in range(10):
			print('1')
			time.sleep(1)
board=my_thread
board.run()
for i in range(20):
	print('2')
	time.sleep(0.7)