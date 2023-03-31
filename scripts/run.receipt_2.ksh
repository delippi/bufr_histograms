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

source ./config.ksh
tstamp=`date -u +%Y%m%d%H%M`
date=$date1
base=`pwd`
cd $base
mkdir -p sh

cat << EOF > ./sh/receipt_2.sh
#!/bin/bash
#SBATCH -A fv3-cam
#SBATCH -N
#SBATCH -p orion
#SBATCH -q batch
#SBATCH -t 00:30:00
#SBATCH -J receipt
#SBATCH -e receipt.log
#SBATCH -o receipt.log
cd ${base}/receipt
python ../../src/receipt_2.py $date1 $date2 $tstamp $CDUMP $bufr 
EOF
mkdir -p receipt
cd receipt
#sbatch ../sh/receipt_2.sh
sh ../sh/receipt_2.sh #could be memory intensive???
cd $base

