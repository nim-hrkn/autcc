#!/usr/bin/env python 
import sys
import sqlite3
import os
import re
import shutil
#---------------------

class QmasOutInfo:
    def __init__(self,path):
        self.lastiter=0
        self.successoutput=0
        self.cdiff=-999
        self.nscf=-999
        self.input="input_scf.txt"
        self.output="output_scf.txt"

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

#---------------

class keyvalue:
	def __init__(self,key,value):
		self.key=key
		self.value=value
		self.changed=0

class keyvalueList:
	def __init__(self,filename):
		self.list=[]
		f=open(filename,"r")
		lines=f.readlines()
		f.close()
		lines2=lines
		for n in lines:
			s=n.rstrip()
			sl=s.split()
			if sl[0]=="add_after":
				self.add_after=sl[1]
				continue
			if len(sl)>=3:
				key=sl[0]; value=sl[2]
				self.list.append(keyvalue(key,value))
			

def change_key(lines,kv):
	for k1 in range(0,len(kv.list)):
		k=kv.list[k1]
		find=re.compile("^ *"+k.key+" ")
		lines2=[]
		for line in lines:
			if find.match(line):
				#print "match:",line
				s=k.key+" = " + k.value
				lines2.append(s)
				kv.list[k1].changed+=1
			else:
				lines2.append(line)
		lines=lines2
	todo=0
	for k in kv.list:
		if k.changed==0:
			todo+=1
        if todo>1:
	    #print "todo",todo
            find=re.compile("^ *"+kv.add_after+" *$")
	    lines2=[]
	    for line in lines:
		lines2.append(line)
		if find.match(line):
			#print "match"
	    		for k in kv.list:
				if k.changed==0:
					lines2.append(k.key+" = "+k.value)
	    lines=lines2

	return lines
			

def apply_keyvalue(inputfile,senario,outputfile):
    kv=keyvalueList(senario)

    f=open(inputfile,"r")
    lines=f.readlines()
    f.close()
    lines2=[]
    for n in lines:
	lines2.append(n.rstrip())	
    lines=lines2

    lines=change_key(lines,kv)

    f=open(outputfile,"w")
    for n in lines:
	f.write(n+"\n")
    f.close()
    return 0 

#ret=apply_keyvalue("data/Fdd2/xsf_2_i0040/input_scf.txt","senario1","input")
#
#exit( ret )

#---------------------------------

class DBrow:
	def __init__(self,row):
		self.hash=row[0]
		self.path=row[1]
		self.mat=row[2]
		self.dbstatus=row[3]
		self.count=row[4]
		self.execstatus=row[5]

class DB:
    def __init__(self,conn,dbname,mat):
		self.conn=conn
		self.dbname=dbname
		self.mat=mat

    def add(self,filelist):
	c = self.conn.cursor()
	# n0 = hash, n1=dirname
	for n  in filelist:
		hash=n.hash
		dirname=n.path
		msg="select count(*) from "+self.dbname+" where dirname='%s'" %(dirname)
		c.execute(msg)
		result=c.fetchall()
		found=0
		for row in result:
			found=row[0]
		if found==1:
			print "data exists, do nothing for "+dirname
		else:
			msg="insert into "+self.dbname+" values('%s','%s','%s','%s',%d,'%s')" % ( hash,dirname,self.mat,'new',0,'idle' )
			print msg
			c.execute(msg)

	self.conn.commit() # save db 
	c.close()

    def add_count(self, hash):
	c=self.conn.cursor()
	msg="select count from "+self.dbname+" where hash='%s'" %(hash)
	c.execute(msg)
	result=c.fetchall()
	print "result=",result
	if len(result)==0:
		print "erorr: failed to find hash="+hash+" in DB"
		print msg
		exit(10)
	for row in result:
		count=row[0]
	count+=1
	msg="update "+self.dbname+" set count="+str(count)+" where hash='%s' " % (hash)
	print msg
	c.execute(msg)
	self.conn.commit()
	c.close()

    def get_list_status_is(self,st1,st2):
	c=self.conn.cursor()
	if len(st2)>0 and len(st1)>0 :
		msg="select * from "+self.dbname+" where dbstatus='%s' and execstatus='%s'" %(st1,st2)
	elif len(st2)>0 and len(st1)==0:
		msg="select * from "+self.dbname+" where execstatus='%s'" %(st2)
	elif len(st1)>0 and len(st2)==0:
		msg="select * from "+self.dbname+" where dbstatus='%s'" %(st1)

	print msg
	c.execute(msg)
	result=c.fetchall()
	#print result
	r=[]
	for row in result:
		r.append(DBrow(row))
	c.close()
	return r

    def change_status(self,hash,st1,st2):
        c=self.conn.cursor()
        s2=" where hash='%s'" %(hash)
        if len(st2)>0 and len(st1)>0 :
                s1=" set dbstatus='%s', execstatus='%s'" %(st1,st2)
                msg="update "+self.dbname+s1+s2
        elif len(st2)>0 and len(st1)==0:
		s1=" set execstatus='%s'" %(st2) 
                msg="update "+self.dbname+s1+s2
        elif len(st1)>0 and len(st2)==0:
		s1=" set dbstatus='%s'" %(st1) 
                msg="update "+self.dbname+s1+s2
	print msg
        c.execute(msg)
	self.conn.commit()
        c.close()


