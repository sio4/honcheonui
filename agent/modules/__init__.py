"""common classes and functions for modules.
"""

import threading, queue

import util


class kModule(threading.Thread):
	class Exception(Exception):
		def __init__(self, code, value):
			self.code = code
			self.value = value
			return

		def __str__(self):
			return repr(self.value)

	def __init__(self, cf, data_queue, message):
		threading.Thread.__init__(self)
		self.c = cf
		self.q = data_queue
		self.m = message

		self.set_module_info()
		self.setName('thread-%s' % self.mod)
		self.host_id = int(self.c.get('module/server/id', 0))
		self.basepath = self.c.get('module/%s/path' % self.mod)

		self.l = util.Log('%s-%s' % (self.typ, self.mod))
		self.l.set_level(cf.get('honcheonui/loglevel'))
		if self.c.get('module/%s/loglevel' % self.mod):
			self.l.set_level(self.c.get(
				'module/%s/loglevel' % self.mod))

		self.__setQueue__()
		self.__prep__()
		self.l.verb('setup path:%s, host:%d' % (self.basepath,
				self.host_id))
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

	def abort(self, msg):
		self.m['abort'] = {'flag':True,'owner':self.mod,'reason':msg}
		import _thread
		_thread.interrupt_main()
		exit(0)
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

	def queue_request(self, data, path, method = 'insert',
			believe = False, retry = 5):
		self.seq += 1
		data['server_id'] = self.host_id
		self.q.dq.put({'type':'request',
			'method':method,
			'owner':self.mod, 'sender':self.mod,
			'believe':believe, 'retry':retry,
			'sequence':self.seq, 'path':path, 'data':data})
		self.l.debug('waiting 5sec for response...')
		try:
			res = self.q.mq[self.mod].get(timeout=5)
		except queue.Empty:
			self.l.warn('timeout!')
			return False
		self.l.debug('response is %s' % res)
		if res.get('sequence') != self.seq:
			diff = int(res.get('sequence')) - self.seq
			self.l.warn('sequence not match. (%d) ignore!' % diff)
			return False
		return res

class kHandler(kModule):
	def __setQueue__(self):
		self.q.hq[self.mod] = queue.Queue(-1)
		self.myq = self.q.hq[self.mod]
		self.l.verb('hqueue registered: 0x%x' % id(self.q.hq[self.mod]))
		return


