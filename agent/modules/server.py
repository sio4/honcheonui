"""server information module for honcheonui.

It provides server information service for honcheonui agent.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""


### class system	------------------------------------------------------
import sys, os
import uuid
import time
from subprocess import *

import honcheonui as hcu

MODULE = 'hcu_server'
VERSION = '0.1.0'

class Server:
	"""Server Information Class."""
	server_id = None
	uuid = None
	hostname = None
	os = dict()	# static, uname and lsb informations
	st = dict()	# dynamic, uptime, monitoring and automation.
	op = dict()	# operation info, mode and level.

	def __init__(self, uuid_str, communicator, logger):
		"""Initialize without any argument."""
		self.c = communicator
		self.l = logger
		self.l.set_tag(MODULE)
		try:
			self.uuid = uuid.UUID(uuid_str)
		except (ValueError, TypeError):
			self.l.info('invalid uuid: %s' % uuid_str)
			self.uuid = uuid.uuid1()
			self.l.info('generate new uuid: %s' % str(self.uuid))
		self.__get_os_info__()
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
		response = None
		has_error = False
		while not response:
			data = {'name':self.hostname,'uuid':str(self.uuid)}
			#error_maker data = {'name':'test'}
			try:
				ret = self.c.json_post('/servers.json', data)
			except hcu.CommunicationError as e:
				has_error = True
				self.l.debug('network error! (%s)' % e.value)
				# XXX if timeout/countout, make error!
				time.sleep(1)
				self.c.connect()
				continue

			if has_error:
				self.l.verb(self.c.__stat_str__())
				self.l.verb(self.c.__error_stat_str__())

			## ok, communication succeeded.
			code,reason,body = ret
			if code == 201 or code == 301:
				self.l.debug('ok, registered. return %d' % code)
				response = body
			elif code == 422:
				## error, mainly duplicated uuid.
				raise hcu.ModuleError(1,'register failed.')
			else:
				raise hcu.ModuleError(9,'Unknown response.')

		self.l.debug(body)
		# set operational values from master. user-given values.
		for k in ('op_mode','op_level','id'):
			self.op[k] = body[k]

		self.l.info('server id on master is %d.' % self.op['id'])
		# put current os informations to master. automatic values.
		data = {'os_name':self.os['name'],
			'os_id':self.os['id'],
			'os_rel':self.os['rel'],
			'os_kernel':self.os['kernel'],
			'os_build':self.os['build'],
			'os_arch':self.os['arch']}
		self.l.debug('data to be updated: (%s)' % data)
		ret = self.c.json_put('/servers/%d.json' % self.op['id'], data)
		self.l.debug('return (%d:%s:%s)' % ret)

		return

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

def run(cf, comm, log):
	server = Server(cf.get('module/server/uuid'), comm, log)
	if str(server.uuid) != cf.get('module/server/uuid'):
		cf.set('module/server/uuid', str(server.uuid), True)
		log.info('uuid changed and saved. %s' % str(server.uuid))

	log.set_level('verb')
	try:
		server.register()
	except hcu.ModuleError as e:
		log.fatal('cannot register the server: (%s)' % str(e))
	except KeyboardInterrupt:
		log.fatal('interrupted before server registration. abort!')

	log.info('ok, server was registered and updated boot time status.')
	log.set_level('debug')
	#server.view()

	return
