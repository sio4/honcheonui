########
#	by sio4@users.sf.net
#
#	common utility functions and classes for any programs

import sys
import os


### class log	--------------------------------------------------------------
level_map = {'debug':1, 'info':2, 'warn':3, 'error':4, 'critical':5 }

class Log:
	tag = 'log'
	level = 3

	def __init__(self, tag, lev = 'warn'):
		self.tag = tag
		self.level = level_map.get(lev)
		return

	def __print__(self, level, string):
		sys.stderr.write("%s:%s: %s\n" % (self.tag, level, string))

	def debug(self, string):
		if self.level == 1:
			self.__print__('DEBUG', string)
		return

	def info(self, string):
		if self.level <= 2:
			self.__print__('', string)
		return

	def warn(self, string):
		if self.level <= 3:
			self.__print__('warnning', string)
		return

	def error(self, string):
		if self.level <= 4:
			self.__print__('error', string)
		return

	def fatal(self, string, code = 99):
		self.__print__('FATAL', string)
		exit(code)


### process handling	------------------------------------------------------

def read_pidlock(pidfile):
	f = open(pidfile, 'r')
	pid = f.read()
	f.close()
	return pid

def write_pidlock(pidfile):
	f = open(pidfile, 'w')
	f.write("%d" % os.getpid())
	f.close()
	return True

def backgroud():
	child_pid = os.fork()
	if child_pid != 0:
		exit(0)

import signal
def doublekill(pid):
	try:
		os.kill(pid, signal.SIGINT)
		time.sleep(2)
		os.kill(pid, signal.SIGKILL)
	except OSError:
		return True
	return False



