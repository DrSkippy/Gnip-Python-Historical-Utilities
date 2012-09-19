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
AUTOPATH=.
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
 cmd="$procName $fn --create-dirs -o ./data/$filen"
 #echo $cmd
 exec $cmd &
done < ./data_files.txt

echo "Download completed at $(date)"
