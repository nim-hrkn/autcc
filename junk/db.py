import sys
import sqlite3
import os


# create table calc_sio2(hash,dirname);

class DB:
    def __init__(self,conn,dbname,mat):
		self.conn=conn
		self.dbname=dbname
		self.mat=mat
		self.input="input_scf.txt"
		self.output="output_scf.txt"

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
	print result
	#for row in result:
	#	print row
	c.close()
	return result

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

#-----------------------------------------------
#begin

filelist=yield_PathList('data')
for n in filelist:
	print n

dbname='sio2'
mat="senario/insulator1_0"

conn=sqlite3.connect('sio2data.sqlite3')
db=DB(conn,dbname,mat)
db.add(filelist)

hash="4f3e95d24e39c923136f0e8f25069e4bc982a4fe"
db.add_count(hash)

result=db.get_list_status_is("new","idle")
for n in result:
	print n

#end
#-----------------------------------------------

