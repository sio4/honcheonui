"""system stat information module for honcheonui.

It provides status/statistics information service for honcheonui agent.

written by Yonghwan SO <sio4@users.sf.net>

* python 3.2.2 compatable.
"""

import sys, os
import time

import psutil

MODULE	= 'stat'
VERSION = '0.1.0'
MTYPE	= 'module'

from modules import kModule

### class system	------------------------------------------------------
#from collections import namedtuple
class Value:
	def __init__(self, value, tm):
		self.maxi = 0
		self.last = value
		self.base = value
		self.last_tm = tm
		self.base_tm = tm
		return

	def update(self, value, tm, reset = False):
		# to prevent initial baseline become 0.
		if self.base == 0:
			reset = True

		curr = (value - self.last) / (tm - self.last_tm)
		avg = (value - self.base) / (tm - self.base_tm)
		self.last = value
		self.last_tm = tm
		if self.maxi < curr:
			self.maxi = curr
		# caution! self.maxi will be reset to 0 before sent.
		maxi = self.maxi
		# reset baseline for maximum, average calcuration.
		if reset:
			self.maxi = 0
			self.base = value
			self.base_tm = tm

		return maxi, avg, curr

class Cpu:
	def __init__(self):
		# prepare values with initail 0.
		# so first update will calcurate uptime average like vmstat.
		self.u = Value(0, 0)
		self.s = Value(0, 0)
		self.w = Value(0, 0)
		self.i = Value(0, 0)
		return

	def stat(self, reset = False):
		st = psutil.cpu_times()
		time = 0
		for k in iter(st):
			time += k
		# checked with vmstat result.
		# i need more study on /proc/stat and meaning of values.
		(um,ua,uc) = self.u.update(st.user + st.nice, time, reset)
		(sm,sa,sc) = self.s.update(st.system + st.softirq, time, reset)
		(wm,wa,wc) = self.w.update(st.iowait, time, reset)
		(im,ia,ic) = self.i.update(st.idle, time, reset)
		return ((um,sm,wm,im), (ua,sa,wa,ia), (uc,sc,wc,ic))


class Mem:
	"""memory status in kB."""
	def __init__(self):
		return

	def stat(self):
		ds = dict()
		ds['pt'] = int(psutil.phymem_usage().total / 1024)
		ds['pf'] = int(psutil.phymem_usage().free / 1024)
		ds['pu'] = int(psutil.phymem_usage().used / 1024)
		ds['pb'] = int(psutil.phymem_buffers() / 1024)
		ds['pc'] = int(psutil.cached_phymem() / 1024)
		ds['st'] = int(psutil.virtmem_usage().total / 1024)
		ds['su'] = int(psutil.virtmem_usage().used / 1024)
		return ds

class Process:
	def __init__(self):
		return

	def show(self):
		return

### 'stat', main class of this module.	--------------------------------------
class stat(kModule):
	def set_module_info(self):
		self.mod = MODULE
		self.ver = VERSION
		self.typ = MTYPE
		return

	def run(self):
		cpu = Cpu()
		mem = Mem()
		chk_int = int(self.c.get('module/stat/check_interval', 15))
		rpt_int = int(self.c.get('module/stat/report_interval', 300))
		self.l.verb('check every %d sec and report every %d.' % (
			chk_int, rpt_int))

		while self.m['onair']:
			if (int(time.time()/chk_int) % (rpt_int/chk_int)) == 0:
				reset = True
			else:
				reset = False

			cm,ca,cc = cpu.stat(reset)
			m = mem.stat()
			"""
			self.l.debug('m %3.2f %3.2f %3.2f %3.2f' % cm)
			self.l.debug('a %3.2f %3.2f %3.2f %3.2f' % ca)
			self.l.debug('c %3.2f %3.2f %3.2f %3.2f' % cc)
			self.l.debug('M %d %d %d %d %d %d %d' % (
				m['pt'], m['pf'], m['pu'], m['pb'], m['pc'],
				m['st'], m['su']))
			"""
			if reset:
				data = {'cpu_used_max':round(cm[0]*100),
					'cpu_used_avg':round(ca[0]*100),
					'cpu_sys_max':round(cm[1]*100),
					'cpu_sys_avg':round(ca[1]*100),
					'cpu_wait_max':round(cm[2]*100),
					'cpu_wait_avg':round(ca[2]*100),
					'cpu_idle_max':round(cm[3]*100),
					'cpu_idle_avg':round(ca[3]*100),
					'mem_used':m['pu'],
					'mem_buffer':m['pb'],
					'mem_cache':m['pc'],
					'swp_used':m['su'],
					'task_total':0,
					'task_running':0,
					'task_blocked':0,
					'task_zombie':0,
					'users':0}
				self.l.debug('cpu max u:%d s:%d w:%d i:%d' % (
					data['cpu_used_max'],
					data['cpu_sys_max'],
					data['cpu_wait_max'],
					data['cpu_idle_max'] ))
				self.l.debug('cpu avg u:%d s:%d w:%d i:%d' % (
					data['cpu_used_avg'],
					data['cpu_sys_avg'],
					data['cpu_wait_avg'],
					data['cpu_idle_avg'] ))
				self.l.debug('mem u:%d b:%d c:%d s:%d' % (
					data['mem_used'], data['mem_buffer'],
					data['mem_cache'], data['swp_used']))
				self.l.debug('reset --------------------------')
				### XXX report function here!

			# simply, full sleep without timing handling.
			# is there some delay on above logic? CHKME!
			time.sleep(chk_int)

		self.l.info('%s finished. bye...' % MODULE)
		return

"""
chk interval	check points	within 500p
15sec		 5760p		2hr
1min		 1440p		8hr
5min		  288p		40hr
10min		  144p		3.5day
"""

### selftest	--------------------------------------------------------------

# stat['proc_total'] = 0
# stat['proc_running'] = 0
# stat['proc_blocked'] = 0
# stat['proc_zombie'] = 0
# stat['users'] = 0

# netstat = psutil.network_io_counters(True)
# iostat = psutil.disk_io_counters(True)

#	for dk in sorted(iostat.keys()):
#		print('%s: %20d bytes read, %20d bytes write' % (dk,
#			iostat[dk].read_bytes, iostat[dk].write_bytes))

#	print('---')
#	netstat_lo = netstat.pop('lo')
#	print('%-10s: %20d bytes sent, %20d bytes recv' % ('lo',
#		netstat_lo.bytes_sent, netstat_lo.bytes_recv))
#	for nk in sorted(netstat.keys()):
#		print('%-10s: %20d bytes sent, %20d bytes recv' % (nk,
#			netstat[nk].bytes_sent, netstat[nk].bytes_recv))


