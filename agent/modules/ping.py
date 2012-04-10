
_plugin_name	= 'ping'
_plugin_version	= '0.1.0'
_plugin_type	= 'periodic'


import orion.plugin
import time



class ping(orion.plugin.Plugin):
	def initialize(self):
		return

	def task_pre(self):
		self.logger.debug('preparing...')
		return

	def task_post(self):
		self.logger.debug('go to bed...')
		return

	def task_check(self):
		super().task_report()
		self.logger.debug('is alive!')
		return

	def task_report(self):
		super().task_report()
		self.logger.debug('report!')
		return


# vim:set ts=4 sw=4:
