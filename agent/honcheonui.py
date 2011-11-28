###
#
#	vim: set ts=4 sw=4:

import sys
import os

hcu_name = "honcheonui"
hcu_version = "0.1"
hcu_codename = "heartbreak hotel"

def error(string):
	sys.stderr.write("%s-common: %s\n" % (hcu_name, string))
	return


### common class for server communication.	----------------------------------
import httplib

class Communication:
	conn = None
	agent = ''
	headers = {
			"Content-type":"application/json",
			"User-Agent":"%s/%s(%s)" % (hcu_name, hcu_version, hcu_codename)
			}
	def __init__(self, host, port, agent = None):
		if agent != None:
			self.agent = ' %s' % agent
		self.conn = httplib.HTTPConnection(host, port)
		return

	def json_post(self, path, data):
		self.conn.request("POST", path, data, self.headers)
		response = self.conn.getresponse()
		res = response.read()
		return response.status


