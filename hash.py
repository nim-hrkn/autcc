#!/usr/bin/env python 
import hashlib
import datetime
import sys

def get_hash(filepath):
	now=datetime.datetime.today()
	now_string = "%s-%s-%s-%s-%s-%s-%s" % (now.year,now.month,now.day,now.hour, now.minute,now.second, now.microsecond)
	hash = hashlib.sha1()
	hash.update(now_string)
	hash.update("hash making program")
    	hash.update(filepath)
    	return hash.hexdigest()

argv= sys.argv
argc=len(argv)

if (argc!=2):
	print "usage:"
	print "thisprogram path"
	print "output is sha1 hash" 
	sys.exit(10)

filename=argv[1]
r=get_hash(filename)
print r

