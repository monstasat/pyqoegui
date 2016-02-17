from gi.repository import Gio
import os, sys

class Backend():
	def __init__(self):
		# backend process id
		self.pid = 0

	def execute(self):
		self.pid = os.system("ats3-backend &")

	def terminate(self):
		os.system("kill " + str(self.pid))
