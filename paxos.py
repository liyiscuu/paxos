#!/usr/bin/python
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

config_file = '/home/liyi/work/paxos/paxos.conf'
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
		node = acceptor.Acceptor(params,ID)
	elif TYPE == 'proposer':
		node = proposer.Proposer(params,ID)
	elif TYPE == 'client':
		node = client.Client(params,ID)
	
	os.system("touch %d.pid" % os.getpid())
	
	node.loop()
	
		