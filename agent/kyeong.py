#!/usr/bin/env python3
"""kyeong, honceonui agent for managed server.

written by Yonghwan SO <sio4@users.sf.net>

* puthon 3.2.2 compatable.
"""

import sys, os
import time

NAME	= 'kyeong'
VERSION	= '0.1.1'

import util
import honcheonui

###
### function definitions	----------------------------------------------
###

def get_options():
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
	return options

### signal handler and helper functions	--------------------------------------
def sighandler(signum, frame):
	log.warn("signal %d received." % signum)
	return

def saygoodbye():
	pidlocked = util.read_pidlock(cf.get('honcheonui/pid_file'))
	if os.getpid() == int(pidlocked):
		log.debug("same pid(%s). remove pidlock" % pidlocked)
		os.unlink(cf.get('honcheonui/pid_file'))
	log.info("bye...")
	return

### module handlers	------------------------------------------------------
def run_threaded_modules(path, blocked = False):
	modules = list()
	for m in cf.subkeys(path):
		log.verb("mod '%s' detected. trying to load..." % m)
		try:
			mod = __import__('modules.%s' % m, fromlist=["modules"])
			mclass = getattr(mod, m)
			t = mclass(cf, queues, message)
			t.start()
		except (ImportError,AttributeError) as e:
			log.error("cannot import module '%s': %s" % (m, str(e)))
		except:
			log.error('unknown exception.')
			raise
		else:
			modules.append(t)
			log.info("module '%s' registered. starting..." % m)
	if blocked:
		log.verb('waiting for blocked module finished...')
		wait_for_modules(modules)
		log.verb('ok, all modules are finished.')
	return modules

def wait_for_modules(modules):
	while len(modules) > 0:
		try:
			time.sleep(1.9)
			for t in modules:
				if not t.is_alive():
					log.verb('%s is gone.' % t.getName())
					modules.remove(t)
				else:
					log.debug('%s alive...' % t.getName())
					t.join(0.1)
		except KeyboardInterrupt as e:
			log.info('interrupted! stopping...')
			message['onair'] = False
	return

###
### start main routine	------------------------------------------------------
###
options = get_options()

log = util.Log('hcu-%s' % NAME)
log.info("initializing...")

try:
	cf = util.Config(options.config)
except util.configError as e:
	log.fatal('%s' % e)

# override some configuration (agent mode).
cf.set('honcheonui/name', 'honcheonui-%s' % NAME)
cf.set('honcheonui/version', VERSION)

log.set_level(cf.get('honcheonui/loglevel'))
log.info('%s configured properly...' % cf.get('honcheonui/name'))

# FIXME reachable test required!
if cf.get('master/host') == '':
	log.fatal("server not configured properly.", os.EX_CONFIG)

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
log.info("%s[%d] started..." % (NAME, os.getpid()))

# yes, about to do my job!
import signal, atexit
signal.signal(signal.SIGHUP, sighandler)
atexit.register(saygoodbye)


###
### start main job	------------------------------------------------------
###
comm = honcheonui.Communication(cf.get('master/host'), cf.get('master/port'))
# FIXME add connection checker here!
# now use xml config for server basis, but it will be site-overide mode.
# we need autoconfig via network broadcast.

###
### module detection and startup...	--------------------------------------
###
import queue
from collections import namedtuple
queues = namedtuple('queues', 'dq mq hq')
queues.dq = queue.Queue(-1)
queues.mq = dict()
queues.hq = dict()
message = {'onair':True, 'interval':2}

### invoke 'long-run' controller module.	------------------------------
controllers = run_threaded_modules('module/*[@type="controller"]')
handlers = run_threaded_modules('module/*[@type="handler"]')

### invoke modules for startup time in blocked mode...	----------------------
modules = run_threaded_modules('module/*[@type="startup"]', True)

### invoke 'long-run observer modules...	------------------------------
log.info('startup processes are done. jump into the fire!')
#modules = run_threaded_modules('module/*[@type="periodic"]')
log.info('now all modules are in running mode...')

### finally,
wait_for_modules(modules + handlers + controllers)
# where to check NO-MORE-QUEUE
log.info('all module thread are exit. shutdown myself.')

exit(0)
