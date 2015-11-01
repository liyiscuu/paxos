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
import db

class Acceptor(msg.Node):
	def __init__(self,params,id):
		funcs = { 'prepare_req':self.do_prepare_req,
				  'accept_req':self.do_accept_req
				}
		
		self.db = db.DB()
		self.params = params
		self.id = id
		bind_addr,connect_addr = self.get_address()
		logout(log.LOG_INFO,"Acceptor Init:, bind_addr:%s, connect_addr:%s" % (str(bind_addr),str(connect_addr)))
		msg.Node.__init__(self,funcs,bind_addr,connect_addr)
		
	def get_address(self):
		acceptors = self.params['acceptors'].split()
		return (acceptors[self.id],None)
		
	def new_inst(self,iid,paxos_id,value_v=None,value_n=None):
		inst = {'iid':iid,'paxos_id':paxos_id,'value_v':value_v,'value_n':value_n}
		return inst
	
	def send_prepare_ack(self,inst,peer) :
		data = {'node_id':self.id,'iid':inst['iid'],'paxos_id':inst['paxos_id'],'value_v':inst['value_v'],'value_n':inst['value_n']}
		self.send_msg(peer,'prepare_ack',data)
	
	def send_accept_ack(self,inst,peer) :
		data = {'node_id':self.id,'iid':inst['iid'],'paxos_id':inst['paxos_id'],'value_v':inst['value_v'],'value_n':inst['value_n']}
		self.send_msg(peer,'accept_ack',data)
		
	def do_accept(self,peer):
		logout(log.LOG_INFO,'accept:%s' % str(peer['addr']))
	
	def do_prepare_req(self,data,peer):
		logout(log.LOG_INFO,'recv Prepare msg:%s from %s' % (str(data),str(data['node_id'])))
		iid = data['iid']
		
		save_inst = self.db.search(iid) 
		if save_inst is None:
			logout(log.LOG_DEBUG,'recv Prepare msg,Mine is None:%s from proposer:%s' 
						% (str(data),str(data['node_id'])))
			save_inst = self.new_inst(iid,data['paxos_id'])
			self.db.insert(save_inst)
		else:
			if save_inst['paxos_id'] <= data['paxos_id']:
				logout(log.LOG_DEBUG,'recv Prepare msg,Newer or Same:%d<=%d from proposer:%s' 
								% (save_inst['paxos_id'],data['paxos_id'],str(data['node_id'])))
				save_inst['paxos_id'] = data['paxos_id']
				self.db.change(iid,save_inst)
			else:
				#don't save
				logout(log.LOG_DEBUG,'recv Prepare msg,Mine is Newer:%d>%d from proposer:%s' 
								% (save_inst['paxos_id'],data['paxos_id'],str(data['node_id'])))
		
		#send prepare_ack
		self.send_prepare_ack(save_inst,peer)
		
		logout(log.LOG_DEBUG,'now,Inst %d DATA Store =%s' % (iid,str(save_inst)))
		
	def do_accept_req(self,data,peer):
		logout(log.LOG_INFO,'recv Accept msg:%s from %s' % (str(data),str(data['node_id'])))
		iid = data['iid']
		save_inst = self.db.search(iid) 
		if save_inst is None:  
			#ok ,Accept
			logout(log.LOG_INFO,'Inst %s , Mine is None,Accept Value:%s, ballot:%s from %d' 
					% (iid,data['value'],data['paxos_id'],data['node_id']))
			save_inst = self.new_inst(iid,data['paxos_id'],value_v = data['value'],value_n=data['paxos_id'])
			self.db.insert(iid,save_inst)
			self.send_accept_ack(save_inst,peer)
			logout(log.LOG_DEBUG,'now,Inst %d DATA Store =%s' % (iid,str(save_inst)))

		elif save_inst['paxos_id'] <= data['paxos_id'] :
			#ok ,Accept
			logout(log.LOG_INFO,'Inst %s , Accept Value:%s, ballot:%s(OLD=%s)' 
						% (iid,data['value'],data['paxos_id'],save_inst['paxos_id']))
			save_inst = self.new_inst(iid,data['paxos_id'],value_v = data['value'],value_n=data['paxos_id'])
			self.db.change(iid,save_inst)
			
			self.send_accept_ack(save_inst,peer)
			logout(log.LOG_DEBUG,'now,Inst %d DATA Store =%s' % (iid,str(save_inst)))

		else:
			#Don't Accept it
			logout(log.LOG_INFO,"Inst %s , Don't Accept Value:%s,ballot:%s from %d" 
						% (iid, data['value'],data['paxos_id'],data['node_id']))
			self.send_accept_ack(self.new_inst(iid,save_inst['paxos_id']),peer)
		
		
if __name__ == '__main__':
	pass