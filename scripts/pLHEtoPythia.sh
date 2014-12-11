#!/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Enter the lhe file as a command line argument"
    exit
fi
working_dir=`pwd`
file=$1
input_file=$working_dir/$file
num_events=$2
release_path=/cms/kdlong/CMSSWgen/CMSSWrel
if [ ! -e $input_file ]; then
    echo Enter a valid lhe file name as a command line argument
    exit
fi
if [ -r $release_path/CMSSW_6_2_11/src ] ; then 
    echo release CMSSW_6_2_11 already exists
else
    cd $release_path
    scram p CMSSW CMSSW_6_2_11
fi
cd $release_path/CMSSW_6_2_11/src
eval `scram runtime -sh`

scram b
cd $working_dir
file_out=${file}_Fall13pLHE
echo "_______________________________________________________________________________
Begining EXO-Fall13pLHE step
_______________________________________________________________________________" 

cmsDriver.py step1 --filein file:$file  --fileout file:$file_out.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE --python_filename EXO-Fall13pLHE-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100 || exit $? ; 
cmsRun -e -j EXO-Fall13pLHE-00001_rt.xml EXO-Fall13pLHE-00001_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Fall13pLHE-00001_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Fall13pLHE-00001_rt.xml 
grep "PeakValueRss" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventTime" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventCPU" EXO-Fall13pLHE-00001_rt.xml 
grep "TotalJobCPU" EXO-Fall13pLHE-00001_rt.xml 
####################################################################################
# EXO-Fall13-00131
echo "_______________________________________________________________________________
Begining EXO-Fall13 step
_______________________________________________________________________________" 
if [ -r $release_path/CMSSW_6_2_11/src ] ; then 
    echo release CMSSW_6_2_11 already exists
else
    cd $release_path
    scram p CMSSW CMSSW_6_2_11
fi
cd $release_path/CMSSW_6_2_11/src
curl  -s https://raw.githubusercontent.com/cms-sw/genproductions/5edbeb36a9f2510e6e0932fa74bc86bcf3dc6be0/python/ThirteenTeV/DYJetsToEEMuMu_M-Binned_13TeV-madgraph_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/DYJetsToEEMuMu_M-Binned_13TeV-madgraph_cff.py 
export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

scram b
cd $working_dir
input_file=$file_out
file_out=${file}_Fall13
cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/DYJetsToEEMuMu_M-Binned_13TeV-madgraph_cff.py --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --conditions POSTLS162_V1::All --step GEN,SIM --magField 38T_PostLS1 --geometry Extended2015 --python_filename EXO-Fall13-00131_1_cfg.py --no_exec -n -1 || exit $? ; 
cmsRun -e -j EXO-Fall13-00131_rt.xml EXO-Fall13-00131_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Fall13-00131_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Fall13-00131_rt.xml 
grep "PeakValueRss" EXO-Fall13-00131_rt.xml 
grep "AvgEventTime" EXO-Fall13-00131_rt.xml 
grep "AvgEventCPU" EXO-Fall13-00131_rt.xml 
grep "TotalJobCPU" EXO-Fall13-00131_rt.xml

