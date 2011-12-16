"""common classes and functions for modules.
"""

import threading, queue

import util

class kModule(threading.Thread):
	def __init__(self, cf, data_queue, message):
		threading.Thread.__init__(self)
		self.c = cf
		self.q = data_queue
		self.m = message

		self.set_module_info()
		self.setName('thread-%s' % self.mod)

		self.l = util.Log('%s-%s' % (self.typ, self.mod))
		self.l.set_level(cf.get('honcheonui/loglevel'))
		if self.c.get('module/%s/loglevel' % self.mod):
			self.l.set_level(self.c.get(
				'module/%s/loglevel' % self.mod))

		self.__setQueue__()
		self.__prep__()
		self.l.info('%s initiated.' % self.getName())
		return

	def __prep__(self):
		return

	def __fin__(self):
		if self.m['onair']:
			self.l.info('%s finished but ON-AIR!' % self.getName())
		else:
			self.l.info('%s finished. bye!' % self.getName())
		return

	def set_module_info(self):
		self.mod = 'NONAME'
		self.ver = '0.0.0'
		self.typ = 'module'
		return

	def __setQueue__(self):
		self.seq = 0
		self.q.mq[self.mod] = queue.Queue(5)
		self.l.verb('mqueue registered: 0x%x' % id(self.q.mq[self.mod]))
		return

	def queue_request(self, data, path, method = 'put'):
		self.seq += 1
		self.q.dq.put({'type':'request',
			'method':method,
			'owner':self.mod, 'sender':self.mod,
			'sequence':self.seq, 'path':path, 'data':data})
		self.l.debug('waiting 5sec for response...')
		try:
			res = self.q.mq[self.mod].get(timeout=5)
		except queue.Empty:
			self.l.warn('timeout!')
			return False
		self.l.debug('response is %s' % res)
		if res.get('sequence') != self.seq:
			self.l.warn('sequence not match. ignore!')
			return False
		return res

class kHandler(kModule):
	def __setQueue__(self):
		self.q.hq[self.mod] = queue.Queue(-1)
		self.myq = self.q.hq[self.mod]
		self.l.verb('hqueue registered: 0x%x' % id(self.q.hq[self.mod]))
		return


