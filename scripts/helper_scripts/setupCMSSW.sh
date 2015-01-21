#!/bin/bash
#
# Setup CMSSW release
#
# Kenneth Long
# 12/12/2014

if [ "$#" -ne 3 ]; then
    echo "Enter the directory where your CMSSW releases should be stored,
          the number of the release you would like to setup (X_X_X), and architecture
          it requires"
    exit
fi

working_dir=`pwd`
release_path=$1
release_num=$2
arch=$3

export SCRAM_ARCH=$arch
if [ -r $release_path/CMSSW_$release_num/src ] ; then 
    echo release CMSSW_$release_num already exists
else
    cd $release_path
    scram p CMSSW CMSSW_$release_num
fi

cd $release_path/CMSSW_$release_num/src
eval `scramv1 runtime -sh`
scram b
cd $working_dir

