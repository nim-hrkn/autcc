#for n in */nk?/stress*/rand-data/xsf_2_i*
for n in *
do 
if [ -d $n ]; then
echo $n;
(cd $n; 
echo "PWD=" `pwd`
cp ~/tmp/sample/* .
gawk -f ~/QMAS/PS/linkps.awk input_scf.txt
qsub runD.sh
)
fi
done
