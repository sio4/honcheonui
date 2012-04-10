
_plugin_name	= 'register'
_plugin_version	= '0.1.0'
_plugin_type	= 'run-once'


import orion.plugin
import time



class register(orion.plugin.Plugin):
	def initialize(self):
		return

	def task_pre(self):
		self.logger.debug('yes, i am here!')
		return


# vim:set ts=4 sw=4:
