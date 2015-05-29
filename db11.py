#!/usr/bin/env python 
import sys
import sqlite3
import os
import re
import shutil

DBNAME_define      = "materialdata"
SENARIODIR_define  = "senario"
INPUTDIR_define    = "inputdata"
TEMPORARYDIR_define= "calcdata"
MATERIALKIND_define= "metal1"
DBFILE_define      = "rundata.sqlite3"

from QmasOutInfo import QmasOutInfo,  QmasInInfo
#---------------------

debug_print=0

#---------------

#---------------------------------

def single_quote(s):
	return "'"+s+"'"

db_tables=["hash","path","material",\
"dbstatus","count", "execstatus",\
"time_last","time_init", "time_send", "time_recv","time_update"]

class DBdef:
	def __init__(self,hash=None,path=None,material=None,dbstatus=None,count=None,\
execstatus=None,time_last=None,time_init=None,time_send=None,time_recv=None,time_update=None):
		self.namelist=[]
		self.valuelist=[]
		self.msglist=[]
                now="datetime('now','localtime')"
		if not isinstance(hash,type(None)):
			self.hash=hash
			self.msglist.append("hash='%s'" %(hash) )
			self.namelist.append("hash"); self.valuelist.append(single_quote(hash))
		if not isinstance(path,type(None)):
			self.path=path
			self.msglist.append("path='%s'" %(path) )
			self.namelist.append("path"); self.valuelist.append(single_quote(path))
		if not isinstance(material,type(None)):
			self.material=material
			self.msglist.append("material='%s'" %(material) )
			self.namelist.append("material"); self.valuelist.append(single_quote(material))
		if not isinstance(dbstatus,type(None)):
			self.dbstatus=dbstatus
			self.msglist.append("dbstatus='%s'" %(dbstatus) )
			self.namelist.append("dbstatus"); self.valuelist.append(single_quote(dbstatus))
		if not isinstance(count,type(None)):
			self.count=count
			self.msglist.append("count=%d" %(count) )
			self.namelist.append("count"); self.valuelist.append(str(count))
		if not isinstance(execstatus,type(None)):
			self.execstatus=execstatus
			self.msglist.append("execstatus='%s'" %(execstatus) )
			self.namelist.append("execstatus"); self.valuelist.append(single_quote(execstatus))
		if not isinstance(time_last,type(None)):
			if time_last=="now":
				time_last=now
			self.time_last=time_last
			self.msglist.append("time_last=%s" %(time_last) )
			self.namelist.append("time_last"); self.valuelist.append(time_last)
		if not isinstance(time_init,type(None)):
			if time_init=="now":
				time_init=now
			self.time_init=time_init
			self.msglist.append("time_init=%s" %(time_init) )
			self.namelist.append("time_init"); self.valuelist.append(time_init)
		if not isinstance(time_send,type(None)):
			if time_send=="now":
				time_send=now
			self.time_send=time_send
			self.msglist.append("time_send=%s" %(time_send) )
			self.namelist.append("time_send"); self.valuelist.append(time_send)
		if not isinstance(time_recv,type(None)):
			if time_recv=="now":
				time_recv=now
			self.time_recv=time_recv
			self.msglist.append("time_recv=%s" %(time_recv) )
			self.namelist.append("time_recv"); self.valuelist.append(time_recv)
		if not isinstance(time_update,type(None)):
			if time_update=="now":
				time_update=now
			self.time_update=time_update
			self.msglist.append("time_update=%s" %(time_update) )
			self.namelist.append("time_update"); self.valuelist.append(time_update)
	def len(self):
		return len(self.tables)
	def name_value_str(self,add=","):
		msg=""
		for i in range(0,len(self.msglist)):
			if i==0:
				pre=""
			else:
				pre=add
			msg = msg + pre+ self.msglist[i]
		return msg
	def name_str(self,add=","):
		msg=""
		for i in range(0,len(self.namelist)):
			if i==0:
				pre=""
			else:
				pre=add
			msg = msg + pre+ self.namelist[i]
		return msg
	def value_str(self,add=","):
		msg=""
		for i in range(0,len(self.valuelist)):
			if i==0:
				pre=""
			else:
				pre=add
			msg = msg + pre+ self.valuelist[i]
		return msg


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
		self.tables=db_tables

    def createdb(self):
        global debug_print
        c = self.conn.cursor()
	msg="create table batchcount (count)"
	try:
		c.execute(msg)
	except sqlite3.Error, e:
                print "Error in sql,", e
		print "if message='table batchcount already exists', probably you have done this action already. If so, Ingore it"
		return 

	msg="insert into batchcount values (0)"
	try:
		c.execute(msg)	
        except sqlite3.Error, e:
                print "Serious Error in sql", e
		print "failed to set count=0 in batchcount" 
                return

	msg="create table history (cmd,time)"
        try:
                c.execute(msg)
        except sqlite3.Error, e:
                print "Error in sql,", e
                print "if message='table batchcount already exists', probably you have done this action already. If so, Ingore it"
                return

	msg="create table "+self.dbname+" ("
	for n in range(0,len(self.tables)):
		s=self.tables[n] 
		if n!=0:
			add=","
		else:
			add=""
		msg = msg + add + s 
	msg = msg + ")"
	if debug_print>0:
		print msg
	#self.conn.enable_callback_tracebacks(False) # test
	try:
        	c.execute(msg)
	except sqlite3.Error, e:
		print "Error in sql", e
		print "if message='table "+self.dbname+" already exists', probably you have done this action already. If so, Ingore it"

        self.conn.commit() # save db
        c.close()

    def update_history(self,msg):
	global debug_print
	c = self.conn.cursor()
	msg="insert into history values ('"+msg+"',datetime('now','localtime'))"
	if debug_print>0:
		print msg
	try:
		c.execute(msg)
	except sqlite3.Error, e:
                print "Error in sql", e
		sys.exit(10)

	self.conn.commit()
	c.close()

    def show_history(self):
	global debug_print
	c = self.conn.cursor()
	msg="select * from history order by time"
	if debug_print>0:
		print msg
	c.execute(msg)
	print "history"
	result=c.fetchall()
	for row in result:
		print row[0],"|",row[1]

	

    def show_status(self):
	c = self.conn.cursor()
	msg="select count(*) from "+self.dbname
	c.execute(msg)
	result=c.fetchall()
	all=0
        for row in result:
                all=row[0]
	s=DBdef(dbstatus="calculated", execstatus="finished")
	msg="select count(*) from "+ self.dbname + " where "+ s.name_value_str(" and ")
	c.execute(msg)
	result=c.fetchall()
        calculated=0
        for row in result:
                calculated=row[0]
	print "calculated/all= ",calculated,"/",all

	msg="select max(count) from "+ self.dbname
	c.execute(msg)
        result=c.fetchall()
        m=0
        for row in result:
                m=row[0]
	print "max(count)=",m

	

    def add(self,filelist):
	global debug_print
	c = self.conn.cursor()
	# n0 = hash, n1=dirname
	for n  in filelist:
		hash=n.hash
		dirname=n.path
		msg="select count(*) from "+self.dbname+" where path='%s'" %(dirname)
		c.execute(msg)
		result=c.fetchall()
		found=0
		for row in result:
			found=row[0]
		if found==1:
			print "data exists, do nothing for "+dirname
		else:
			dbrow=DBdef(hash=hash,path=dirname,material=self.mat,dbstatus='new',execstatus='idle',time_last='now', time_init='now',count=0)
			msg = "insert into "+self.dbname+ " ( "+dbrow.name_str() +" ) values ( "+ dbrow.value_str() +" ) "
			if debug_print>0:
				print msg
			c.execute(msg)

	self.conn.commit() # save db 
	c.close()

    def add_count(self, hash):
	global debug_print
	c=self.conn.cursor()
	msg="select count from "+self.dbname+" where hash='%s'" %(hash)
	c.execute(msg)
	result=c.fetchall()
	if debug_print>0:
		print "result=",result
	if len(result)==0:
		print "erorr: failed to find hash="+hash+" in DB"
		print msg
		exit(10)
	for row in result:
		count=row[0]
	count+=1
	msg="update "+self.dbname+" set count="+str(count)+" where hash='%s' " % (hash)
	if debug_print>0:
		print msg
	c.execute(msg)
	self.conn.commit()
	c.close()

    def get_list_status_is(self,st1,st2):
	global debug_print
	dbwhere=DBdef(dbstatus=st1,execstatus=st2)
	c=self.conn.cursor()
	s=dbwhere.name_value_str(" and ")
	msg="select * from "+self.dbname+" where "+s
	#if len(st2)>0 and len(st1)>0 :
	#	msg="select * from "+self.dbname+" where dbstatus='%s' and execstatus='%s'" %(st1,st2)
	#elif len(st2)>0 and len(st1)==0:
	#	msg="select * from "+self.dbname+" where execstatus='%s'" %(st2)
	#elif len(st1)>0 and len(st2)==0:
	#	msg="select * from "+self.dbname+" where dbstatus='%s'" %(st1)

	if debug_print>0:
		print msg
	c.execute(msg)
	result=c.fetchall()
	#print result
	r=[]
	for row in result:
		r.append(DBrow(row))
	c.close()
	return r

    def change_status(self,dbrow,dbwhere):
	global debug_print
        c=self.conn.cursor()
	s1=dbrow.name_value_str()
	s2=dbwhere.name_value_str(" and ")
        msg="update "+self.dbname+" set " + s1+" where " + s2
	if debug_print>0:
		print "msg=",msg
        c.execute(msg)
	self.conn.commit()
        c.close()


