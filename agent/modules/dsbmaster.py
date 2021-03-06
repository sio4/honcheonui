"""master data storage backend module for honcheonui.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os

import threading, queue
import time

MODULE	= 'dsbmaster'
VERSION	= '0.1.0'
MTYPE	= 'backend'

import honcheonui
import util
from modules import kHandler

class dsbmaster(kHandler):
	def __prep__(self):
		self.master = True
		return

	def set_module_info(self):
		self.mod = MODULE
		self.ver = VERSION
		self.typ = MTYPE
		return

	def run(self):
		comm = honcheonui.Communication(self.c.get('master/host'),
				self.c.get('master/port'))
		has_error = False
		while self.m['onair']:
			try:
				req = self.myq.get(True, 0.5)
			except queue.Empty:
				self.l.debug('queue.get timeout!')
				continue
			self.l.debug('req.get %s: %s' % (req.get('type'), req))

			### process here!	------------------------------
			if not req.get('path'):
				self.l.error('no path given. format error!')
				self.myq.task_done()
				continue

			token = self.c.get('master/token')
			if len(token) > 10:
				path = '%s.json?%s' % (req['path'], token)
			else:
				path = '%s.json' % req['path']

			try:
				self.l.debug('send json %s...' % req['method'])
				if req.get('method') == 'insert':
					res = comm.json_post(path, req['data'])
				elif req.get('method') == 'update':
					res = comm.json_put(path, req['data'])
				else:
					fmt = 'unknown method <%s>. ignore.'
					self.l.error(fmt % req.get('method'))

				code,reason,body = res
			except honcheonui.CommunicationError as e:
				has_error = True
				self.l.error('network error! (%s)' % e.value)
				# XXX if timeout/countout, make error!
				time.sleep(1)
				comm.connect()
				if req['believe'] and req['retry'] > 0:
					self.l.debug('believe mode. requeue.')
					time.sleep(0.5)
					req['retry'] -= 1
					self.myq.put(req)

				#self.myq.task_done()
				continue

			if has_error:
				has_error = False
				self.l.verb(comm.__stat_str__())
				self.l.verb(comm.__error_stat_str__())

			### response if needed.	------------------------------
			if req.get('type') == 'request' and self.master:
				self.response(req, code, reason, body)
			self.myq.task_done()

		self.__fin__()
		return

	def response(self, request, code, reason, body):
		if not request.get('owner'):
			return False
		ret = {'type':'response',
			'owner':request.get('owner'),
			'sequence':request.get('sequence'),
			'code':code,
			'reason':reason,
			'data':body}
		self.l.verb('response to %s: c%d,s%d' % (request.get('owner'),
			ret['code'],
			ret['sequence'],
			))
		self.q.dq.put(ret)
		return True

