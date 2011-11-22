#!/usr/bin/env python
#
# vim: set ts=4 sw=4:

import sys
import os

hcu_name = "honcheonui"
hcu_version = "0.1"
hcu_codename = "heartbreak hotel"

# XXX checkit! where is the place of global but library valiable?
# one more Class for logger?
log_level = 1 # 1:verbose 2:info 3:warnning 4:error 5:critical


### simple helper methods.		----------------------------------------------

import re
import json
from datetime import datetime

def debug(string):
	if log_level == 1:
		sys.stderr.write("DEBUG: %s\n" % (string))
	return

def info(string):
	if log_level <= 2:
		sys.stderr.write("%s: %s\n" % (hcu_name, string))
	return

def warn(string):
	if log_level <= 3:
		sys.stderr.write("warn: %s\n" % string)
	return

def error(string):
	if log_level <= 4:
		sys.stderr.write("error: %s ignore.\n" % string)
	return

def abort(code, string):
	sys.stderr.write("fatal: %s abort!\n" % string)
	exit(code)


log_parser = re.compile("^(?P<datetime>[a-zA-Z]{3}\s+\d\d?\s\d\d\:\d\d:\d\d)(?:\s)?\s(?P<host>[a-zA-Z0-9_-]+)\s(?P<process>[a-zA-Z0-9\/_-]+)(\[(?P<pid>\d+)\])?:\s(?P<message>.+)$")

def syslog2json(group, string):
	m = log_parser.match(string)
	d = datetime.strptime(m.group('datetime'), "%b %d %H:%M:%S")
	# oops! it will generates critical value problem! chk it later!
	# for example, parsing log of YYYY-12-31 23:59:ss
	d = d.replace(datetime.now().year)
	if m.group('pid') == None:
		pid = 0
	else:
		pid = m.group('pid')

	data = {'group':group,
			'logdate':d.strftime("%Y-%m-%d %H:%M:%S"),
			'server_id':m.group('host'),
			'process':m.group('process'),
			'pid':pid,
			'message':m.group('message')}
	return json.dumps(data)


import os
def backgroud():
	info("about to be the daemon...")
	child_pid = os.fork()
	if child_pid == 0:
		info("running in background mode...(pid:%d)" % os.getpid())
		### be the daemon!
	else:
		exit(0)


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


### common class, 'Config' for site-wide configuration parser.	--------------
#
#
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
		loglevel = doc.xpathEval('//config/runtime/loglevel')[0].content
		if loglevel == "verbose":
			self.loglevel = 1
		elif loglevel == "info":
			self.loglevel = 2
		elif loglevel == "warn":
			self.loglevel = 3
		elif loglevel == "error":
			self.loglevel = 4
		elif loglevel == "critical":
			self.loglevel = 5
		return

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
#
#
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


