#!/usr/bin/env python 
import sys
import sqlite3
import os
import re
import shutil

from QmasOutInfo import QmasOutInfo 
#---------------------

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

class DBdef:
	def __init__(self):
		self.tables=["hash","dirname","material",\
"dbstatus","count", "execstatus",\
"time_last","time_init", "time_send", "time_recv","time_update"]

class DBrow:
	def __init__(self,row):

		self.hash=row[0]
		self.path=row[1]
		self.mat=row[2]
		self.dbstatus=row[3]
		self.count=row[4]
		self.execstatus=row[5]
		self.time_last=row[6]
		self.time_init=row[7]
		self.time_send=row[8]
		self.time_recv=row[9]
		self.time_update=row[10]

class DB:
    def __init__(self,conn,dbname,mat):
		self.conn=conn
		self.dbname=dbname
		self.mat=mat
		self.tables=DBdef()

    def createdb(self):
        c = self.conn.cursor()
	msg="create table batchcount (count)"
	c.execute(msg)
	msg="insert into batchcount values (0)"
	c.execute(msg)	
	msg="create table sio2 ("
	for n in range(0,len(self.tables)):
		s=self.tables[n] 
		if n!=0:
			add=","
		else:
			add=""
		msg = msg + add + s 
	msg = msg + ")"
        c.execute(msg)
        self.conn.commit() # save db
        c.close()

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
			now="datetime('now','localtime')"
			msg="insert into "+self.dbname+" values('%s','%s','%s','%s',%d,'%s',%s,%s,NULL,NULL,NULL)" % ( hash,dirname,self.mat,'new',0,'idle',now,now )
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

    def change_status(self,hash,count,st1,st2,t_send,t_update,t_recv):
        c=self.conn.cursor()
	now="datetime('now','localtime')"
	t_list=[]
	t_list.append("time_last=%s" %(now))
	if isinstance(t_send,str):
		t_list.append("time_send=%s" %(now))
        if isinstance(t_update,str):
		t_list.append("time_update=%s" %(now))
        if isinstance(t_recv,str):
		t_list.append("time_recv=%s" %(now))
	if isinstance(count,type(None)): 
        	s2=" where hash='%s'" %(hash)
	else:
		print "hash,count=",hash,count
		s2=" where hash='%s' and count=%d" %(hash,count)
        if len(st2)>0 and len(st1)>0 :
                s1=" set dbstatus='%s', execstatus='%s'" %(st1,st2)
        elif len(st2)>0 and len(st1)==0:
		s1=" set execstatus='%s'" %(st2) 
        elif len(st1)>0 and len(st2)==0:
		s1=" set dbstatus='%s'" %(st1) 

	for n in t_list:
		s1=s1+","+n
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

def read_file_content(filename):
        f=open(filename,"r")
        lines=f.readlines()
        f.close()
	for s in lines: 
		s1=s.split()
		return s1[0]


class Info:
	def __init__(self):
		self.dbname="sio2"
		self.senariodir="senario"
		self.inputdir="inputdata"
		self.temporarydir="calcdata"
		self.execstatusfile=".EXECSTATUS"
		self.mat="insulator1"
		self.dbfile="sio2data.sqlite3"
		self.mode=""
		error=0
		havecorrectoption=0
		print sys.argv
		for iarg in range(1,len(sys.argv)):
			n=sys.argv[iarg]
			if n=="-init":
				self.mode="init"
				havecorrectoption=1
			elif n=="-createdb":
				self.mode="createdb"
				havecorrectoption=1
			elif n=="-send":
				self.mode="send"
				havecorrectoption=1
			elif n=="-updatestatus":
				self.mode="updatestatus"
				havecorrectoption=1
			elif n=="-recv":
				self.mode="recv"
				havecorrectoption=1
			elif n=="-purge":
				self.mode="purge"
				havecorrectoption=1
			elif n=="-help":
				self.mode="help"
				havecorrectoption=1
			else:
				print "failed to understand option ",n
				error+=1
		if havecorrectoption==0 or self.mode=="help" or error>0:
				print sys.argv[0]," <options>"
				msg="""<options>
	-init
	-send
	-updatestatus
	-recv
	-purge
	-help"""
				print msg
				error+=1

		if error>0:
			sys.exit(10)

	def temporarypath(self,hash,count):
		return self.temporarydir+"/"+hash+"."+str(count)
	def execstatuspath(self,hash,count):
		return self.temporarypath(hash,count)+"/"+self.execstatusfile
	def resultpath(self,n):
		return n+".o"
				
			
class CombiInfo:
	def __init__(self,dbrow,info):
		# dbrow=DBrow, info=Info
		self.dbrow=dbrow
		self.info=info
	def temporarypath(self):
		return self.info.temporarydir+"/"+self.dbrow.hash+"."+str(self.dbrow.count)
	def temporarypath_with_count(self,count):
		return self.info.temporarydir+"/"+self.dbrow.hash+"."+str(count)
	def execstatuspath(self):
		return self.temporarypath()+"/"+self.info.execstatusfile
	def resultpath(self):
		return self.dbrow.path+".o"

	def file_copy_to_temporarypath(self):
		file_copy(self.dbrow.path,self.temporarypath())
	def file_copy_to_resultpath(self):
		file_copy(self.temporarypath(),self.resultpath())

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

elif info.mode=="createdb":
	db.createdb()

elif  info.mode=="send":
    result=db.get_list_status_is("new","idle")
    for n in result:
	print n.hash,n.path
	cinfo=CombiInfo(n,info)
        odir=cinfo.temporarypath()
	print "temporarydir=",odir
	cinfo.file_copy_to_temporarypath()
	db.change_status(n.hash,None,"submitted","idle",'now',None,None)
        make_file(cinfo.execstatuspath(),"idle")

	#input= n.path+"/"+datatype.input
        #senariofile=info.senariodir+"/"+n.mat+"_"+str(n.count)
        #print input,senariofile,odir
	#output=odir+"/"+datatype.input
	#r= apply_keyvalue (input,senariofile,output)
	#print output, " is changed."

elif info.mode=="updatestatus":
        filelist=yield_all_files(info.temporarydir)
	for s in  filelist:
		statusfile="/"+info.execstatusfile
		n=len(statusfile)
		s1=s[len(s)-n:len(s)]
		if s1==statusfile:
			print s
			execstatus=read_file_content(s)
			path=s[:len(s)-n]
			hashfile=path+"/"+".ID"
			hash=read_file_content(hashfile)
			count=int(path[-1:])
		        db.change_status(hash,count,"",execstatus,None,'now',None)

	sys.exit(10)


elif info.mode=="recv":
    result=db.get_list_status_is("submitted","finished")
    for n in result:
	cinfo=CombiInfo(n,info)
	result=QmasOutInfo(cinfo.temporarypath())
	if result.success()==1:
		print "OK",n.path,n.hash,n.count
		db.change_status(n.hash,None,"calculated","finished",None,None,'now')
		tdir=cinfo.temporarypath()
		path=cinfo.resultpath()
		cinfo.file_copy_to_resultpath()
	else:
		print "NG",n.path,n.hash,n.count
		db.add_count(n.hash)
		db.change_status(n.hash,None,"new","idle",None,None,'now')

elif info.mode=="purge":
    result=db.get_list_status_is("calculated","finished")
    for n in result:
	print n.hash
	cinfo=CombiInfo(n,info)
	for i in range(0,n.count+1):
		tdir=cinfo.temporarypath_with_count(i)
		print i,tdir
		if os.path.exists(tdir):
			shutil.rmtree(tdir)

#end
#-----------------------------------------------

