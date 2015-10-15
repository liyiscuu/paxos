#!/usr/bin/python
import ConfigParser
import random
import sys
import getopt
import time
import copy
import msg

class Acceptor(msg.Node):
	def __init__(self,params,id):
		msg.Node.__init__(self,None,None)
		
	def do_event(self,event_id,sock):
		pass
		
if __name__ == '__main__':
	pass