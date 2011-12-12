"""
"""

import threading, queue
import time

MODULE	= 'ds_local'
VERSION	= '0.1.0'

class DataStore(threading.Thread):
	def __init__(self, cf, data_queue, message):
		threading.Thread.__init__(self)
		self.c = cf
		self.q = data_queue
		self.m = message
		self.setName('Thread-%s' % MODULE)
		return


class ds_local(DataStore):
	def run(self):
		while self.m['onair']:
			try:
				data = self.q.get(True, 2)
			except queue.Empty:
				continue

			print('ADSF:',data)
