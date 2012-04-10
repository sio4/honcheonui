"""Orion runner, process management module for orion project.
"""

__mod_name__	= 'runner'
__mod_version__	= '0.1.0'

import sys
import os

import atexit
import signal
import time

import logging
import logging.handlers

class Daemon:
	initialized = False
	interrupted = False

	def __init__(self, name = 'daemon', pidfile = None):
		self.name = name
		self.pidfile = pidfile
		if pidfile == None:
			self.pidfile = '/tmp/%s.pid' % name

		self.start_ts = time.time()

		# parse arguments and doing maintenece operations.
		self.__parse_options__()

		if self.opts.stop:
			sys.stderr.write('stopping existing process...\n')
			_process(self.__read_pidlock()).kill_existing()
			sys.exit()

		# check existing agent.
		if self.__read_pidlock() > 0:
			sys.stderr.write('pid lock detected. ')
			if self.opts.force:
				sys.stderr.write('force start...\n')
				_process(self.__read_pidlock()).kill_existing()
			else:
				sys.stderr.write('abort!\n')
				sys.exit()

		# ok, it's my own world. redirect stdout/stderr to given files.
		if self.opts.stdout.name != sys.stdout.name:
			os.dup2(self.opts.stdout.fileno(), sys.stdout.fileno())
		if self.opts.stderr.name != sys.stderr.name:
			os.dup2(self.opts.stderr.fileno(), sys.stderr.fileno())

		sys.stderr.write("start my engine...\n")

		# setup logger too, including syslog.
		self.__set_logger()

		if self.opts.debug:
			self.__print_options__()

		# call additional initializer.
		self.initialize()
		self.initialized = True
		self.syslog('%s initialized!' % self.name)
		return

	def __del__(self):
		if self.initialized:
			# finalizing code here!
			self.logger.info("an.yeong~!")
			sys.stderr.write("an.yeong~!\n")	# to hell?
		return

	def initialize(self):
		"""Additional/Custom initializations.
		user can override it with her own method without any limitations.
		"""
		message = ""
		if self.opts.debug:
			message = " (implement %s.initialize)" % __class__.__name__
		self.logger.info("initialize...%s" % message)
		return

	def daemonize(self):
		"""Double fork and daemonize process.
		"""
		self.logger.debug('born to be daemon...')
		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError as e:
			self.logger.critical("fork failed! %d:%s" % (e.errno, e.strerror))
			sys.exit(1)

		os.chdir('/')
		os.setsid()
		os.umask(0)

		try:
			pid = os.fork()
			if pid > 0:
				sys.exit(0)
		except OSError as e:
			self.logger.critical("fork failed! %d:%s" % (e.errno, e.strerror))
			sys.exit(2)

		# duplicate stdout/stderr. (to null or to given files)
		if hasattr(os, 'devnull'):
			null_file = os.devnull
		else:
			null_file = '/dev/null'
		null_i = open(null_file, 'r')
		null_o = open(null_file, 'w')

		os.dup2(null_i.fileno(), sys.stdin.fileno())

		if self.opts.stdout.name == sys.__stdout__.name:
			sys.stdout.flush()
			os.dup2(null_o.fileno(), sys.stdout.fileno())
		else:
			self.logger.debug('stdout redirected to %s. do not dup2.' %
					self.opts.stdout.name)

		if self.opts.stderr.name == sys.__stderr__.name:
			sys.stderr.flush()
			os.dup2(null_o.fileno(), sys.stderr.fileno())
		else:
			self.logger.debug('stderr redirected to %s. do not dup2.' %
					self.opts.stderr.name)

		self.__write_pidlock()
		self.logger.debug('pid %d locked.' % self.__read_pidlock())

		# XXX right position? chk this.
		atexit.register(self.exit_handler)
		signal.signal(signal.SIGINT, self.interrupt_handler)

		self.logger.info('%s[%d] daemonized!' % (self.name, os.getpid()))

		return

	def interrupt_handler(self, signum, frame):
		self.logger.info('----- signal %d received.', signum)
		self.interrupted = True
		return

	def exit_handler(self):
		if os.getpid() == self.__read_pidlock():
			self.logger.debug('ok, remove my own lock.')
			self.__delete_pidfile()
		else:
			self.logger.debug('whoami? my pid is %d, but lock is %d.' %
					(os.getpid(), self.__read_pidlock()))
			self.logger.warn('lock file changed. leave it as is.')
		self.logger.info('ok, exit safely.')
		return


	def runtime(self):
		return time.time() - self.start_ts


	### pid file management		----------------------------------------------
	def __write_pidlock(self):
		f = open(self.pidfile, 'w')
		f.write('%d' % os.getpid())
		f.close()
		return

	def __read_pidlock(self):
		try:
			f = open(self.pidfile, 'r')
			pid = f.read()
			f.close()
		except IOError as e:
			sys.stderr.write('cannot read pid %d:%s\n' % (e.errno, e.strerror))
			pid = -e.errno
		return int(pid)

	def __delete_pidfile(self):
		os.unlink(self.pidfile)
		return


	### log management			----------------------------------------------
	def __set_logger(self):
		self.logger = logging.getLogger(self.name)

		self.logger.setLevel(logging.INFO)
		if self.opts.debug:	# finally, FIXME to use config value.
			self.logger.setLevel(logging.DEBUG)

		time_fmt = '%Y-%m-%d %H:%M:%S'
		log_fmt = '%(asctime)s %(levelname)s:%(name)s %(message)s'
		dbg_fmt = log_fmt + ' (%(filename)s:%(lineno)d)'
		formatter_log = logging.Formatter(log_fmt, time_fmt)
		formatter_dbg = logging.Formatter(dbg_fmt, time_fmt)

		if self.opts.logfile:
			### FIXME check permission for logfile.
			fh = logging.handlers.TimedRotatingFileHandler(self.opts.logfile,
					when = 'h', interval=1, backupCount=10)
			fh.setFormatter(formatter_log)
			self.logger.addHandler(fh)

		if self.opts.debug:	# add stream and level up! for debug.
			if self.opts.logfile:
				fh.setFormatter(formatter_dbg)
			ch = logging.StreamHandler(sys.stdout)
			ch.setFormatter(formatter_dbg)
			self.logger.addHandler(ch)

		# syslog for general informations.
		self._syslog = logging.getLogger(self.name + '.syslog')
		self._syslog.setLevel(logging.INFO)
		sh = logging.handlers.SysLogHandler(address='/dev/log',
				facility='daemon')
		self._syslog.addHandler(sh)
		self.logger.info('logger started')
		return

	def syslog(self,message):
		if self.opts.syslog:
			self._syslog.info(message)
		else:
			self.logger.info(message)
		return


	### argument parser					--------------------------------------
	def __parse_options__(self):
		import argparse
		parser = argparse.ArgumentParser(
				description = 'Daemon Options.'
				)
		group = parser.add_mutually_exclusive_group(required=True)
		group.add_argument('--start', action='store_true',
				help='start program in normal mode')
		group.add_argument('--stop', action='store_true',
				help='stop existing program in graceful way')
		parser.add_argument('-m', '--mode', dest='mode', default='start',
				help='operation mode')
		parser.add_argument('-c', '--conf', dest='config', default=None,
				help='configuration file', metavar='FILE')
		parser.add_argument('-l', '--log', dest='logfile', default=None,
				help='log file to save printed messages', metavar='FILE')
		parser.add_argument('-o', '--stdout', dest='stdout',
				default=sys.stdout, type=argparse.FileType('a'),
				help='send output to FILE instead of stdout', metavar='FILE')
		parser.add_argument('-e', '--stderr', dest='stderr',
				default=sys.stderr, type=argparse.FileType('a'),
				help='send error to FILE instead of stderr', metavar='FILE')
		parser.add_argument('-d', '--debug', dest='debug', action='store_true',
				help='running in debugging mode')
		parser.add_argument('-f', '--force', dest='force', action='store_true',
				help='kill existing agent and run new one.')
		parser.add_argument('-s', '--syslog', dest='syslog',
				action='store_true', help='log on syslog too.')
		self.opts = parser.parse_args()
		return

	def __print_options__(self):
		if not self.opts.debug:
			return

		self.logger.debug('initial options:')
		for k in vars(self.opts):
			self.logger.debug('- option %s is %s' % (k, vars(self.opts)[k]))

		return


