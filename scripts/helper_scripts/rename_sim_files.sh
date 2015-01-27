#!/bin/bash
#
# Renames simulation files from simultion steps to avoid excessively
# long file names
#
# Kenneth Long
# 01/22/2015

if [ "$#" -ne 4 ]; then
    echo "requires 4 command line arguments:
        rename_sim_files <job_name> <username> <current step name> <previous step name>"
    exit
fi

job_name=$1
user_name=$2
current_step=$3
append=$4

hdfs_path=/hdfs/store/user/$user_name/$job_name$append

if [ -d "$hdfs_path" ]; then
    cd $hdfs_path
else
    echo $hdfs_path does not exit. Job failed
    exit
fi
for f in *.root; do
    mv $f `echo $f | sed "s/$append//"`; 
done

