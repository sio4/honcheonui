###
#
#	vim: set ts=4 sw=4:

import sys
import os

hcu_name = "honcheonui"
hcu_version = "0.1"
hcu_codename = "heartbreak hotel"


### common class, 'Config' for site-wide configuration parser.	--------------
import libxml2

class Config:
	master_host = None
	master_port = 80
	pid_file = '/var/run/honcheonui.pid'
	log_group = 'messages'
	log_path = '/logs'
	log_pipe = '/tmp/log.pipe'

	loglevel = 3

	proc_name = hcu_name
	proc_version = hcu_version
	proc_codename = hcu_codename
	pkg_sign = "%s/%s" % (hcu_name, hcu_version)
	proc_sign = "%s/%s" % (proc_name, proc_version)

	# now use xml config for server basis, but it will be site-overide mode.
	# we need autoconfig via network broadcast.
	def __init__(self, conf_file):
		if os.access(conf_file, os.R_OK) == False:
			error("cannot access config file. (%s)" % conf_file)
			return

		try:
			doc = libxml2.parseFile(conf_file)
		except libxml2.parserError:
			error("cannot parse configuration file.")
			return
		except:
			error("Unexpected error:",sys.exc_info()[0])
			raise

		# FIXME if no values set?
		self.master_host = doc.xpathEval('//config/master/host')[0].content
		self.master_port = int(doc.xpathEval('//config/master/port')[0].content)
		self.pid_file = doc.xpathEval('//config/runtime/pid_file')[0].content
		self.log_group = doc.xpathEval('//config/log/group')[0].content
		self.log_path = doc.xpathEval('//config/log/path')[0].content
		self.log_pipe = doc.xpathEval('//config/log/pipe')[0].content
		self.loglevel = doc.xpathEval('//config/runtime/loglevel')[0].content
		return
	def view(self):
		print 'self.pid_file: %s' % self.pid_file
		print 'self.loglevel: %s' % self.loglevel
		print 'self.master_host: %s' % self.master_host
		print 'self.master_port: %s' % self.master_port
		print 'self.log_group: %s' % self.log_group
		print 'self.log_path: %s' % self.log_path
		print 'self.log_pipe: %s' % self.log_pipe

	def __version__(self):
		self.proc_sign = "%s/%s" % (self.proc_name, self.proc_version)

	def set_procname(self, string):
		self.proc_name = string
		self.__version__()

	def set_procversion(self, string):
		self.proc_version = string
		self.__version__()

	def get_pkgsign(self):
		return self.pkg_sign

	def get_procsign(self):
		return self.proc_sign


### common class for server communication.	----------------------------------
import httplib

class Communication:
	conn = None
	sub_agent = "%s/%s" % (Config.proc_name, Config.proc_version)
	headers = {
			"Content-type":"application/json",
			"User-Agent":"%s/%s(%s) %s" %
			(hcu_name, hcu_version, hcu_codename, sub_agent)}
	def __init__(self, host, port):
		self.conn = httplib.HTTPConnection(host, port)
		return

	def json_post(self, path, data):
		self.conn.request("POST", path, data, self.headers)
		response = self.conn.getresponse()
		res = response.read()
		return response.status


