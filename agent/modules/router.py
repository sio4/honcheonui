"""dummy-local data storage backend module for honcheonui.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os

import queue
import time

MODULE	= 'router'
VERSION	= '0.1.0'

import util
from modules import kModule

class router(kModule):
	def set_module_info(self):
		self.mod = MODULE
		self.ver = VERSION
		self.typ = 'control'
		return

	def __setQueue__(self):
		self.l.verb('i do not need my own queue.')
		return

	def run(self):
		while self.m['onair']:
			# simply get data from queue,
			try:
				data = self.q.dq.get(True, 2)
			except queue.Empty:
				continue
			self.l.debug('get data: %s' % data)

			# then select destinations,
			self.l.debug('queue type is %s' % data.get('type'))
			if data.get('type') == 'response' and data.get('owner'):
				self.l.debug('owner is %s' % data.get('owner'))
				target_qs = [self.q.mq[data.get('owner')]]
			else:
				target_qs = list(self.q.hq.values())

			# ofcause some error corrections,
			if len(target_qs) < 1:
				self.l.error('epp! no queue handler found!')

			# finally send data to destinations.
			self.l.debug('selected queue is %s' % str(target_qs))
			for q in target_qs:
				# replicate to queue handlers.
				self.l.verb('Q[%s:%s:%d] to 0x%x' % (
					data.get('owner'),
					data.get('type'),
					data.get('sequence'),
					id(q)))
				q.put(data)

			# yes, it's my job!
			self.q.dq.task_done()

		self.__fin__()
		return
