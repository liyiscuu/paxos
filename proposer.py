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

class Proposer(msg.Node):
	
	TIME_OUT = 8
	
	def __init__(self,params,id):
		funcs = { 'client_req': self.do_client_req,
				  'prepare_ack':self.do_prepare_ack,
				  'accept_ack':self.do_accept_ack
				}
		
		self.params = params
		self.id = id
		self.base = int(self.params['paxos_id_base'])
		self.P1_size = int(self.params['p1_windows_size'])
		self.acceptor_num = len(self.params['acceptors'].split())
		
		bind_addr,connect_addr = self.get_address()
		logout(log.LOG_INFO, "Proposer Init %d:, bind_addr:%s, connect_addr:%s" % (self.id,str(bind_addr),str(connect_addr)))
		msg.Node.__init__(self,funcs,bind_addr,connect_addr,2)
		
		self.values = []
		self.P1_insts = {}
		self.P2_insts = {}
		self.next_iid = 0
	
	def get_address(self):
		#print self.params
		acceptors = self.params['acceptors']
		proposers = self.params['proposers'].split()
		
		return (proposers[self.id],acceptors)
	
	def get_next_id(self,paxos_id=None):
		if paxos_id is None : return self.id
		return  paxos_id + self.base
		
	def create_P1_instance(self,paxos_id=None,iid = None):
		inst = {'iid':0,
				'paxos_id':0,
				'value_v':None,
				'value_n':None,
				'myself_v':False,
				'quorum':{},
				'time':0
			}
		if iid is not None:
			inst['iid'] = iid
		else:
			inst['iid'] = self.next_iid
			self.next_iid += 1
		inst['paxos_id'] = paxos_id if paxos_id is not None else self.get_next_id(None)
		
		return inst
		
	def fill_P1(self):
		if self.P1_size <= len(self.P1_insts) : return
		for i in xrange(self.P1_size - len(self.P1_insts)):
			inst = self.create_P1_instance()
			self.P1_insts[inst['iid']] = inst
			self.send_prepare_msg(inst)
	
	def try_accept(self):
		#check quorum
		insts = sorted(self.P1_insts.items(), key=lambda d:d[0])
		ret = False
		for inst in insts:
			inst = inst[1]
			if len(inst['quorum']) >= (self.acceptor_num/2 + 1):
				#do P2
				if inst['value_v'] is None:
					try:
						inst['value_v'] = self.values.pop(0)
						inst['value_n'] = inst['paxos_id']
						inst['myself_v'] = True
					except:
						continue
					
				inst = self.move_to_P2(inst)
				self.send_accept_msg(inst)
				ret = True
			
		return ret
			
	def move_to_P2(self,inst):
		del self.P1_insts[inst['iid']]
		inst['quorum'] = {}
		self.P2_insts[inst['iid']] = inst
		return inst
		
	def send_accept_msg(self,inst):
		data = {'node_id':self.id,'iid':inst['iid'],'paxos_id':inst['paxos_id'],'value':inst['value_v']}
		for peer in [ x for x in self.peers if x['connected'] and x['type'] == 'acceptor']:
			self.send_msg(peer,'accept_req',data)
		inst['timeout']=time.time() + random.randint(3,Proposer.TIME_OUT)
		logout(log.LOG_DEBUG,'%d Send AcceptReq MSG:%s' % (self.id,data))
		
	def send_prepare_msg(self,inst):
		data = {'node_id':self.id,'iid':inst['iid'],'paxos_id':inst['paxos_id']}
		for peer in [ x for x in self.peers if x['connected'] and x['type'] == 'acceptor']:
			self.send_msg(peer,'prepare_req',data)
		inst['timeout']=time.time() + random.randint(3,Proposer.TIME_OUT)
		logout(log.LOG_DEBUG,'%d Send PrepareReq MSG:%s' % (self.id,data))
		
	def do_connect(self,peer):
		logout(log.LOG_INFO,'connect:%s' % str(peer['addr']))
		peer['type'] = 'acceptor'
		
	def do_accept(self,peer):
		logout(log.LOG_INFO,'accept:%s' % str(peer['addr']))
		peer['type'] = 'client'
	
	def do_client_req(self,data,peer):
		assert(peer['type'] == 'client')
		self.values.append(data)
		logout(log.LOG_INFO,'RECV value:%s,%s' % (str(data),str(self.values)))
		if self.try_accept():
			self.fill_P1()
	
	def preemp_inst(self,inst,paxosid):
		new_paxos_id = self.get_next_id(inst['paxos_id'])
		while paxosid > new_paxos_id:
			new_paxos_id = self.get_next_id(new_paxos_id)
			
		if inst['myself_v'] :
			#reinsert to values,but may chang the order
			self.values.insert(0,inst['value_v'])
		
		new_inst = self.create_P1_instance(new_paxos_id,inst['iid'])
		self.P1_insts[inst['iid']] = new_inst
		time.sleep(random.random()*2)
		self.send_prepare_msg(new_inst)
			
	def do_prepare_ack(self,data,peer):
		logout(log.LOG_INFO,'recv Prepare_ACK msg:%s from %d' % (str(data),data['node_id']))
		assert(peer['type'] == 'acceptor')
		
		# 1.get inst
		try:
			inst = self.P1_insts[data['iid']]
		except:
			# can't find, ignore
			return  
		
		# 2. handle ack
		paxosid = data['paxos_id']
		
		if paxosid > inst['paxos_id'] :
			#inc self paxos_id & resend
			logout(log.LOG_WARNING,'IID:%d,recv NEW paxos_id:%d > %d,Inc myself id' % (inst['iid'],paxosid,inst['paxos_id']))
			self.preemp_inst(inst,paxosid)
			
		elif paxosid < inst['paxos_id']:
			#drop
			logout(log.LOG_WARNING,'IID:%d,recv OLD paxos_id:%d < %d,Drop it' % (inst['iid'],paxosid,inst['paxos_id']))
			
		else:
			#handle
			acceptor_id = data['node_id']
			value_n = data['value_n']
			value_v = data['value_v']
			logout(log.LOG_INFO,'IID:%d,recv SAME paxos_id:%d ,from %d, value_v:%s,value_n:%s,quorum:%s' % (inst['iid'],paxosid,acceptor_id,str(value_v),str(value_n),str(inst['quorum'])))
			
			if inst['quorum'].get(acceptor_id) is None:
				inst['quorum'][acceptor_id] = 1
				
				# set quorum values
				if value_v is not None:
					assert(value_n is not None)
					if value_n > inst['value_n']:
						inst['value_n'] = value_n
						inst['value_v'] = value_v

		if self.try_accept():
			self.fill_P1()
		
	def do_accept_ack(self,data,peer):
		logout(log.LOG_INFO,'recv Accept_ACK msg:%s' % str(data))
		assert(peer['type'] == 'acceptor')
		# 1.get inst
		try:
			inst = self.P2_insts[data['iid']]
		except:
			# can't find, ignore
			return  
		
		# 2. handle ack
		paxosid = data['paxos_id']
		
		if paxosid == inst['paxos_id'] :
			acceptor_id = data['node_id']
			logout(log.LOG_INFO,'Inst:%s, Accept_ACK from %s, ballot:%s' % (inst['iid'],acceptor_id,inst['paxos_id']))

			if inst['quorum'].get(acceptor_id) is None:
				inst['quorum'][acceptor_id] = 1
				if len(inst['quorum']) >= (self.acceptor_num/2 + 1):
					logout(log.LOG_PRT,'Inst:%s,REACHED QUORUM!!, ballot:%s,value:%s' % (inst['iid'],inst['paxos_id'],inst['value_v']))
					del self.P2_insts[data['iid']]
		else:
			logout(log.LOG_WARNING,'Accept_ACK,IID:%d,recv NOT Same paxos_id:%d > %d' % (inst['iid'],paxosid,inst['paxos_id']))
			self.preemp_inst(inst,paxosid)
			del self.P2_insts[data['iid']]
	
	def do_timeout(self,peer):
		for iid,inst in self.P1_insts.items() :
			if len(inst['quorum']) >= (self.acceptor_num/2 + 1): continue
			if inst['timeout'] <= time.time():
				self.send_prepare_msg(inst)
		
		for iid,inst in self.P2_insts.items() :
			if len(inst['quorum']) >= (self.acceptor_num/2 + 1): continue
			if inst['timeout'] <= time.time():
				self.send_accept_msg(inst)
				
		
		self.fill_P1()

		#print '(%d)P1:' % self.id, self.P1_insts
		#print '(%d)P2:' % self.id, self.P2_insts
		#print '(%d)v:' % self.id,self.values

if __name__ == '__main__':
	pass