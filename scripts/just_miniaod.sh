#!/bin/bash

####################################################################################
# EXO-Spring14miniaod
echo "_______________________________________________________________________________
Begining EXO-Spring14miniaod step
_______________________________________________________________________________" 
if [ -r CMSSW_7_0_6_patch1/src ] ; then 
 echo release CMSSW_7_0_6_patch1 already exists
else
scram p CMSSW CMSSW_7_0_6_patch1
fi
cd CMSSW_7_0_6_patch1/src
eval `scram runtime -sh`

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert
scram b
cd ../../
input_file=$1_Spring14dr_step2
file_out=${file}_Spring14MiniAOD
cmsDriver.py step1 --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions PLS170_V7AN1::All --step PAT --python_filename EXO-Spring14miniaod-00115_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14miniaod-00115_rt.xml EXO-Spring14miniaod-00115_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14miniaod-00115_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14miniaod-00115_rt.xml 
grep "PeakValueRss" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventTime" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventCPU" EXO-Spring14miniaod-00115_rt.xml 
grep "TotalJobCPU" EXO-Spring14miniaod-00115_rt.xml 
