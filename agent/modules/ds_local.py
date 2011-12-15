"""dummy-local data storage backend module for honcheonui.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os

import threading, queue
import time

MODULE	= 'ds_local'
VERSION	= '0.1.0'

import util
from modules import kHandler

class ds_local(kHandler):
	def set_module_info(self):
		self.mod = MODULE
		self.ver = VERSION
		self.typ = 'backend'
		return

	def run(self):
		while self.m['onair']:
			try:
				data = self.myq.get(True, 2)
			except queue.Empty:
				self.l.debug('queue.get timeout!')
				continue
			self.l.debug('get %s: %s' % (data.get('type'), data))

			### process here!	------------------------------
			self.l.verb('processing %s...' % data)

			if data.get('type') == 'request' and data.get('owner'):
				ret = {'type':'response',
					'owner':data.get('owner'),
					'sequence':data.get('sequence'),
					'code':201,
					'reason':'ok',
					'data':{'aa':0,'n':'b'}}
				self.q.dq.put(ret)
			self.myq.task_done()

		self.__fin__()
		return
