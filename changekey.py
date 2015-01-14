import sys
import string
import re

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
