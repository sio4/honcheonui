"""Orion plugin, plugin management module for orion project.
"""

__mod_name__	= 'plugin'
__mod_version__	= '0.1.0'

import threading, queue
import time
import orion

class pluginError(orion.orionError):
	def __str__(self):
		return repr('pluginError:%s' % self.strerror)

class Plugin(threading.Thread):
	def __init__(self, pname, pver, ptype, conf, message_queue, logger):
		threading.Thread.__init__(self)
		self.plugin_type = ptype
		self.conf = conf
		self.mqueue = message_queue
		self.logger = logger
		self.__stop = threading.Event()
		self.__chk = threading.Event()
		self.__rpt = threading.Event()

		self.setName('plugin-%s-%s' % (pname, pver))
		self.loglevel = self.conf.get('loglevel')
		if self.plugin_type == 'periodic':
			self.int_chk = int(self.conf.get('check_interval', 0))
			self.int_rpt = int(self.conf.get('report_interval', 0))
			self.logger.info("check every %d, report every %d." %
					(self.int_chk, self.int_rpt))

		self.initialize()
		self.logger.info('%s initialized!' % self.name)
		return

	def initialize(self):
		self.logger.warn('OVERRIDE IT ----')
		return

	def run(self):
		time.sleep(0.5)	# startup delay.
		self.logger.info('starting %s...' % self.name)
		self.task_pre()
		if self.plugin_type == 'periodic':
			self.periodic()
		self.task_post()
		self.logger.info('<%s> finished!' % self.getName())
		return

	def periodic(self):
		self.logger.info('jump into the fire!')
		while not self.__stop.is_set():
			if self.__chk.is_set():
				self.__chk.clear()
				self.task_check()
				if self.__rpt.is_set():
					self.__rpt.clear()
					self.task_report()
			else:
				time.sleep(0.2)	# XXX HARD-CODING, PERFORMANCE
		# XXX check no-more-queue!
		self.logger.info('come out from the duty!')
		return

	def task_pre(self):
		return self.logger.warn('has no task_pre.')

	def task_check(self):
		return self.logger.debug('has no task_check.')

	def task_report(self):
		return self.logger.debug('has no task_report.')

	def task_post(self):
		return self.logger.warn('has no task_post.')

	def stop(self):
		return self.__stop.set()

	def tick(self, now_ts):
		if (now_ts % self.int_chk) == 0:
			self.__chk.set()
		if (now_ts % self.int_rpt) == 0:
			self.__rpt.set()
		return


class PluginManager():
	def __init__(self, conf, logger):
		self.conf = conf
		self.logger = logger.getChild('p')	# short!

		self.mqueue = mQueue()
		self.plugins = list()

		self.logger.info('<plugin manager> initialized!')
		return

	def load_plugin(self, module, wait_until_done):
		self.logger.info('trying to load <%s>...' % module)
		try:
			mod = __import__('modules.%s' % module, fromlist = ['modules'])
			mclass = getattr(mod, module)
			pn = getattr(mod, '_plugin_name')
			pv = getattr(mod, '_plugin_version')
			pt = getattr(mod, '_plugin_type')
			self.logger.info('%s version %s (%s)...' % (pn, pv, pt))
			logger = self.logger.getChild(module)
			conf = self.conf.get_branch('plugins/plugin[@name="%s"]' % module)
			plugin_thread = mclass(pn, pv, pt, conf, self.mqueue, logger)
			plugin_thread.start()
		except (ImportError, AttributeError) as e:
			self.logger.error('cannot import module <%s>' % module)
			self.logger.error('-- E(%s)' % e)
			raise
		except:
			self.logger.info('UNKNOWN EXCEPTION.')
			raise
		else:
			self.plugins.append(plugin_thread)
			self.logger.info('<%s> registered.' % module)

		if wait_until_done:
			self.logger.debug('blocking mode. wait until done.')
			plugin_thread.join(30)
			if plugin_thread.is_alive():
				self.logger.warn('what is happen? still alive!')
			else:
				self.plugins.remove(plugin_thread)
				self.logger.debug('ok, blocked thread finished.')

		return

	def load_plugins(self, ptype, block = False):
		self.logger.info('loading %s plugins...', ptype)
		for plugin in self.conf.subnames('plugins/plugin[@type="%s"]' % ptype):
			self.logger.debug('loading plugin <%s>...' % plugin)
			self.load_plugin(plugin, block)
		return

	def get_list(self):
		return self.plugins

	def tick_at(self, interval):
		while True:
			now_ts = int(time.time())
			if (now_ts % interval) == 0:
				for p in self.plugins:
					if p.is_alive():
						p.tick(now_ts)
				time.sleep(1)	# XXX HARD-CODING, PERFORMANCE, TIMING
				return
			else:
				time.sleep(0.1)	# XXX HARD-CODING, PERFORMANCE
		return

	def clean(self):
		for p in self.plugins:
			p.join(0.1)
			if not p.is_alive():
				self.logger.info('<%s> is done.' % p.getName())
				self.plugins.remove(p)
			else:
				#self.logger.debug('<%s> is alive.' % p.getName())
				pass
		return

	def clean_all(self):
		while len(self.plugins) > 0:
			self.clean()
		return

	def shutdown_modules():
		return




import queue
from collections import namedtuple
class mQueue:
	def __init__(self):
		self.dq = queue.Queue(-1)
		#self.mq = dict()
		#self.hq = dict()


# vim:set ts=4 sw=4:
