#!/usr/bin/env python

import sys
import os
import time

import honcheonui
import util
import hcu_logger

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


### basic configuration.	----------------------------------------------
cf = honcheonui.Config(options.config)
cf.set_procname("honcheonui-agent")
cf.set_procversion("0.1")

log = util.Log(cf.proc_name, cf.loglevel)
log.info("initializing...")

if cf.master_host == None:
	log.fatal("server not configured properly.", os.EX_CONFIG)

comm = honcheonui.Communication(cf.master_host, cf.master_port)
### FIXME add connection checker here!


### signal handler and helper functions	--------------------------------------
import signal
def sighandler(signum, frame):
	log.warn("signal %d received." % signum)
	return

signal.signal(signal.SIGHUP, sighandler)

import atexit
def saygoodbye():
	pidlocked = util.read_pidlock(cf.pid_file)
	if os.getpid() == int(pidlocked):
		log.debug("same pid(%s). remove pidlock" % pidlocked)
		os.unlink(cf.pid_file)
	log.info("bye...")
	exit(0)


### go background!	------------------------------------------------------
if options.debug != True:
	util.backgroud()

if os.path.exists(cf.pid_file):
	pid = util.read_pidlock(cf.pid_file)
	log.info("another agent is running maybe. check pid %s." % pid)
	if options.force == True:
		log.info("execution forced. kill other and run!")
		if util.doublekill(int(pid)):
			log.debug("ok, double kill return exception.")
			log.debug("- %s maybe killed." % pid)
	else:
		log.fatal("execution aborted. use --force for ignore it.")

util.write_pidlock(cf.pid_file)
log.info("%s (%d) started on %s..." % \
		(cf.get_procsign(), os.getpid(), os.uname()[1]))

# yes, about to do my job!
atexit.register(saygoodbye)


### log loop			----------------------------------------------

# FIXME make FIFO automatically. os.mkfifo(cf.log_pipe)
if os.access(cf.log_pipe, os.R_OK) == False:
	log.fatal("cannot access FIFO(%s)." % cf.log_pipe, os.EX_CONFIG)

logger_message = hcu_logger.Logger("messages", cf.log_pipe)
logger_message.loop()


