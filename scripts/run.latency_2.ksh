#!/bin/ksh
export ndate=/home/dlippi/bin/ndate
bufr="" #initialize empty string
file="./bufr.txt" #file to read bufr file types from use "#" to comment them out
count=0
while IFS= read -r line; do #while loop to read file
  if [[ $line =~ ^"#" ]]; then #skipping lines starting with "#"
#     echo "skipping $line" 
     (( count = count + 1 ))
  else
  bufr="$bufr $line" #append to bufr string if doesn't start with #
  fi
done <"$file"
echo "processing: $bufr"
#bufr="1bamua 1bhrs4 1bmhs adpsfc adpupa aircar aircft airsev amsr2 ascatt 
#ascatw atms atmsdb atovs avcsam avcspm bathy cris crisdb esamua esatms 
#escris eshrs3 esiasi esmhs geoimr goesfv gome gpsipw gpsro iasidb mtiasi 
#omi osbuv8 proflr rassda saphir satwnd sevasr sevcsr sfcshp ssmisu status 
#tesac trkob vadwnd prepbufr prepbufr.acft_profiles"
#bufr="prepbufr"
#date1="2020032100"; date2="2020032200"
source ./config.ksh

date=$date1
base=`pwd`
cd $base
mkdir -p sh

while [[ $date -le $date2 ]]; do
cat << EOF > sh/latency_2_${date}.sh
#!/bin/bash
#SBATCH -A fv3-cam
#SBATCH -N 1    
#SBATCH -p orion
#SBATCH -q batch
#SBATCH -t 00:30:00
#SBATCH -J latency_2_${date} 
#SBATCH -e latency_2_${date}.log
#SBATCH -o latency_2_${date}.log
python ../../src/latency_2.py $date $date $bufr
#rm -f latency_2_${date}.err latency_2_${date}.out
rm -f latency_2_${date}.log
EOF
mkdir -p latency
cd latency
#echo $date $b
sh ../sh/latency_2_${date}.sh
#sbatch ../sh/latency_2_${date}.sh
cd $base
date=`$ndate $date +6`
done
sleep 00

