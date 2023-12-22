#!/usr/bin/env python

#
# The Personis system is copyright 2000-2011 University of Sydney
# Licenced under GPL v3
#


import sys
import bottle
import Personis_server
import Personis_base
import Personis_globals
from Personis_exceptions import *
import socket
import os
import logging
import argparse
import configparser
from multiprocessing import Process, Queue
import cronserver

class Access(Personis_server.Access):

	def __init__(self, model = None, user=None, password=None, app=None, description="", configfilename="~/.personis.conf", modelserver=None, debug=0):
		self.model = model
		self.debug = debug
		self.port = 2005
		self.hostname = 'localhost'
		self.modelname = model
		self.configfile = os.path.expanduser(configfilename)

		self.config = configparser.ConfigParser()
		
		try: 
			self.config.readfp(open(self.configfile, "r"), self.configfile)
			self.port = self.config.get('personis_client', 'client.server_port')
		except: 
			pass

		try: 
			self.hostname = self.config.get('personis_client','client.serverHost')
			# hack to cope with different config parsers 
			if self.hostname[:1] in ['"',"'"] and  self.hostname[-1:] in ['"',"'"]:
				self.hostname = self.hostname[1:-1] # strip off quotes
		except: 
			pass

		try:
			(self.modelname, modelserver) = self.modelname.split('@')
		except:
			pass
		if modelserver == None:
			self.modelserver = self.hostname + ":" + str(self.port)
		else:
			self.modelserver = modelserver
		logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
		logging.info(">>>>Access: %s::%s", self.modelname, self.modelserver)

		Personis_server.Access.__init__(self, model=self.modelname, modelserver=self.modelserver, user=user, password=password, app=app, description=description, debug=debug)


def runServer(modeldirname, configfile):
	logging.info("++++++++++++++++++++++++++++++++++++++++")
	logging.info("serving models in '%s'" % (modeldirname))
	logging.info("config file '%s'" % (configfile))
	logging.info("starting cronserver")
	logging.info("++++++++++++++++++++++++++++++++++++++++")
	Personis_globals.modeldir = modeldirname
#	cronserver.cronq = Queue()
	p = Process(target=cronserver.cronserver, args=(cronserver.cronq, Personis_globals.modeldir))
	p.start()

	config = configparser.ConfigParser()
	config.readfp(open(os.path.expanduser(configfile), "r"))
	port = config.get('personis_server', 'server.server_port')
	host = config.get('personis_server', 'server.socket_host')
	logging.info("Modeldir: %s, server: %s, port:%s"% ( Personis_globals.modeldir, host, port))
	try:
		try:
			bottle.run(host=host, port=port, debug=True)
		except Exception as E:
			logging.error("Failed to run Personis Server:" + str(E))
	finally:
		logging.info("Shutting down Personis Server.")
		p.put(dict(op="quit"))
		p.join()

if __name__ == "__main__":
	aparser = argparse.ArgumentParser(description='Personis Server')
	aparser.add_argument('--models', help='directory holding models', default="Models")
	aparser.add_argument('--log', help='log file', default="stdout")
	aparser.add_argument('--config', help='config file for server', default='~/.personis.conf')
	args = aparser.parse_args(sys.argv[1:])
	if args.log != "stdout":
		sys.stdout = open(args.log, "w", 0)

	runServer(args.models, args.config)

