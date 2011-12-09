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
modules = list()
for mname in cf.subkeys('module/*[@type="periodic"]'):
	log.verb("configration for '%s' detected. trying to load..." % mname)
	try:
		mod = __import__('modules.%s' % mname, fromlist=["modules"])
	except ImportError as e:
		log.error("cannot import module '%s'. ignore." % mname)
	else:
		modules.append({'name':mname, 'module':mod, 'thread':None})
		log.verb("module '%s' registered." % mname)

for mod in modules:
	log.info("starting module '%s'..." % mod['name'])
	try:
		# XXX check run method's argument. it makes TypeError.
		mod['thread'] = Thread(target=mod['module'].run,
				args=(cf, comm, log))
		mod['thread'].start()
	except AttributeError as e:
		log.error("invalid module '%s'. %s" % (mod['name'], str(e)))

log.info('now all modules are in running mode...')
for mod in modules:
	try:
		mod['thread'].join()
	except:
		print('aaa')

log.info('all module thread are exit. shutdown myself.')

exit(0)

### server registeration	----------------------------------------------
server = hcu_server.Server(cf.get('server/uuid'), comm, log)
if str(server.uuid) != cf.get('server/uuid'):
	cf.set('server/uuid', str(server.uuid), True)
	log.info('uuid changed and saved. %s' % cf.get('server/uuid'))

log.set_level('info')
try:
	server.register()
except honcheonui.ModuleError as e:
	log.fatal('cannot register the server: (%d:%s)' % (e.code, e.value))
except KeyboardInterrupt:
	log.fatal('interrupted before server registration. abort!')

log.info('ok, server was registered and updated boot time status.')
log.set_level('debug')
#server.view()

### register periodic job. settimeout? signal? main loop and flags? what?

exit(0)


### log loop			----------------------------------------------

# FIXME make FIFO automatically. os.mkfifo(cf.log_pipe)
if os.access(cf.get('mod_log/pipe'), os.R_OK) == False:
	log.fatal("cannot access FIFO(%s)." % cf.get('mod_log/pipe'), os.EX_CONFIG)

logger_message = hcu_logger.Logger("messages", cf.get('mod_log/pipe'))
logger_message.loop()


