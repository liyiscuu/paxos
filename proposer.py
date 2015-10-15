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
		msg.Node.__init__(self,bind_addr,connect_addr)
		
	def get_address(self):
		return ('10.74.120.2:1234','10.74.120.2:9132 10.17.12.34:23')
		
	def do_event(self,event_id,sock):
		print "++++++++++" + event_id
	
if __name__ == '__main__':
	pass