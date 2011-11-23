###
#
#

import sys
import re
import json
from datetime import datetime

class Log:
	group = ''
	logdate = ''
	host = ''
	process = ''
	pid = ''
	message = ''

	def __init__(self, group, logstr):
		log_parser = re.compile("^(?P<datetime>[a-zA-Z]{3}\s+\d\d?\s\d\d\:\d\d:\d\d)(?:\s)?\s(?P<host>[a-zA-Z0-9_-]+)\s(?P<process>[a-zA-Z0-9\/_-]+)(\[(?P<pid>\d+)\])?:\s(?P<message>.+)$")
		m = log_parser.match(logstr)
		# error checker.
		d = datetime.strptime(m.group('datetime'), "%b %d %H:%M:%S")
		# oops! it will generates critical value problem! chk it later!
		# for example, parsing log of YYYY-12-31 23:59:ss
		d = d.replace(datetime.now().year)
		if m.group('pid') == None:
			self.pid = 0
		else:
			self.pid = m.group('pid')

		self.group = group
		self.logdate = d.strftime("%Y-%m-%d %H:%M:%S")
		self.host = m.group('host')
		self.process = m.group('process')
		self.message = m.group('message')
		return

	def to_json(self):
		data = {'group':self.group,
			'logdate':self.logdate,
			'server_id':self.host,
			'process':self.process,
			'pid':self.pid,
			'message':self.message}
		return json.dumps(data)


class Logger:
	conf_group = ''
	conf_fifo = ''

	def __init__(self, group, fifo):
		self.conf_group = group
		self.conf_fifo = fifo
		return

	def log_filter(self, log):
		return

	def loop(self):
		while True:
			f = open(self.conf_fifo)
			try:
				for line in f:
					log = Log(self.conf_group, line)
					data_json = log.to_json()
					print data_json
					#comm.json_post(cf.log_path, data_json)
				sys.stderr.write('logger: looping...\n')
			except IOError:
				sys.stderr.write('I/O Exception.\n')

