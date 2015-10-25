#!/usr/bin/python

import os
import time

if __name__ == '__main__':
	for f in os.listdir(os.getcwd()) :
		if f.endswith(".pid"):
			os.system("kill -9 %s" % f.split(".")[0])
			os.remove(f)
			