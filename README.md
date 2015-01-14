data handler for huge number of calculatins

program:
prog=db9.py 

condition:
python v3  and sqliete3 and its python interface is necessary. 

Usage:
0. make .ID  that is sha1 hash  in the directory that contains data to make input files. 
1. $prog -createdb        count=0
2. $prog -init            status=('init",'idle')
  search sub directories that have .ID
3. $prog -send            status=('submitted','idle'), make input data with material_kind and count
 send files to calculation servers and add a control file to submit and submit them. 
 $prog doesn't care about the result and status of the calculation servers.

 file_status=('finished') if the job is really finished
 receive files from the calculation servers 

4. $prog -updatestatus    status=('submitted','finished'), reflect file_status from the files to the database. 
5. $prog -recv            status=('calculated','finished') or (('new','idle') and  count++)
goto 3 if not (calculted","finished")

You can purge unnecessary files anytime
$prog -purge 

Check what you did
$prog -history 

Check completed/all numbers of files
$prog -status


----------------------------------

                self.dbname="sio2"  # create table sio2 (...)
                self.senariodir="senario" # not used
                self.inputdir=["inputdata"] # input directories
                self.temporarydir="calcdata" # output directory
                self.execstatusfile=".EXECSTATUS" # status file in the file side. 
                self.mat="insulator1"          # material kind
                self.dbfile="sio2data.sqlite3"   # database file 



----------------------------------
How to make .ID

hash.py string > path_of_the_file/.ID

"string" is used to make sha1 hash. I recommend to use your_name+hostname+directory_full_path as long as possible to distinguish them. 


