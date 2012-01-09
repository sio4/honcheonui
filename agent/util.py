"""common utility library for config and log handling

It provides basic configuration handling in xml format and log handling.

Class 'Config' provides get/set/save functionality for configuration in
xml file.  configuration values can be accessed via get() method and
assigned via set() method.  both methods use xpath like convention for
configuration key.  updated configurations can be stored to xml file via
save() method.  for automatic save at assign, user can pass additional
parameter to set().

Class 'Log' currently provides simple print() like methods including
debug(), verb(), info(), warn(), error() and fatal(). it provides 'tag'
and 'level' for logs, so user can handle verboseness of logs, and logs
are distinct by tags.  'level' and 'tag' can be reset by set_level()
and set_tag() methods, so user can easily control the logs.

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

### class Timer	--------------------------------------------------------------
import time

class Timer:
	def __init__(self):
		"""initiate Timer and start timer automatically."""
		return self.start()

	def start(self):
		self._result = 0
		self._start = time.time()
		return

	def finish(self):
		return self.result()

	def result(self):
		self._result = time.time() - self._start
		return self._result

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
		nodelist[0].text = str(value)
		if save == True:
			self.save()
		return

	def get(self, key, default = None):
		"""Get configuration value on 'key'
		If there is more than one node with save path, first on is used.
		"""
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			printerr("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			printerr("oops! no value found for key!:%s"% key)
			return default
		return nodelist[0].text

	def subkeys(self, key):
		nodelist = self.doc.findall(key)
		keylist = list()
		for node in nodelist:
			keylist.append(node.tag)
		return keylist

	def save(self, filename = 'auto'):
		"""Save current configuration on xml file.
		If argument 'filename' is not given, write on current file.
		"""
		### FIXME save backup!
		if filename == 'auto':
			filename = self.filename
		if ElementTree.VERSION >= "1.3.0":	# for python 3.x
			self.doc.write(filename, 'utf-8', xml_declaration=True)
		else:
			self.doc.write(filename, 'utf-8')
		return


### class Log	--------------------------------------------------------------
from datetime import datetime
level_map = {'debug':1, 'verb':2, 'verbose':2, 'info':3,
	'warn':4, 'warnning':4, 'error':5, 'fatal':6 }

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

	def __print__(self, string, level = None):
		if level:
			fmt = '%s %s %s: (' + level + ') %s\n'
		else:
			fmt = '%s %s %s: %s\n'
		now = datetime.strftime(datetime.now(),'%b %d %H:%M:%S')
		sys.stderr.write(fmt % (now, 'me', self.tag, string))
		sys.stderr.flush()
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
		if self.level == level_map.get('debug'):
			self.__print__(string, 'DEBUG')
		return

	def verb(self, string):
		"""Print messages on stderr with header 'verb'."""
		if self.level <= level_map.get('verb'):
			self.__print__(string, 'verb')
		return

	def info(self, string):
		"""Print messages on stderr without header."""
		if self.level <= level_map.get('info'):
			self.__print__(string)
		return

	def warn(self, string):
		"""Print messages on stderr with header 'warnning'."""
		if self.level <= level_map.get('warn'):
			self.__print__(string, 'warnning')
		return

	def error(self, string):
		"""Print messages on stderr with header 'error'."""
		if self.level <= level_map.get('error'):
			self.__print__(string, 'error')
		return

	def fatal(self, string, code = 99):
		"""Print messages on stderr with header FATAL and exit.
		If argument 'code' is set, it used by exit().
		If argument 'code' is 0, just print and do not exit.
		"""
		self.__print__(string, 'FATAL')
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
	sk = cf.subkeys('module/*')
	for k in sk:
		print(' -- subkey %s' % k, cf.subkeys('module/%s/*' % k))
	print("util version: %s" % cf.get('util/version'))
	print("util loglevel: %s" % cf.get('util/loglevel'))
	cf.set('util/loglevel', 'fatal')
	print("util loglevel: %s" % cf.get('util/loglevel'))
	cf.save('test.xml')

	return

if __name__ == '__main__':
	test()

