#!/usr/bin/env python 
import sys
import sqlite3
import os
import re
import shutil
#---------------------

from keyvalue import apply_keyvalue

qmas_inputfile="input_scf.txt"
qmas_outputfile="output_scf.txt"

class QmasInInfo:
    def __init__(self):
	x=0
    def apply(self,inputpath,senariofile,outputpath):
	input=inputpath+"/"+qmas_inputfile
	output=outputpath+"/"+qmas_inputfile
        r= apply_keyvalue (input,senariofile,output)
        print output, " is changed."
	

class QmasOutInfo:
    def __init__(self,path,fullpath=0):
        self.lastiter=0
        self.successoutput=0
        self.cdiff=-999
        self.nscf=-999
        #self.input="input_scf.txt"
        self.output=qmas_outputfile

	if fullpath==1:
		filename=path
	else:
		filename=path+"/"+self.output
        f = open(filename,'r')
        lin=f.readlines()
        f.close()
        for s in lin:
                s2=s[0:5]
                if s2==" out ":
                        v=s.split()
                        self.lastiter= int(v[1])
                        self.cdiff=float(v[2])
                s3=s[0:21]
                if s3==" === successfully end":
                        self.successoutput=1
                s4=s[0:6]
                if s4==" nscf=":
                        v=s.split()
                        self.nscf=int(v[1])

    def showinfo(self):
	print self.lastiter,self.nscf,self.success
    def success(self):
	if self.successoutput==1 and self.lastiter < self.nscf : 
		return 1
	else:
	 	return 0

if __name__ == "__main__":

    if len(sys.argv)==2:
	filename=sys.argv[1]
	r=QmasOutInfo(filename,fullpath=1)
	s=r.success()
	print "return code=",s
	sys.exit(s)
    else:
	print "usage ", sys.argv[0] , " output_of_qmas"
	sys.exit(255)

