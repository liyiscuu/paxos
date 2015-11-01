#!/usr/bin/python

import time
import copy
from log import logout

class DB:
	def __init__(self):
		self.db = {}
	
	def insert(self,inst):
		self.db[inst['iid']] = copy.copy(inst)
	
	def remove(self,iid):
		del self.db[iid]
	
	def change(self,iid,inst):
		self.db[iid] = copy.copy(inst)
	
	def search(self,iid):
		return copy.copy(self.db.get(iid))
	