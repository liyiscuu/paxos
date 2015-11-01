#!/usr/bin/python
import sys
import time
try:
	from termcolor import colored, cprint
except:
	def colored(str1,str2=None,str3=None):
		return str1 

LOG_PRT 	= 0
LOG_ERROR 	= 1
LOG_WARNING = 2
LOG_INFO	= 3
LOG_DEBUG 	= 4

LogCfg = { 
	LOG_PRT:('---','magenta'),
	LOG_ERROR: ('ERROR','red'),
	LOG_WARNING:('WARNING','yellow'),
	LOG_INFO:('INFO','green'),
	LOG_DEBUG:('DEBUG','grey')
}

LogLevel = LOG_ERROR

def set_log(name,id,bgcolor):
	global HEAD,BGCOLOR
	HEAD = "%s(%d):" %(name,id)
	BGCOLOR = bgcolor
	
def logout(level,str):
	if level <= LogLevel :
		str = colored(HEAD,'white',BGCOLOR) + colored('[%s]:%s' % (LogCfg[level][0],str),LogCfg[level][1])
		print str
		