#!/usr/bin/python
import ConfigParser
import random
import sys
import getopt
import time
import copy
import msg

class Client(msg.Node):
	def __init__(self,params,id):
		print "Client Init"
		self.params = params
		self.id = id
		self.base = -1
		bind_addr,connect_addr = self.get_address()
		msg.Node.__init__(self,bind_addr,connect_addr,1)
		
	def get_address(self):
		#print self.params
		proposers = self.params['proposers'].split()
		
		return (None,proposers[0])
		
	def do_connect(self,peer):
		print 'Client' , self.id , peer
		peer['value'] = self.base
		peer['time']=time.time()
		self.base -= 10000
	
	def do_timeout(self,peer):
		for peer in self.peers:
			if peer['connected']:
				try:
					if time.time() - peer['time'] >= 10:
						print 'send v'
						peer['value'] = peer['value'] - 1
						self.send_msg(peer,peer['value'])
						peer['time']=time.time()
						#print peer['sbuf']
				except:
					pass

if __name__ == '__main__':
	pass