#!/usr/bin/env python 
import sys
import os
import re
import shutil
import string

from XsfInfo import XsfInInfo
from keyvalue import keyvalueList, change_key

qmas_psfile=[ " ",
"h","he",
"li","be","b","c","n","08lda2","f","ne",
"na","mg","al","14lda2","p","s","cl","ar" ]

class QmasInputGen:
    def __init__(self,xsf):
        msg=""
	msg+="""
file_begin
!
! file
    title = material_____
    add = scf
unit = 1 # set it to ang !{1:Ang, 2:Bohr}
lattice_type = 2 #vectors
lattice_list
"""
	# lattice
	for j in range(3):
	    msg+="( %s %s %s )\n" % ( xsf.pvec[0][j], xsf.pvec[1][j], xsf.pvec[2][j] )
	msg+="atomic_pos = 2 #absolute\n"
	# number_atom
	msg+="number_atom = "+str(xsf.natom)+"\n"
        msg+"atom_list\n"	
	# atoms
	for j in range(xsf.natom):
	    msg+=" %s %s %s %s %i 0\n" % ( xsf.namepos[j][0],xsf.namepos[j][1],xsf.namepos[j][2], xsf.namepos[j][3],xsf.namepos[j][4]+1 )
        n= len(xsf.specie_list)
        msg +="number_element = "+str(n) +"\n"
	msg +="element_list\n"
	for j in range(n):
		msg+=xsf.specie_list[j][0]+" "+qmas_psfile[xsf.specie_list[j][1]]+"\n"
	msg+="""
! symmetry
  space_group = gen

! parallelization
    mpi_type = 1 !{1:k-parallel, 2:band-parallel}
    conv_type = 1 !{1:Davidson, 2:Kosugi}
    nb_divide = 2 ! divide number of Kosugi argo.
! for scf
k_point_type = 1
nk_v = 4 4 4
!sk_v = -4 -4 -4
!ek_v = 2 2 2
! for_SCF
cutoff_wf = 40 Ry
    exc_type = 1
    number_spin = 1
    number_max_iteration = 100
    continue_iteration = 0
    number_unoccupied = 15
    number_pre_iteration = 0
    charge_state = 0
    number_population = -999
    kerker_apre = 0.4e0
    kerker_g0sq = 0.5e0
    gauss_delta = 0.025e0
    sw_to_pulay = 10
    sw_to_rmmdiis = 500
! atomic_relaxation
    number_max_relax = 0
    continue_relax = 0
!
! convergence
    th_charge = 1e-8
    th_force = 5.e-5
    th_stress = 5.e-7
! input file

    input_charge = 0
    input_occupancy = 0
    input_atomic_pos = 0
    input_vector = 0
    input_g = 0
    charge_fixed = 0
    set_k_point = 0
! stress
    cal_stress = 0
    number_ref_pulay = 0
    external_stress_v = 0.e0, 0.e0, 0.e0
! md
    md_mode = -5
    time_step = 150.d0
    lattice_mass = 1.d4
    filtering_projector = 0
    cal_in_realspace = 0
!
file_end"""
    	self.inputcontent= msg

    def apply_senario(self,senariofile):
        kv=keyvalueList(senariofile)
	lines=self.inputcontent.split("\n")
	lines2=[]
	for n in lines:
		lines2.append(n.rstrip())
	lines=lines2
        lines=change_key(lines,kv)
	return lines
        #for x in lines:
    	#    print  x

if __name__ == "__main__":

    xsf=XsfInInfo("/home/kino/kino/work/autcc/inputdata/Fdd2/xsf_2_i0041")

    x=QmasInputGen(xsf)

    lines=x.apply_senario("/home/kino/kino/work/autcc/senario/metal1_1")

    for x in lines:
    	print  x

