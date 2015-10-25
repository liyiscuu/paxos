#!/usr/bin/python
import ConfigParser
import random
import sys
import getopt
import time
import copy
import msg


class Proposer(msg.Node):
	def __init__(self,params,id):
		
		self.params = params
		self.id = id
		bind_addr,connect_addr = self.get_address()
		print "Proposer Init:%d , bind_addr:%s, connect_addr:%s" % (id,str(bind_addr),str(connect_addr)) 
		msg.Node.__init__(self,bind_addr,connect_addr)
		
		self.values = []
		self.P1_insts = []
		self.P2_insts = []
		
	def get_address(self):
		#print self.params
		acceptors = self.params['acceptors']
		proposers = self.params['proposers'].split()
		
		return (proposers[self.id],acceptors)
		
	def do_connect(self,peer):
		peer['type'] = 'acceptor'
		
	def do_accept(self,peer):
		peer['type'] = 'client'
		
	def do_read(self,peer):
		msg = self.recv_msg(peer)
		#print msg,peer
		if peer['type'] == 'client':
			self.values.append(msg)
			print self.values
		
if __name__ == '__main__':
	pass