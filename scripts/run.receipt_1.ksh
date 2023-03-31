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

source ./config.ksh
if [[ $CDUMP == "GFS" ]]; then
   hrly=6
elif [[ $CDUMP == "OW" ]]; then
   hrly=1
fi

date=$date1
base=`pwd`
cd $base
mkdir -p sh

while [[ $date -le $date2 ]]; do
  for b in $bufr; do
    walltime="00:30:00"
    if [[ $b == "avcsam" ]]; then
      walltime="04:00:00"
    elif [[ $b == "avcspm" ]]; then
      walltime="02:00:00"
  fi
cat << EOF > sh/receipt_${b}_${date}.sh
#!/bin/bash
#SBATCH -A fv3-cam
#SBATCH -N 1    
#SBATCH -p orion
#SBATCH -q batch
#SBATCH -t $walltime
#SBATCH -J receipt_${b}_${date} 
#SBATCH -e receipt_${b}_${date}.log
#SBATCH -o receipt_${b}_${date}.log
python ../../src/receipt_1.py $date $date $CDUMP $b
EOF
  mkdir -p receipt
  cd receipt
  #echo $date $b
  #sh ../sh/receipt_${b}_${date}.sh
  sbatch ../sh/receipt_${b}_${date}.sh
  cd $base
  done #for b in bufr
  date=`$ndate $date +$hrly`

  #let's not submit too many jobs...
  njobs=$((`squeue -u $USER | wc -l` - 1)) #get number of batch jobs for user
  while [[ $njobs -ge 25 ]]; do
     echo sleep 60 @ `date` 
     sleep 60 #wait some period for jobs to finish
     njobs=$((`squeue -u $USER | wc -l` - 1)) #get number of batch jobs for user and try again
  done

done #while date -le date2

