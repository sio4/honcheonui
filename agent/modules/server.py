"""server information module for honcheonui.

It provides server information service for honcheonui agent.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os
import time

from subprocess import *
import uuid

MODULE	= 'server'
VERSION	= '0.1.0'
MTYPE	= 'module'

import util
from modules import kModule

class server(kModule):
	"""Server Information Class."""
	hostname = None
	os = dict()	# static, uname and lsb informations
	st = dict()	# dynamic, uptime, monitoring and automation.
	op = dict()	# operation info, mode and level.

	def __prep__(self):
		try:
			uuid_str = self.c.get('module/server/uuid', 'unset')
			self.uuid = uuid.UUID(uuid_str)
		except (ValueError, TypeError):
			self.l.info('invalid uuid: %s' % uuid_str)
			self.uuid = uuid.uuid1()
			self.c.set('module/server/uuid', str(self.uuid), True)
			self.l.info('generate new uuid: %s' % str(self.uuid))
		self.__get_os_info__()
		return

	def set_module_info(self):
		self.mod = MODULE
		self.ver = VERSION
		self.typ = MTYPE
		return

	def __get_os_info__(self):
		os_name, hostname, kernel, build, arch = os.uname()
		self.os['name'] = os_name
		self.hostname = hostname
		self.os['kernel'] = kernel
		self.os['build'] = build
		self.os['arch'] = arch

		# use lsb interface for compatibility.
		# strip() for removing '\n', decode() for binary2str.
		p = Popen(['lsb_release', '-si'], stdout=PIPE)
		self.os['id'] = p.communicate()[0].strip().decode()
		p = Popen(['lsb_release', '-sr'], stdout=PIPE)
		self.os['rel'] = p.communicate()[0].strip().decode()

		# update initial dynamic status.
		self.update_st()
		return

	def register(self):
		registered = False
		has_error = False
		while not registered and self.m['onair']:
			data = {'name':self.hostname,'uuid':str(self.uuid)}
			#error_maker data = {'name':'test'}
			self.l.verb('request for register...')
			res = self.queue_request(data, self.basepath)
			if res == False:
				self.l.verb('some error. sleep 1sec.')
				time.sleep(1)	# CHKME: infinite seq mismatch.
				continue

			### ok, communication succeeded.
			### FIXME need more beautiful return value handling...
			code = res.get('code')
			if code == 201 or code == 301:
				self.l.debug('ok, registered. return %d' % code)
				response = res.get('data')
				registered = True
			elif code == 422:
				## error, mainly duplicated uuid.
				raise kModule.Exception(9,'register failed.')
			else:
				raise kModule.Exception(8,'Unknown response.')

		if not self.m['onair']:
			return registered
		# set operational values from master. user-given values.
		for k in ('op_mode','op_level','id'):
			self.op[k] = response.get(k,0)

		self.l.info('server id on master is %d.' % self.op['id'])
		self.c.set('module/server/id', self.op['id'])
		# put current os informations to master. automatic values.
		data = {'os_name':self.os['name'],
			'os_id':self.os['id'],
			'os_rel':self.os['rel'],
			'os_kernel':self.os['kernel'],
			'os_build':self.os['build'],
			'os_arch':self.os['arch']}
		self.l.debug('data to be updated: (%s)' % data)
		res = self.queue_request(data, '%s/%d' % (self.basepath,
			self.op['id']), 'update')
		self.l.verb('update request returns: c%d,s%d' % (
			res['code'], res['sequence']))

		return True

	def update_st(self):
		"""update current dynamic status informations."""
		f = open( "/proc/uptime" )
		contents = f.read().split()
		f.close()
		self.st['uptime'] = int(float(contents[0]) / (60*60*24))

		# FIXME currently not implemented.
		# where... in here? or process?
		self.st['monitoring'] = True
		self.st['automation'] = True
		return


	### debuging purpose...
	def view(self):
		"""for test, view all values of this class."""
		print("uuid: %s" % self.uuid)
		print("hostname: %s" % self.hostname)
		for k in self.os.keys():
			print("os_%s: %s" % (k, self.os[k]))
		for k in self.st.keys():
			print("st_%s: %s" % (k, self.st[k]))
		for k in self.op.keys():
			print("op_%s: %s" % (k, self.op[k]))

	def run(self):
		try:
			registered = self.register()
		except kModule.Exception as e:
			self.abort('cannot register the server: %s' % str(e))
		except KeyboardInterrupt:
			self.abort('interrupted before server registration!')
		except:
			self.abort('unknown exception!')

		if registered:
			self.l.info('ok, server was registered and updated.')
			self.view()

		return
