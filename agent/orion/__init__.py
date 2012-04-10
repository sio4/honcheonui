"""
"""

__package_name__	= 'orion'
__package_version__	= '0.1.0'

import os
from xml.etree import ElementTree

### default logger	----------------------------------------------------------
class Logger:
	def __init__(self):
		return

	def error(self, string):
		return self.debug(string)

	def warn(self, string):
		return self.debug(string)

	def debug(self, string):
		import sys
		return sys.stderr.write("%s: %s\n" %(__package_name__, string))


### configuration holder	--------------------------------------------------
class orionError(Exception):
	"""Configuration Error"""
	def __init__(self, code, value):
		self.errno = code
		self.strerror = value

	def __str__(self):
		return repr(self.strerror)

class configError(orionError):
	def __str__(self):
		return repr('configError:%s' % self.strerror)


class Config:
	def __init__(self, element=None, filename=None, text=None, logger=None):
		self.filename = filename
		if logger:
			self.logger = logger
		else:
			self.logger = Logger()

		if text:
			try:
				self.doc = ElementTree.fromstring(text)
			except ElementTree.ParseError as e:
				raise configError(2, 'cannot parse config. (%s)' % text)
		elif self.filename:
			if os.access(filename, os.R_OK) == False:
				raise configError(3, 'cannot access file. (%s)' % filename)

			try:
				self.doc = ElementTree.ElementTree(file=filename)
			except ElementTree.ParseError as e:
				raise configError(4, 'cannot parse file. (%s)' % filename)
		elif element is not None:
			self.doc = ElementTree.ElementTree(element=element)
		else:
			raise configError(1, 'initializing failed. no file and text.')

		return

	def set(self, key, value, save = False):
		"""Set configuration value on 'key'
		If argument 'save' is True, it call method save() too.
		If there is more than one node with save path, first on is used.
		"""
		nodelist = self.doc.findall(key)
		if len(nodelist) > 1:
			self.logger.warn("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			self.logger.warn("oops! do you want add? not implemented!")
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
			self.logger.warn("eep! duplicated key found. using first!")
		elif len(nodelist) < 1:
			self.logger.warn("oops! no value found for key!:%s" % key)
			return default
		return nodelist[0].text

	def get_branch(self, key):
		return Config(element = self.doc.find(key), logger = self.logger)

	def subkeys(self, key):
		keylist = list()
		for node in self.doc.findall(key):
			keylist.append(node.tag)
		return keylist

	def subnames(self, key):
		namelist = list()
		for node in self.doc.findall(key):
			namelist.append(node.attrib['name'])
		return namelist

	def save(self, filename = None):
		"""Save current configuration on xml file.
		If argument 'filename' is not given, write on current file.
		"""
		### FIXME save backup!
		if filename:
			self.filename = filename

		if self.filename:
			if ElementTree.VERSION >= "1.3.0":	# for python 3.x
				self.doc.write(filename, 'utf-8', xml_declaration=True)
			else:
				self.doc.write(filename, 'utf-8')
		else:
			self.logger.warn('filename is not defined. abort!')

		return



# vim:set ts=4 sw=4:
