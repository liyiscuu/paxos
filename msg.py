#!/usr/bin/python
# coding=gbk
import socket,sys
import time
import copy
import select
import json
from log import logout
import log

'''
   client_req(v)
   prepare_req : 	{'node_id','iid','paxos_id'}
   accept_req : 	{'node_id','iid','paxos_id','value'}
   prepare_ack:		{'node_id','iid','paxos_id','value_v','value_n'}
   accept_ack:		{'node_id','iid','paxos_id','value_v','value_n'}
   repeat()
'''
   
class Node:

	MSG_LEN = 256
	
	#addr: ip:port
	def __init__(self,msg_handle,bind_addr=None,peer_addrs=None,timeout = 5):
		
		#print bind_addr,peer_addrs,timeout
		self.timeout = timeout
		self.msg_handle = msg_handle
		
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
		self.peers = []

		for addr in self.peer_addrs :
			self.create_peer({'addr':addr,'connect-to':True,'connected':False,'sock':None})
			
		#print self.bind_addr,self.peer_addrs,self.timeout
		#print self.peers

	def create_peer(self,d):
		peer = {}
		peer['addr'] = d['addr']
		peer['connect-to'] = d['connect-to']
		peer['connected'] = d['connected']
		peer['rbuf'] = []
		peer['sbuf'] = []
		peer['sock'] = d['sock']
		self.peers.append(peer)
		return peer
		
	def send_msg(self,peer,msg_type,msg_data):
		msg={}
		msg['type']=msg_type
		msg['data']=msg_data
		msg = json.dumps(msg)
		assert(len(msg) < Node.MSG_LEN)
		peer['sbuf'].append(msg + ' ' * (Node.MSG_LEN-len(msg)) )
	
	def recv_msg(self,peer):
		if len(peer['rbuf']) > 0:
			return json.loads(peer['rbuf'].pop(0))
		else :
			return None
	
	def do_timeout(self,peer):
		logout(log.LOG_INFO,'time out')
	
	def do_read(self,peer):
		msg = self.recv_msg(peer)
		msg_type = msg['type']
		self.msg_handle.get(msg_type)(msg['data'],peer)
		#logout(log.LOG_ERROR, 'msg = %s' % str(msg))
		
	def do_connect(self,peer):
		logout(log.LOG_INFO,'connect to %s' % str(peer['addr']))
	
	def do_accept(self,peer):
		logout(log.LOG_INFO,'accept to %s' % str(peer['addr']))
	
	def do_event(self,event_id,peer):
		funcs = { 	'connect':self.do_connect, 
					'timeout':self.do_timeout,
					'accept':self.do_accept,
					'read':self.do_read }
					
		#print  event_id,peer
		funcs.get(event_id)(peer)

	def loop(self):
		oldtime = time.time()
		while True:
			# 1. connect
			for peer in self.peers:
				if not peer['connected']:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 2)
					s.settimeout(3)
					try :
						s.connect((peer['addr'][0],int(peer['addr'][1])))
						peer['connected'] = True
						s.settimeout(None)
						
						peer['sock'] = s
						self.do_event('connect',peer)
					except:
						s.close()
					
			# 2. select
			socks = [x['sock'] for x in self.peers if x['connected']] 
			if self.bindsock is not None : socks = socks + [self.bindsock]
			#print socks
			
			readable , writable , exceptional = select.select(socks, [], socks, 1)
			
			#print readable,writable,exceptional
			
			if self.bindsock in readable :
				#accept
				conn,addr=self.bindsock.accept()
				#print conn,addr
				peer = self.create_peer({'addr':addr,'connect-to':False,'connected':True,'sock':conn})
				self.do_event('accept',peer)
			
			for s in readable :
				#read
				for peer in self.peers :
					if peer['sock'] == s :
						try:
							msg = s.recv(Node.MSG_LEN)
						except:
							msg=''
						#print msg.strip()
						if len(msg) == 0:
							#error
							logout(log.LOG_WARNING,'peer %s disconnected!' % str(peer['addr']))
							peer['sock'].close()
							peer['sock'] = None
							peer['connected'] = False
							if not peer['connect-to'] :
								self.peers.remove(peer)
						else :
							peer['rbuf'].append(msg.strip())
							self.do_event('read',peer)
						break
						
			for s in exceptional:
				#err
				assert(False)
			
			# 3. send
			for peer in self.peers :
				if peer['connected']:
					for msg in peer['sbuf'] :
						peer['sock'].send(msg)
					peer['sbuf'] = []
			
			#4. check timout
			delta_time = time.time() - oldtime
			if delta_time >= self.timeout:
				self.do_event('timeout',None)
				oldtime = time.time()
			
			#logout('LOG_INFO','==')
if __name__ == '__main__':
	
	n = Node(None,'10.74.120.2:9132 10.74.120.2:1234',5)
	#n = Node('10.74.120.2:1234',None,10)
	#n = Node('10.74.120.2:1234','10.74.120.2:9132 10.74.120.2:9133',10)
	
	n.loop()
	
	