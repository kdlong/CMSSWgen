#!/bin/bash
###################################################################################
# EXO-Spring14dr
echo "_______________________________________________________________________________
Begining EXO-Spring14dr step
_______________________________________________________________________________" 
if [ -r CMSSW_7_0_6_patch1/src ] ; then 
    echo release CMSSW_7_0_6 already exists
else
    scram p CMSSW CMSSW_7_0_6_patch1
fi
cd CMSSW_7_0_6_patch1/src
eval `scram runtime -sh`

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

input_file=longer_test_nc.lhe_BG2-Fall13
file_out=${file}_Spring14dr_step1
scram b
cd ../../
cmsDriver.py step1 --filein file:$input_file.root --fileout file:$file_out.root --pileup_input "dbs:/MinBias_TuneA2MB_13TeV-pythia8/Fall13-POSTLS162_V1-v1/GEN-SIM" --mc --eventcontent RAWSIM --pileup AVE_20_BX_25ns --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --conditions POSTLS170_V5::All --step DIGI,L1,DIGI2RAW,HLT:2013,RAW2DIGI,L1Reco --magField 38T_PostLS1 --geometry DBExtendedPostLS1 --python_filename EXO-Spring14dr-00199_1_cfg.py --no_exec -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14dr-00199_rt.xml EXO-Spring14dr-00199_1_cfg.py || exit $? ; 
echo 73 events were ran 
grep "TotalEvents" EXO-Spring14dr-00199_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14dr-00199_rt.xml 
grep "PeakValueRss" EXO-Spring14dr-00199_rt.xml 
grep "AvgEventTime" EXO-Spring14dr-00199_rt.xml 
grep "AvgEventCPU" EXO-Spring14dr-00199_rt.xml 
grep "TotalJobCPU" EXO-Spring14dr-00199_rt.xml 

input_file=$file_out
file_out=${file}_Spring14dr_step2

cmsDriver.py step2 --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent AODSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --conditions POSTLS170_V5::All --step RAW2DIGI,L1Reco,RECO,EI --magField 38T_PostLS1 --geometry DBExtendedPostLS1 --python_filename EXO-Spring14dr-00199_2_cfg.py --no_exec -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14dr-00199_2_rt.xml EXO-Spring14dr-00199_2_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14dr-00199_2_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14dr-00199_2_rt.xml 
grep "PeakValueRss" EXO-Spring14dr-00199_2_rt.xml 
grep "AvgEventTime" EXO-Spring14dr-00199_2_rt.xml 
grep "AvgEventCPU" EXO-Spring14dr-00199_2_rt.xml 
grep "TotalJobCPU" EXO-Spring14dr-00199_2_rt.xml

####################################################################################
# EXO-Spring14miniaod
echo "_______________________________________________________________________________
Begining EXO-Spring14miniaod step
_______________________________________________________________________________" 

input_file=$file_out
file_out=${file}_Spring14MiniAOD

cd CMSSW_7_0_6_patch1/src
scram b
cd ../../
cmsDriver.py step1 --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions PLS170_V7AN1::All --step PAT --python_filename EXO-Spring14miniaod-00115_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14miniaod-00115_rt.xml EXO-Spring14miniaod-00115_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14miniaod-00115_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14miniaod-00115_rt.xml 
grep "PeakValueRss" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventTime" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventCPU" EXO-Spring14miniaod-00115_rt.xml 
grep "TotalJobCPU" EXO-Spring14miniaod-00115_rt.xml 
