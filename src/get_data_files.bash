#!/usr/bin/env bash
# utility to download historical data set from S3
waitForNProcs()
{
  #  procName set prior to calling e.g. procName=$xmlparser
  nprocs=$(pgrep -f $procName | wc -l)
  while [ $nprocs -gt $MAXPROCS ]; do
	sleep $SLEEPTIME
  	nprocs=$(pgrep -f $procName | wc -l)
  done
}
# Configure
SLEEPTIME=15   # seconds
MAXPROCS=8     # cores?
procName=curl
# to run different directory, update these
# Auto updated: 2013-08-01 03:47:32.150603
# AUTOPATH=.
AUTOPATH=/home/blehman/Gnip-Python-Historical-Utilities/src
#
export PYTHONPATH=${PYTHONPATH}:$AUTOPATH
mangler="$AUTOPATH/name_mangle.py"

if [ ! -e ./data ]; then
  mkdir ./data
fi

echo "Starting download at $(date)"
echo "Copying $(wc -l ./data_files.txt) files:"

while read fn
 do
 waitForNProcs
 filen=$(echo $fn | $mangler)
 echo "  copying file $fn to $filen..."
 if [ -n "$1" ]
    cmd="$procName $fn --create-dirs -o ./data/$1/$filen"
 else
    cmd="$procName $fn --create-dirs -o ./data/$filen"
 fi
 #echo $cmd
 exec $cmd &
done < ./data_files.txt

echo "Download completed at $(date)"