def yield_all_files(directory):
    for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
            yield os.path.join(root, file)

#def get_filelist(filelist):
#    f=open(filelist,"r")
#    lines=f.readlines()
#    f.close()
#    filelist=[]
#    for n in lines:
#	[path,hash]=n.split()
#	filelist.append([hash,path,'sio2'])
#    return filelist

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

#def get_liststatus(filelist):
#	for [path,hash,mat] in filelist:
#		r=get_status(path+"/output_scf.txt")
#		print path,r

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
	global debug_print
	f=os.path.exists(t)
	if f:
		print t, "exists, skip it"
		return 1
	cmd="cp -RP "+s+" "+t
	if debug_print>0:
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
		global debug_print
		self.dbname=DBNAME_define  # "sio2"
		self.senariodir=SENARIODIR_define #"senario"
		self.inputdir=[INPUTDIR_define ] #["inputdata"]
		self.temporarydir=TEMPORARYDIR_define #"calcdata"
		self.execstatusfile=".EXECSTATUS"
		self.mat=MATERIALKIND_define #"metal1"
		self.dbfile=DBFILE_define # "rundata.sqlite3"
		self.mode=""
		error=0
		havemodeoption=0
		if debug_print>0:
			print sys.argv
		self.cmd=""
		self.commandline=""
		for  s in sys.argv:
			self.commandline= self.commandline + " " + s
		for iarg in range(1,len(sys.argv)):
			n=sys.argv[iarg]
			if n=="-init":
				self.mode="init"
				havemodeoption=1
			elif n=="-createdb":
				self.mode="createdb"
				havemodeoption=1
			elif n=="-status":
				self.mode="status"
				havemodeoption=1
			elif n=="-send":
				self.mode="send"
				havemodeoption=1
			elif n=="-updatestatus":
				self.mode="updatestatus"
				havemodeoption=1
			elif n=="-recv":
				self.mode="recv"
				havemodeoption=1
			elif n=="-purge":
				self.mode="purge"
				havemodeoption=1
			elif n=="-history":
				self.mode="history"
				havemodeoption=1
			elif n=="-help":
				self.mode="help"
				havemodeoption=1
			elif n=="-debug":
				debug_print=1
			else:
				print "failed to understand option ",n
				error+=1
		if havemodeoption==0 or self.mode=="help" or error>0:
				print sys.argv[0]," <options>"
				msg="""<options>
	-createdb
	-init
	-send
	-updatestatus
	-recv
	-purge

	-status
	-history
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

if not info.mode in ("createdb","history"):
    if debug_print>0:
	print "commandline=",info.commandline
    db.update_history(info.commandline)


if info.mode=="init":
	filelist=[]
	for n in info.inputdir:
		filelist.extend(yield_PathList(n))
	db.add(filelist)

elif info.mode=="createdb":
	db.createdb()

elif info.mode=="send":
    result=db.get_list_status_is("new","idle")
    if len(result)==0:
	print "nothing to do"
    else:
	print "make",len(result),"directories"
    for n in result:
	if debug_print>0:
		print n.hash,n.path
	cinfo=CombiInfo(n,info)
        odir=cinfo.temporarypath()
	if debug_print>0:
		print "temporarydir=",odir

	cinfo.file_copy_to_temporarypath()

	#dbrow=DBdef(dbstatus='submitted',execstatus='idle',time_send='now',time_last="now")
	#dbwhere=DBdef(hash=n.hash)
	#db.change_status(dbrow,dbwhere)
        #make_file(cinfo.execstatuspath(),"idle")

        #inputfile="input_scf.txt"
	#input= n.path+"/"+inputfile
        senariofile=info.senariodir+"/"+n.mat+"_"+str(n.count)
	#output=odir+"/"+inputfile
        #print "input=",input,"senario=",senariofile,"output=",output
	#r= apply_keyvalue (input,senariofile,output)
	#print output, " is changed."
	changefunc=QmasInInfo()
	changefunc.apply(n.path,senariofile,odir)

        dbrow=DBdef(dbstatus='submitted',execstatus='idle',time_send='now',time_last="now")
        dbwhere=DBdef(hash=n.hash)
        db.change_status(dbrow,dbwhere)
        make_file(cinfo.execstatuspath(),"idle")


elif info.mode=="updatestatus":
        filelist=yield_all_files(info.temporarydir)
	if isinstance(filelist,type(None)):
		print "nothing to do"
	else:
	    for s in  filelist:
		statusfile="/"+info.execstatusfile
		n=len(statusfile)
		s1=s[len(s)-n:len(s)]
		if s1==statusfile:
			if debug_print>0:
				print "checking ",s
			execstatus=read_file_content(s)
			path=s[:len(s)-n]
			hashfile=path+"/"+".ID"
			hash=read_file_content(hashfile)
			count=int(path[-1:])
			dbrow=DBdef(execstatus=execstatus,time_update='now',time_last="now")
			dbwhere=DBdef(hash=hash,count=count)
		        db.change_status(dbrow,dbwhere)



elif info.mode=="recv":
    result=db.get_list_status_is("submitted","finished")
    if len(result)==0:
	print "nothing to do"
    else:
	print "process ",len(result),"directories"
    for n in result:
	cinfo=CombiInfo(n,info)
	result=QmasOutInfo(cinfo.temporarypath())
	if result.success()==1:
		print "OK",n.path,n.hash,n.count
		tdir=cinfo.temporarypath()
		path=cinfo.resultpath()
		cinfo.file_copy_to_resultpath()
		dbrow=DBdef(dbstatus="calculated",execstatus="finished",time_recv="now",time_last="now")
		dbwhere=DBdef(hash=n.hash)
		db.change_status(dbrow,dbwhere)
	else:
		print "NG",n.path,n.hash,n.count
		db.add_count(n.hash)
		dbrow=DBdef(dbstatus="new",execstatus="idle",time_recv="now",time_last="now")
		dbwhere=DBdef(hash=n.hash)
		db.change_status(dbrow,dbwhere)

elif info.mode=="purge":
    result=db.get_list_status_is("calculated","finished")
    if len(result)==0:
	print "nothing to do"
    for n in result:
	#print n.hash
	cinfo=CombiInfo(n,info)
	for i in range(0,n.count+1):
		tdir=cinfo.temporarypath_with_count(i)
		if debug_print>0:
			print "try deleting ",tdir
		if os.path.exists(tdir):
			shutil.rmtree(tdir)

elif info.mode=="status":
	db.show_status()

elif info.mode=="history":
	db.show_history()

print info.mode,"done"
sys.exit(0)
#end
#-----------------------------------------------

