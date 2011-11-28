###
#
#

### class system	------------------------------------------------------
import os
from subprocess import *

class Server:
	hostname = ''
	os_name = ''
	os_id = ''
	os_rel = ''
	os_kernel = ''
	os_build = ''
	os_arch = ''
	op_mode = ''
	op_level = ''
	op_uptime = ''

	def __init__(self):
		self.__get_os_info__()
		return

	def __get_os_info__(self):
		os_name, hostname, kernel, build, arch = os.uname()
		self.os_name = os_name
		self.hostname = hostname
		self.os_kernel = kernel
		self.os_build = build
		self.os_arch = arch

		p = Popen(['lsb_release', '-si'], stdout=PIPE)
		self.os_id = p.communicate()[0].strip()
		p = Popen(['lsb_release', '-sr'], stdout=PIPE)
		self.os_rel = p.communicate()[0].strip()

		f = open( "/proc/uptime" )
		contents = f.read().split()
		f.close()
		self.op_uptime = int(float(contents[0]) / (60*60*24))

		return

	def view(self):
		print "hostname: %s" % self.hostname
		print "os_name: %s" % self.os_name
		print "os_id: %s" % self.os_id
		print "os_rel: %s" % self.os_rel
		print "os_kernel: %s" % self.os_kernel
		print "os_build: %s" % self.os_build
		print "os_arch: %s" % self.os_arch
		print "op_mode: %s" % self.op_mode
		print "op_level: %s" % self.op_level
		print "op_uptime: %s" % self.op_uptime


#sys = Server()
#sys.view()
