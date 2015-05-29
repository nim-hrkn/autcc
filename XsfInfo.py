#!/usr/bin/env python 
import sys
import os
import re
import shutil

xsf_inputfile_define="3.xsf"
qmas_inputfile_define="3.xsf"

periodictable_species_names=[ " ",
 "H","He",
"Li","Be","B","C","N","O","F","Ne",
"Na","Mg","Al","Si","P","S","Cl","Ar" ]

class Periodic_table_name:
    def __init__(self):
	x=0
    def Z(self,name):
        flag=1
	try:
	    i=int(name)
	except:
	    flag=0
        if flag==1:
	    return i
	for i in range(len(periodictable_species_names)):
		if name==periodictable_species_names(i):
			return i
	print "failed to find Z of the element",name
	sys.exit(10)

class XsfInInfo:
    def __init__(self,path):
	self.inputfile=xsf_inputfile_define
	filename=path+"/"+self.inputfile
	f=open(filename,"r")
	lin=f.readlines()
	f.close()
	n=len(lin) 
	i=0
	while i<n:
		s=lin[i]
		s2=s.split()
		if s2[0]=='CRYSTAL':
	            start=1
		    i+=1
		    break
		i+=1
        if start>0:
	    while i<n:
		s=lin[i]; s2=s.split()
		if s2[0]=='PRIMVEC':
	          self.pvec=[[0 for j in range(3)] for k in range(3)]
		  for j in range(0,3):
		    i+=1; s=lin[i]; s2=s.split()
		    for k in range(0,3):
		      self.pvec[j][k]=s2[k]
		elif s2[0]=="PRIMCOORD":
		    i+=1; s= lin[i]; s2=s.split()
		    self.natom=int(s2[0])
	            self.namepos=[[" ",0,0,0] for k in range(0,self.natom)]
		    for j in range(0,self.natom) :  
			i+=1; s=lin[i]; s2=s.split()
			for k in range(0,4):
			    self.namepos[j][k]=s2[k]
		    break
		i+=1

       
      # specie?
        x=[]
        for s in self.namepos:
	  	x.append(s[0])
        y=list(set(x))
	self.specie_list=[]
        pname=Periodic_table_name()
        for x in y:
		z=pname.Z(x)
		self.specie_list.append([x,z])


      # specie -> atom_name
        for i in range(len(self.namepos)):
	  for j in range(len(self.specie_list)):
	      if (self.namepos[i][0]==self.specie_list[j][0]):
		self.namepos[i].append(j)

    def show(self):
        print "primitive vector"
	for j in range(0,3):
	    print j,self.pvec[j][0],self.pvec[j][1],self.pvec[j][2]	
	print "atoms",self.natom
	for j in range(0,self.natom):
	    print j,self.namepos[j][0],self.namepos[j][1],self.namepos[j][2],self.namepos[j][3],self.namepos[j][4]
	print "species",len(self.specie_list)
	for j in range(0,len(self.specie_list)):
	    print j, self.specie_list[j]

# main #

if __name__ == "__main__":

    xsf=XsfInInfo("/home2/kino2/kino/work/autcc/inputdata/Fdd2/xsf_2_i0041")
    xsf.show()

