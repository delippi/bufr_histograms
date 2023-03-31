#!/bin/ksh

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
#date1="2020032200"; date2="2020032200"
source ./config.ksh
tstamp=`date -u +%Y%m%d%H%M`
date=$date1
base=`pwd`
cd $base
mkdir -p sh
cat << EOF > ./sh/latency_3.sh
#!/bin/bash
#SBATCH -t 00:30:00
##SBATCH -A gsienkf
#SBATCH -A fv3-cam
#SBATCH -N 1    
#SBATCH -J latency
#SBATCH -e latency.log
#SBATCH -o latency.log
cd ${base}/latency
python ../../src/latency_3.py $date1 $date2 $tstamp
EOF
mkdir -p latency
cd latency
#sbatch ../sh/latency_3.sh
sh ../sh/latency_3.sh #could be memory intensive???
cd $base

