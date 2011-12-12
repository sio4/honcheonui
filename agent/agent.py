#!/usr/bin/env python3
#
#



import sys, os
import time

import util
import honcheonui

NAME = 'agent'
VERSION = '0.1.0'

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
except util.configError as e:
	log.fatal('%s' % e)

# override some configuration (agent mode).
cf.set('honcheonui/name', 'honcheonui-kyeong')
cf.set('honcheonui/version', '0.1')

log.set_level(cf.get('honcheonui/loglevel'))
log.info('%s configured properly...' % cf.get('honcheonui/name'))

# XXX reachable test required!
if cf.get('master/host') == '':
	log.fatal("server not configured properly.", os.EX_CONFIG)


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
	return


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
comm = honcheonui.Communication(cf.get('master/host'), cf.get('master/port'))
# FIXME add connection checker here!
# now use xml config for server basis, but it will be site-overide mode.
# we need autoconfig via network broadcast.

###
### module detection and serve...	--------------------------------------
###

### modules for startup time...	----------------------------------------------
for mname in cf.subkeys('module/*[@type="startup"]'):
	log.verb("startup module '%s' detected. trying to load..." % mname)
	try:
		mod = __import__('modules.%s' % mname, fromlist=["modules"])
	except ImportError as e:
		log.error("cannot import module '%s'. ignore." % mname)
	else:
		log.info("ok, loaded. starting module '%s'..." % mname)
		mod.run(cf, comm, log)

### modules for periodic run...	----------------------------------------------
from threading import Thread

message = {'stop':False}
modules = list()
for mname in cf.subkeys('module/*[@type="periodic"]'):
	log.verb("configration for '%s' detected. trying to load..." % mname)
	try:
		mod = __import__('modules.%s' % mname, fromlist=["modules"])
	except ImportError as e:
		log.error("cannot import module '%s'. ignore." % mname)
	else:
		modules.append({'name':mname, 'module':mod})
		log.verb("module '%s' registered." % mname)

for mod in modules:
	log.info("starting module '%s'..." % mod['name'])
	try:
		mclass = getattr(mod['module'], mod['name'])
		mod['thread'] = mclass(cf, comm, log, message)
		mod['thread'].start()
	except AttributeError as e:
		log.error("invalid module '%s'. %s" % (mod['name'], str(e)))
	except:
		log.error('unknown exception: %s' % str(e))
		rais

log.info('now all modules are in running mode...')
while len(modules):
	for i in range(len(modules)):
		t = modules[i]['thread']
		if not t.is_alive():
			log.verb('%s already exit.' % t.getName())
			modules.pop(i)
			break
		log.verb('%s alive...' % t.getName())
		### use signal?
		try:
			t.join(2)
		except KeyboardInterrupt as e:
			log.info('interrupted! %s' % str(e))
			message['stop'] = True


log.info('all module thread are exit. shutdown myself.')

exit(0)
