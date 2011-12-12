#!/usr/bin/env python3
"""agent for honcheonui.
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
def run_blocked_modules(path):
	for m in cf.subkeys(path):
		log.verb("config '%s' detected. trying to load..." % m)
		try:
			mod = __import__('modules.%s' % m, fromlist=["modules"])
		except ImportError as e:
			log.error("cannot import module '%s'. ignore." % m)
		else:
			log.info("ok, loaded. starting module '%s'..." % m)
			mod.run(cf, comm, log)
	return

def run_threaded_modules(path):
	modules = list()
	for m in cf.subkeys(path):
		log.verb("config '%s' detected. trying to load..." % m)
		try:
			mod = __import__('modules.%s' % m, fromlist=["modules"])
			mclass = getattr(mod, m)
			t = mclass(cf, comm, log, message)
			t.start()
		except (ImportError,AttributeError) as e:
			log.error("cannot import module '%s': %s" % (m, str(e)))
		except:
			log.error('unknown exception.')
			raise
		else:
			modules.append(t)
			log.info("module '%s' registered. starting..." % m)
	return modules

###
### start main routine	------------------------------------------------------
###
options = get_options()

log = util.Log('honcheonui-kyeong')
log.info("initializing...")
try:
	cf = util.Config(options.config)
except util.configError as e:
	log.fatal('%s' % e)

# override some configuration (agent mode).
cf.set('honcheonui/name', 'honcheonui-%s' % NAME)
cf.set('honcheonui/version', '0.1')

log.set_level(cf.get('honcheonui/loglevel'))
log.info('%s configured properly...' % cf.get('honcheonui/name'))

# XXX reachable test required!
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
log.info("%s (%d) started..." % (NAME, os.getpid()))

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

### module detection and serve...	--------------------------------------
### modules for startup time...	----------------------------------------------
run_blocked_modules('module/*[@type="startup"]')

### modules for periodic run...	----------------------------------------------
message = {'stop':False, 'interval':5}
modules = run_threaded_modules('module/*[@type="periodic"]')
log.info('now all modules are in running mode...')


import threading
while threading.active_count() > 1:
	try:
		for t in modules:
			if not t.is_alive():
				log.verb('%s already exit.' % t.getName())
			else:
				log.debug('%s alive...' % t.getName())
				t.join(2)
	except KeyboardInterrupt as e:
		log.info('interrupted! stopping...')
		message['stop'] = True

log.info('all module thread are exit. shutdown myself.')

exit(0)
