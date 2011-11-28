########
#	by sio4@users.sf.net
#
#	common utility functions and classes for any programs

import sys, os

module_name = 'util'


def printerr(string):
	sys.stderr.write("sound-of-%s: %s\n" % (module_name, string))
	return

### class xmlConfig	------------------------------------------------------
import libxml2

class configError:
	code = 0
	desc = 'configuration error.'

	def __init__(self, code, desc):
		self.code = code
		self.desc = desc
		return

class Config:
	doc = None

	def __init__(self, xml):
		if os.access(xml, os.R_OK) == False:
			err = configError(1, 'cannot access config. (%s)' % xml)
			raise err
		try:
			self.doc = libxml2.parseFile(xml)
		except libxml2.parserError:
			err = configError(2, "cannot parse configuration file.")
			raise err
		except:
			raise
		return

	def set(self, key, value):
		nodelist = self.doc.xpathEval('//config/%s' % key)
		if len(nodelist) > 1:
			printerr("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			printerr("oops! not implemented!")
			return None
		return nodelist[0].setContent(value)

	def get(self, key):
		nodelist = self.doc.xpathEval('//config/%s' % key)
		if len(nodelist) > 1:
			printerr("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			printerr("oops! no value found!")
			return None
		return nodelist[0].content

	def show(self):
		str = self.doc.serialize('utf-8')
		print str
		return

	def save(self, filename):
		self.doc.saveFormatFile(filename, 1)
		return


### class Log	--------------------------------------------------------------
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
		return

	def set_level(self, lev):
		self.level = level_map.get(lev)
		return

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