def yield_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

def get_filelist(filelist):
    f=open(filelist,"r")
    lines=f.readlines()
    f.close()
    filelist=[]
    for n in lines:
	[path,hash]=n.split()
	filelist.append([hash,path,'sio2'])
    return filelist

def get_dbstatus(filename):
	print filename
	try:
		f=open(filename)
	except:
		return 0
	lines=f.readlines()
	f.close()
	msg=" === successfully"
	for n in lines:
		s=n[:len(msg)]	
		if s==msg:
			return 1
	return 0

def get_liststatus(filelist):
	for [path,hash,mat] in filelist:
		r=get_status(path+"/output_scf.txt")
		print path,r

def read_hash_from_ID(s):
    f=open(s,'r')
    lines=f.readlines()
    f.close()
    hash=lines[0]
    hash=hash.rstrip()
    return hash

class PathHash:
	def __init__(self,hash,path):
		self.hash=hash
		self.path=path

def yield_PathList(dir):
    filelist=yield_all_files(dir)
    list=[]
    for s in filelist:
        n=len(s)
        if s[n-4:n]=="/.ID":
                path=s[:-4]
                hash=read_hash_from_ID(s)
		pathlast=path[-2:len(path)]
		if pathlast!=".o":
                	list.append(PathHash(hash,path))
    return list

		
#def yield_pathlist(dir):
#    filelist=yield_all_files(dir)
#    list=[]
#    for s in filelist:
#	n=len(s)	
#	if s[n-4:n]=="/.ID":
#		path=s[:-4]
#		hash=read_hash_from_ID(s) 
#		list.append([hash,path])
#    return list


def file_copy(s,t):
	print "t=",t
	f=os.path.exists(t)
	if f:
		print t, "exists, skip it"
		return 1
	cmd="cp -RP "+s+" "+t
	print cmd
	os.system(cmd)
	return 0

def make_file(filename,content):
	f=open(filename,"w")
	f.write(content+"\n")
	f.close()

class Info:
	def __init__(self):
		self.dbname="sio2"
		self.senariodir="senario"
		self.inputdir="inputdata"
		self.temporarydir="calcdata"
		self.execstatusfile=".EXECSTATUS"
		self.mat="insulator1"
		self.dbfile="sio2data.sqlite3"
		self.mode="init"
		error=0
		print sys.argv
		for iarg in range(1,len(sys.argv)):
			n=sys.argv[iarg]
			if n=="-init":
				self.mode="init"
			elif n=="-send":
				self.mode="send"
			elif n=="-recv":
				self.mode="recv"
			elif n=="-purge":
				self.mode="purge"
			else:
				print "failed to understand option ",n
				error+=1
		if error>0:
			sys.exit(10)

	def temporarypath(self,hash,count):
		return self.temporarydir+"/"+hash+"."+str(count)
	def execstatuspath(self,hash,count):
		return self.temporarypath(hash,count)+"/"+self.execstatusfile
	def resultpath(self,n):
		return n+".o"
				
			

#-----------------------------------------------
#begin

info=Info()

# connect DB
conn=sqlite3.connect(info.dbfile)
db=DB(conn,info.dbname,info.mat)

print "mode=",info.mode

if info.mode=="init":
	filelist=yield_PathList(info.inputdir)
	db.add(filelist)

elif  info.mode=="send":
    result=db.get_list_status_is("new","idle")
    for n in result:
	print n.hash,n.path
        odir=info.temporarypath(n.hash,n.count)
	print "temporarydir=",odir
	file_copy(n.path,odir)
	db.change_status(n.hash,"submitted","idle")
        make_file(info.execstatuspath(n.hash,n.count),"idle")

	#input= n.path+"/"+datatype.input
        #senariofile=info.senariodir+"/"+n.mat+"_"+str(n.count)
        #print input,senariofile,odir
	#output=odir+"/"+datatype.input
	#r= apply_keyvalue (input,senariofile,output)
	#print output, " is changed."

elif info.mode=="recv":
    result=db.get_list_status_is("submitted","finished")
    for n in result:
	result=QmasOutInfo(info.temporarypath(n.hash,n.count))
	if result.success()==1:
		print "OK",n.path,n.hash,n.count
		db.change_status(n.hash,"calculated","finished")
		tdir=info.temporarypath(n.hash,n.count)
		path=info.resultpath(n.path)
		file_copy(tdir,path)
	else:
		print "NG",n.path,n.hash,n.count
		db.add_count(n.hash)
		db.change_status(n.hash,"new","idle")

elif info.mode=="purge":
    result=db.get_list_status_is("calculated","finished")
    for n in result:
	print n.hash
	for i in range(0,n.count+1):
		print i
		tdir=info.temporarypath(n.hash,i)
		print tdir
		shutil.rmtree(tdir)

#end
#-----------------------------------------------

