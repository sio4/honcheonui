"""main classes and methods of honcheonui.

It provides main and common classes and functions to package.

Class Communication provides facility to communicate with master server.
It handles connection to master server and provides some HTTP request
functionalities including POST, PUT,...
For communication between managed server and master server, honcheonui
uses JSON formated payload (http://www.json.org), it mainly provides
JSON over POST (to insert, create, register,...) and JSON over PUT
(to update).

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os
import time

hcu_name = "honcheonui"
hcu_version = "0.1"
hcu_codename = "heartbreak hotel"

MODULE = 'honcheonui'
VERSION = '0.1.0'

def error(string):
	sys.stderr.write("%s-common: %s\n" % (hcu_name, string))
	return

### generic exception	------------------------------------------------------
class HoncheonuiError(Exception):
	"""Honcheonui Error"""
	def __init__(self, code, value):
		"""Initialize with error code and value."""
		self.code = code
		self.value = value

	def __str__(self):
		return repr(self.value)

class ModuleError(HoncheonuiError):
	"""Module Error"""

class CommunicationError(HoncheonuiError):
	"""Communication Error"""

### common class for master communication.	------------------------------
from http import client
import json
import socket

class Communication:
	"""Communication with master server."""
	conn = None
	agent = ''

	host = None
	port = None

	no_req_total = 0
	no_req_error = 0

	headers = {"Content-type":"application/json",
		"User-Agent":"%s/%s(%s)" % (hcu_name, hcu_version, hcu_codename)
		}
	def __init__(self, host, port, agent = None):
		"""Initialize with host, port and optional agent."""
		if agent != None:
			self.agent = ' %s' % agent
		self.host = host
		self.port = port
		self.connect()
		return

	def __statistics__(self):
		return (self.no_req_error, self.no_req_total,
				int(100*self.no_req_error/self.no_req_total))

	def __stat_str__(self):
		return '%d errors, %d requests. (%d%%)' % self.__statistics__()

	def connect(self):
		"""connection generator.
		it automatically called by initiator, but user can call it
		for regeneration of connection after connection related
		exception.
		"""
		self.conn = client.HTTPConnection(self.host, self.port)
		return

	def request(self, method, path, data=None, header=None):
		"""simple HTTP request on 'path', using 'method'."""
		self.no_req_total += 1
		try:
			self.conn.request(method, path, data, header)
		except (socket.error, client.CannotSendRequest) as e:
			self.no_req_error += 1
			raise CommunicationError(70, str(e))
		except:
			raise
		else:
			response = self.conn.getresponse()
			status = response.status
			reason = response.reason
			body = response.read().decode()

		return (status, reason, body)

	def json_post(self, path, data):
		"""POST dictionary 'data' to 'path' in JSON format,
		return JSON replay as dictionary type. (with status and reason.)
		"""
		data = json.dumps(data)
		s,r,b = self.request("POST", path, data, self.headers)
		return (s,r,json.loads(b))

	def json_put(self, path, data):
		"""PUT dictionary 'data' to 'path' in JSON format,
		return status and reason, and body it self.
		"""
		### XXX check response BODY for future use.
		data = json.dumps(data)
		return self.request("PUT", path, data, self.headers)


