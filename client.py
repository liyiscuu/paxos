#!/usr/bin/python
# coding=gbk
import ConfigParser
import random
import sys
import getopt
import time
import copy
import msg
import log
from log import logout
import paxos

class Client(msg.Node):
	def __init__(self,params,id):
		logout(log.LOG_INFO,"Init")
		self.params = params
		self.id = id
		self.base = 0
		bind_addr,connect_addr = self.get_address()
		msg.Node.__init__(self,None,bind_addr,connect_addr,1)
		
	def get_address(self):
		#print self.params
		proposers = self.params['proposers'].split()
		
		return (None,' '.join(proposers))
		
	def do_connect(self,peer):
		logout(log.LOG_INFO, 'Connect: %s' % (peer['addr']))
		peer['value'] = self.base
		peer['time']=time.time()
		self.base -= 10000
	
	def do_timeout(self,peer):
		for peer in self.peers:
			if peer['connected']:
				if time.time() - peer['time'] >= 10:
					peer['value'] = peer['value'] - 1
					self.send_msg(peer,'client_req',peer['value'])
					peer['time']=time.time()
					logout(log.LOG_INFO,'Send v:%d to %s' % (peer['value'],str(peer['addr'])))
if __name__ == '__main__':
	pass