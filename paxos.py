#!/usr/bin/python
# coding=gbk
import ConfigParser
import random
import sys,os
import getopt
import time
import copy
import msg
import proposer
import acceptor
import leaner
import client
import log

config_file = '../paxos.conf'
TYPE = 'proposer'
ID = 0

def get_config():
	conf = ConfigParser.ConfigParser()
	conf.read(config_file)
	d = {}
	for item in conf.items("main"):
		d[item[0]] = item[1]
	return d

if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "c:t:")
	except getopt.error, msg:
		print "Error Parameters!"
		sys.exit(-1)
	
	t = os.getenv('PAXOS_TYPE')
	if t is not None: TYPE = t
	
	id = os.getenv('PAXOS_ID')
	if id is not None: ID = int(id)
	
	# option processing
	for option, value in opts:
		if option == "-c":
			config_file = value
		if option == "-t":
			TYPE = value
 
	#print 'Config File : %s, Type : %s' % (config_file,TYPE)
	
	params = get_config()
	#print params
	
	if TYPE == 'acceptor':
		log.set_log('Acceptor',ID,'on_blue')
		node = acceptor.Acceptor(params,ID)
	elif TYPE == 'proposer':
		log.set_log('Proposer',ID,'on_green')
		node = proposer.Proposer(params,ID)
	elif TYPE == 'client':
		log.set_log('Client',ID,'on_yellow')
		node = client.Client(params,ID)
	
	os.system("touch %d.pid" % os.getpid())
	
	node.loop()
	
		