### utility class		------------------------------------------------------
class _process:
	def __init__(self, pid):
		self.pid = pid
		return

	def kill_signal(self, signum):
		try:
			os.kill(self.pid, signum)
		except OSError as e:
			if e.errno == 3:
				pass
			else:
				sys.stderr.write('Exception %d:%s\n' % (e.errno, e.strerror))
			return e.errno
		return 0

	def wait_until_running(self, timeout = 5):
		for i in range(0,timeout):
			if not os.path.exists('/proc/%d' % self.pid):
				return False
			time.sleep(1)
		return True

	def kill_existing(self):
		if self.pid <= 0:
			sys.stderr.write('cannot get pid. do nothing.\n')
			sys.exit()

		ret = self.kill_signal(signal.SIGINT)
		if ret == 3:
			sys.stderr.write('cannot send signal. already killed?\n')
			return True
		sys.stderr.write('sent SIGINT to %d. wait... ' % self.pid)
		sys.stderr.flush()
		self.wait_until_running(20)

		ret = self.kill_signal(signal.SIGTERM)
		if ret == 3:
			sys.stderr.write('ok, exited.\n')
			return True
		sys.stderr.write('alive yet!\nsent SIGTERM to %d. wait... ' % self.pid)
		sys.stderr.flush()
		self.wait_until_running(5)

		ret = self.kill_signal(signal.SIGKILL)
		if ret == 3:
			sys.stderr.write('ok, terminated!\n')
			return True
		sys.stderr.write('alive yet!\nsent SIGKILL to %d. wait... ' % self.pid)
		sys.stderr.flush()
		self.wait_until_running(2)

		ret = self.kill_signal(signal.SIGKILL)
		if ret == 3:
			sys.stderr.write('ok, killed!\n')
			return True
		sys.stderr.write('ERROR! process alive YET! cannot kill!\n')
		sys.stderr.flush()
		return False

# vim:set ts=4 sw=4:
