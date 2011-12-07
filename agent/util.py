"""common utility library for config and log handling

It provides basic configuration handling in xml format and log handling.

Class 'Config' provides get/set/save functionality for configuration in
xml file.  configuration values can be accessed via get() method and
assigned via set() method.  both methods use xpath like convention for
configuration key.  updated configurations can be stored to xml file via
save() method.  for automatic save at assign, user can pass additional
parameter to set().

Class 'Log' currently provides simple print() like methods including
debug(), info(), warn(), error() and fatal().  it provides 'tag' and
'level' for logs, so user can handle verboseness of logs, and logs are
distinct by tags.  'level' and 'tag' can be reset by set_level() and
set_tag() methods, so user can easily control the logs.

currently, all messages are printed to standard out. (no file writer
supported yet.)  method fatal() has exit() feature too, but it can be
handled with additional parameter.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os

MODULE = 'util'
VERSION = '0.1.0'


def printerr(string):
	"""Print error message to standard error."""
	sys.stderr.write("sound-of-%s: %s\n" % (MODULE, string))
	return

### class xmlConfig	------------------------------------------------------
from xml.etree import ElementTree

class configError(Exception):
	"""Configuration Error"""
	def __init__(self, code, value):
		self.code = code
		self.value = value

	def __str__(self):
		return repr(self.value)

class Config:
	"""Common xml configuration handler."""
	def __init__(self, xml):
		"""Initialize with xml filename"""
		if os.access(xml, os.R_OK) == False:
			raise configError(1, 'cannot access config. (%s)' % xml)

		try:
			self.doc = ElementTree.ElementTree(file=xml)
		except ElementTree.ParseError as e:
			raise configError(2, 'cannot parse config. (%s)' % xml)

		self.filename = xml
		return

	def set(self, key, value, save = False):
		"""Set configuration value on 'key'
		If argument 'save' is True, it call method save() too.
		If there is more than one node with save path, first on is used.
		"""
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			printerr("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			printerr("oops! do you want add? not implemented!")
			return None
		nodelist[0].text = value
		if save == True:
			self.save()
		return

	def get(self, key):
		"""Get configuration value on 'key'
		If there is more than one node with save path, first on is used.
		"""
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			printerr("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			printerr("oops! no value found!")
			return None
		return nodelist[0].text

	def save(self, filename = 'auto'):
		"""Save current configuration on xml file.
		If argument 'filename' is not given, write on current file.
		"""
		if filename == 'auto':
			filename = self.filename
		if ElementTree.VERSION >= "1.3.0":	# for python 3.x
			self.doc.write(filename, 'utf-8', xml_declaration=True)
		else:
			self.doc.write(filename, 'utf-8')
		return


### class Log	--------------------------------------------------------------
level_map = {'debug':1, 'info':2, 'warn':3, 'error':4, 'critical':5 }

class Log:
	"""Common log handler."""
	tag = 'log'
	level = 3

	def __init__(self, tag, lev = 'warn'):
		"""Initialize with log-tag and log-level.
		Currently log-to-file is not supported.
		"""
		self.tag = tag
		self.level = level_map.get(lev)
		return

	def __print__(self, level, string):
		sys.stderr.write("%s:%s: %s\n" % (self.tag, level, string))
		return

	def set_tag(self, tag):
		"""Set log new log tag."""
		self.tag = tag
		return

	def set_level(self, lev):
		"""Set log level (debug, info, warn, error and critical)"""
		self.level = level_map.get(lev)
		return

	def debug(self, string):
		"""Print messages on stderr with header 'DEBUG'."""
		if self.level == 1:
			self.__print__('DEBUG', string)
		return

	def info(self, string):
		"""Print messages on stderr without header."""
		if self.level <= 2:
			self.__print__('', string)
		return

	def warn(self, string):
		"""Print messages on stderr with header 'warnning'."""
		if self.level <= 3:
			self.__print__('warnning', string)
		return

	def error(self, string):
		"""Print messages on stderr with header 'error'."""
		if self.level <= 4:
			self.__print__('error', string)
		return

	def fatal(self, string, code = 99):
		"""Print messages on stderr with header FATAL and exit.
		If argument 'code' is set, it used by exit().
		If argument 'code' is 0, just print and do not exit.
		"""
		self.__print__('FATAL', string)
		if code != 0:
			exit(code)


### process handling	------------------------------------------------------

def read_pidlock(pidfile):
	"""Read and return content of 'pidfile'."""
	f = open(pidfile, 'r')
	pid = f.read()
	f.close()
	return pid

def write_pidlock(pidfile):
	"""Write pid of current process to 'pidfile'."""
	f = open(pidfile, 'w')
	f.write("%d" % os.getpid())
	f.close()
	return True

def backgroud():
	"""Make current process to background process."""
	child_pid = os.fork()
	if child_pid != 0:
		exit(0)

import signal
def doublekill(pid):
	"""send SIGTERM and SIGKILL to specified process."""
	try:
		os.kill(pid, signal.SIGTERM)
		time.sleep(2)
		os.kill(pid, signal.SIGKILL)
	except OSError:
		return True
	return False

def test(args = None):
	"""method for self-test."""
	log = Log('test')
	log.debug('testing module "%s"... debug' % MODULE)
	log.info('testing module "%s"... info' % MODULE)
	log.warn('testing module "%s"... warn' % MODULE)
	log.error('testing module "%s"... error' % MODULE)
	log.fatal('testing module "%s"... fatal' % MODULE, code=0)
	log.set_level('debug')
	log.debug('testing module "%s"... debug' % MODULE)
	log.info('testing module "%s"... info' % MODULE)
	log.warn('testing module "%s"... warn' % MODULE)
	log.error('testing module "%s"... error' % MODULE)
	log.fatal('testing module "%s"... fatal' % MODULE, code=0)

	cf = Config('util.xml')
	print("util version: %s" % cf.get('util/version'))
	print("util loglevel: %s" % cf.get('util/loglevel'))
	cf.set('util/loglevel', 'fatal')
	print("util loglevel: %s" % cf.get('util/loglevel'))
	cf.save('test.xml')

	return

if __name__ == '__main__':
	test()

