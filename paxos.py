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
	return  conf.items("main")



	
if __name__ == '__main__':
	try:
		opts, args = getopt.getopt(sys.argv[1:], "c:t:")
	except getopt.error, msg:
		print "Error Parameters!"
		sys.exit(-1)
	
	t = os.getenv('PAXOS_TYPE')
	if t is not None: type = t
	
	# option processing
	for option, value in opts:
		if option == "-c":
			config_file = value
		if option == "-t":
			TYPE = value
 
	print 'Config File : %s, Type : %s' % (config_file,TYPE)
	
	params = get_config()

	if TYPE == 'acceptor':
		node = acceptor.Acceptor(params,ID)
	elif TYPE == 'proposer':
		node = proposer.Proposer(params,ID)
	
	
	os.system("touch %d.pid" % os.getpid())
	
	node.loop()
	
		