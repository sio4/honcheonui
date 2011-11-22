#!/usr/bin/env python

import sys
import os
import time

import honcheonui

### command line configurations	----------------------------------------------
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-c", "--conf", dest="config",
		default="/etc/opt/honcheonui/honcheonui.xml",
		help="configuration file", metavar="FILE")
parser.add_option("-d", "--debug", dest="debug",
		action="store_true",
		help="running in foreground")
parser.add_option("-f", "--force", dest="force",
		action="store_true",
		help="kill existing agent and run new one.")
(options, args) = parser.parse_args()


### signal handler and helper functions	--------------------------------------
import signal
def sighandler(signum, frame):
	honcheonui.warn("signal %d received." % signum)
	raise KeyboardInterrupt

signal.signal(signal.SIGINT, sighandler)

import atexit
def saygoodbye():
	pidlocked = honcheonui.read_pidlock(cf.pid_file)
	if os.getpid() == int(pidlocked):
		honcheonui.debug("same pid(%s). remove pidlock" % pidlocked)
		os.unlink(cf.pid_file)
	honcheonui.info("bye...")
	exit(0)


### basic configuration.	----------------------------------------------
honcheonui.info("initializing...")
cf = honcheonui.Config(options.config)
cf.set_procname("honcheonui-agent")
cf.set_procversion("0.1")
if cf.master_host == None:
	honcheonui.abort(os.EX_CONFIG, "server not configured properly.")

comm = honcheonui.Communication(cf.master_host, cf.master_port)
### FIXME add connection checker here!


### go background!	------------------------------------------------------
if options.debug != True:
	honcheonui.backgroud()

if os.path.exists(cf.pid_file):
	pid = honcheonui.read_pidlock(cf.pid_file)
	honcheonui.warn("another agent is running maybe. check pid %s." % pid)
	if options.force == True:
		honcheonui.info("execution forced. run anyway!")
		try:
			os.kill(int(pid), signal.SIGINT)
			time.sleep(2)
			os.kill(int(pid), signal.SIGKILL)
		except OSError:
			honcheonui.debug("ok, double kill return exception.")
			honcheonui.debug("- %s maybe killed." % pid)
	else:
		honcheonui.abort(1, "blocked. use --force for ignore.")

honcheonui.write_pidlock(cf.pid_file)
honcheonui.info("%s (%d) started on %s..." % (
	cf.get_procsign(), os.getpid(), os.uname()[1]))

# yes, about to do my job!
atexit.register(saygoodbye)


### log loop			----------------------------------------------

# FIXME make FIFO automatically. os.mkfifo(cf.log_pipe)
if os.access(cf.log_pipe, os.R_OK) == False:
	honcheonui.abort(os.EX_CONFIG, "cannot access FIFO(%s)." % cf.log_pipe)

# FIXME we need timing loop and bulk insertion.
c = 0
f = open(cf.log_pipe)
for line in f:
	data_json = honcheonui.syslog2json(group,line)
	print data_json
	comm.json_post(cf.log_path, data_json)


print cf.proc_name
print cf.proc_version
print cf.proc_codename
