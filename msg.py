#!/usr/bin/python

import socket,sys
import time
import copy
import select

class Node:

	MSG_LEN = 256
	
	#addr ip:port
	def __init__(self,bind_addr=None,peer_addrs=None,timeout = 5):
		
		self.timeout = timeout
		
		if bind_addr is not None :
			self.bind_addr = bind_addr.split(':')
			self.bindsock = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
			self.bindsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
			self.bindsock.bind((self.bind_addr[0], int(self.bind_addr[1])))  
			self.bindsock.setblocking(False)
			self.bindsock.listen(5)
		else:
			self.bindsock = None
			self.bind_addr = None

		self.peer_addrs = [x.split(':') for x in peer_addrs.split()] if peer_addrs is not None else []
		self.sockets = []
		sock = {}
		for addr in self.peer_addrs :
			sock['addr'] = addr
			sock['connect-to'] = True
			sock['connect'] = False
			sock['rbuf'] = []
			sock['sbuf'] = []
			sock['sock'] = None
			self.sockets.append(copy.copy(sock))
			
		print self.bind_addr,self.peer_addrs,self.timeout
		print self.sockets

	def send(self,sock,msg):
		assert(len(msg) < Node.MSG_LEN)
		return sock['sbuf'].append(msg + ' ' * (Node.MSG_LEN-len(msg)) )
	
	def recv(self,sock):
		if len(sock['rbuf']) > 0:
			return sock['rbuf'].pop(0)
		else :
			return None
	
	def do_event(self,event_id,sock):
		print event_id,sock
		if event_id == 'read' :
			msg = self.recv(sock)
			self.send(sock,msg)

	def loop(self):
		while True:
			# 1. connect
			for sock in self.sockets:
				if not sock['connect']:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
					s.settimeout(3)
					try :
						s.connect((sock['addr'][0],int(sock['addr'][1])))
						sock['connect'] = True
						s.settimeout(None)
						
						sock['sock'] = s
						self.do_event('connect',sock)
					except:
						s.close()
					
			# 2. select
			socks = [x['sock'] for x in self.sockets if x['connect']] 
			if self.bindsock is not None : socks = socks + [self.bindsock]
			print socks
			
			readable , writable , exceptional = select.select(socks, [], socks, 1)
			
			print readable,writable,exceptional
			
			if self.bindsock in readable :
				#accept
				conn,addr=self.bindsock.accept()
				print conn,addr
				sock = {}
				sock['addr'] = addr
				sock['connect-to'] = False
				sock['connect'] = True
				sock['rbuf'] = []
				sock['sbuf'] = []
				sock['sock'] = conn
				self.sockets.append(copy.copy(sock))
				self.do_event('accept',self.sockets[-1])
			
			for s in readable :
				#read
				for s1 in self.sockets :
					if s1['sock'] == s :
						msg = s.recv(Node.MSG_LEN)
						print msg
						if len(msg) == 0:
							#error
							s1['sock'].close()
							s1['sock'] = None
							s1['connect'] = False
							if not s1['connect-to'] :
								self.sockets.remove(s1)
						else :
							s1['rbuf'].append(msg.strip())
							self.do_event('read',s1)
						break
						
			for s in exceptional:
				#err
				assert(False)
			
			# 3. send
			for s in self.sockets :
				for msg in s['sbuf'] :
					s['sock'].send(msg)
				s['sbuf'] = []
				
	
if __name__ == '__main__':
	
	#n = Node(None,'10.74.120.2:9132 10.17.12.34:23',10)
	n = Node('10.74.120.2:1234',None,10)
	#n = Node('10.74.120.2:1234','10.74.120.2:9132 10.17.12.34:23',10)
	
	n.loop()
	
	