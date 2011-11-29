#!/usr/bin/env python

import sys
import os
import time

import honcheonui
import util
import hcu_server
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
log = util.Log('honcheonui-kyeong')
log.info("initializing...")
try:
	cf = util.Config(options.config)
except util.configError, e:
	log.fatal('%s' % e.message)

# override some configuration (agent mode).
cf.set('honcheonui/name', 'honcheonui-kyeong')
cf.set('honcheonui/version', '0.1')

log.set_level(cf.get('honcheonui/loglevel'))
log.info('%s configured properly...' % cf.get('honcheonui/name'))

if cf.get('master/host') == '':
	log.fatal("server not configured properly.", os.EX_CONFIG)

comm = honcheonui.Communication(cf.get('master/host'), cf.get('master/port'))
# FIXME add connection checker here!
# now use xml config for server basis, but it will be site-overide mode.
# we need autoconfig via network broadcast.


### signal handler and helper functions	--------------------------------------
import signal
def sighandler(signum, frame):
	log.warn("signal %d received." % signum)
	return

signal.signal(signal.SIGHUP, sighandler)

import atexit
def saygoodbye():
	pidlocked = util.read_pidlock(cf.get('honcheonui/pid_file'))
	if os.getpid() == int(pidlocked):
		log.debug("same pid(%s). remove pidlock" % pidlocked)
		os.unlink(cf.get('honcheonui/pid_file'))
	log.info("bye...")
	exit(0)


### go background!	------------------------------------------------------
if options.debug != True:
	util.backgroud()

if os.path.exists(cf.get('honcheonui/pid_file')):
	pid = util.read_pidlock(cf.get('honcheonui/pid_file'))
	log.info("another agent is running maybe. check pid %s." % pid)
	if options.force == True:
		log.info("execution forced. kill other and run!")
		if util.doublekill(int(pid)):
			log.debug("ok, double kill return exception.")
			log.debug("- %s maybe killed." % pid)
	else:
		log.fatal("execution aborted. use --force for ignore it.")

util.write_pidlock(cf.get('honcheonui/pid_file'))
log.info("%s (%d) started on %s..." % \
		(cf.get('honcheonui/name'), os.getpid(), os.uname()[1]))

# yes, about to do my job!
atexit.register(saygoodbye)


###
### start main job	------------------------------------------------------
###
sys = hcu_server.Server()
sys.view()

exit()


### log loop			----------------------------------------------

# FIXME make FIFO automatically. os.mkfifo(cf.log_pipe)
if os.access(cf.get('mod_log/pipe'), os.R_OK) == False:
	log.fatal("cannot access FIFO(%s)." % cf.get('mod_log/pipe'), os.EX_CONFIG)

logger_message = hcu_logger.Logger("messages", cf.get('mod_log/pipe'))
logger_message.loop()


