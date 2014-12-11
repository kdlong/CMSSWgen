#!/bin/bash

# Procedure for running pp > w+l+l- > l+vll+l- MadGraph LHE files through full CMSSW
# generation. Compiled by Kenneth Long
#
# pLHE to EDM and Gen Sim via B2G-chain_Fall13_flowF13PU20bx25-00001 from 
# https://cms-pdmv.cern.ch/mcm/chained_requests?prepid=B2G-chain_Fall13_flowF13PU20bx25-00001&page=0&shown=15 
#

if [ "$#" -ne 2 ]; then
    echo "Enter the lhe file and number of events as a command line argument"
    exit
fi

working_dir=`pwd`
file=$1
input_file=$working_dir/$file
num_events=$2
release_path=/cms/kdlong/CMSSWgen/CMSSWrel
if [ ! -e ./$file ]; then
    echo Enter a valid lhe file name as a command line argument
    exit
fi
export SCRAM_ARCH=slc5_amd64_gcc472
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
###################################################################################
# B2G-Fall13pLHE-00001 from 
# https://cms-pdmv.cern.ch/mcm/requests?prepid=B2G-Fall13pLHE-00001&page=0&shown=127
###################################################################################
file_out=${file}_Fall13pLHE
echo "_______________________________________________________________________________
Begining EXO-Fall13pLHE step
_______________________________________________________________________________" 

cmsDriver.py step1 --filein file:$file  --fileout file:$file_out.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE --python_filename EXO-Fall13pLHE-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n $num_events || exit $? ; 
cmsRun -e -j EXO-Fall13pLHE-00001_rt.xml EXO-Fall13pLHE-00001_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Fall13pLHE-00001_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Fall13pLHE-00001_rt.xml 
grep "PeakValueRss" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventTime" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventCPU" EXO-Fall13pLHE-00001_rt.xml 
grep "TotalJobCPU" EXO-Fall13pLHE-00001_rt.xml 
###################################################################################
# EXO-Fall13-00035 from
# https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/B2G-Fall13-00035
###################################################################################
cd $release_path/CMSSW_6_2_11/src
eval `scram runtime -sh`

curl  -s https://raw.githubusercontent.com/cms-sw/genproductions/4cf7516f3f6d9ff8908c90663dbb2135c3e57c9e/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py 
[ -s Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py ] || exit $?;

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert
scram b

cd $working_dir
cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py --filein file:$input_file --fileout file:B2G-Fall13-00035.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --conditions POSTLS162_V1::All --step GEN,SIM --magField 38T_PostLS1 --geometry Extended2015 --python_filename B2G-Fall13-00035_1_cfg.py --no_exec -n 38 || exit $? ; 
cmsRun -e -j B2G-Fall13-00035_rt.xml B2G-Fall13-00035_1_cfg.py || exit $? ; 
echo 38 events were ran 
grep "TotalEvents" B2G-Fall13-00035_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" B2G-Fall13-00035_rt.xml 
grep "PeakValueRss" B2G-Fall13-00035_rt.xml 
grep "AvgEventTime" B2G-Fall13-00035_rt.xml 
grep "AvgEventCPU" B2G-Fall13-00035_rt.xml 
grep "TotalJobCPU" B2G-Fall13-00035_rt.xml 
###################################################################################
# EXO-Spring14dr-00199 form
# https://cms-pdmv.cern.ch/mcm/requests?prepid=EXO-Spring14dr-00199&page=0&shown=127
###################################################################################
echo "_______________________________________________________________________________
Begining EXO-Spring14dr step1
_______________________________________________________________________________" 
export SCRAM_ARCH=slc6_amd64_gcc481
if [ -r $release_path/CMSSW_7_0_6_patch1/src ] ; then 
    echo release CMSSW_7_0_6_patch1 already exists
else
    cd $release_path
    scram p CMSSW CMSSW_7_0_6_patch1
fi
cd $release_path/CMSSW_7_0_6_patch1/src 
eval `scram runtime -sh`

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

input_file=${file_out}
file_out=${file}_Spring14dr_step1
scram b
cd $working_dir
cmsDriver.py step1 --filein file:$input_file.root --fileout file:$file_out.root --pileup_input "dbs:/MinBias_TuneA2MB_13TeV-pythia8/Fall13-POSTLS162_V1-v1/GEN-SIM" --mc --eventcontent RAWSIM --pileup AVE_20_BX_25ns --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM-RAW --conditions POSTLS170_V5::All --step DIGI,L1,DIGI2RAW,HLT:2013,RAW2DIGI,L1Reco --magField 38T_PostLS1 --geometry DBExtendedPostLS1 --python_filename EXO-Spring14dr-00199_1_cfg.py --no_exec -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14dr-00199_rt.xml EXO-Spring14dr-00199_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14dr-00199_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14dr-00199_rt.xml 
grep "PeakValueRss" EXO-Spring14dr-00199_rt.xml 
grep "AvgEventTime" EXO-Spring14dr-00199_rt.xml 
grep "AvgEventCPU" EXO-Spring14dr-00199_rt.xml 
grep "TotalJobCPU" EXO-Spring14dr-00199_rt.xml 

echo "_______________________________________________________________________________
Begining EXO-Spring14dr step2
_______________________________________________________________________________" 
input_file=$file_out
file_out=${file}_Spring14dr_step2
cd $working_dir

cmsDriver.py step2 --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent AODSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier AODSIM --conditions POSTLS170_V5::All --step RAW2DIGI,L1Reco,RECO,EI --magField 38T_PostLS1 --geometry DBExtendedPostLS1 --python_filename EXO-Spring14dr-00199_2_cfg.py --no_exec -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14dr-00199_2_rt.xml EXO-Spring14dr-00199_2_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14dr-00199_2_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14dr-00199_2_rt.xml 
grep "PeakValueRss" EXO-Spring14dr-00199_2_rt.xml 
grep "AvgEventTime" EXO-Spring14dr-00199_2_rt.xml 
grep "AvgEventCPU" EXO-Spring14dr-00199_2_rt.xml 
grep "TotalJobCPU" EXO-Spring14dr-00199_2_rt.xml

####################################################################################
# EXO-Spring14miniaod-00024 from
# https://cms-pdmv.cern.ch/mcm/requests?prepid=B2G-Spring14miniaod-00024&page=0&shown=127
####################################################################################

echo "_______________________________________________________________________________
Begining EXO-Spring14miniaod step
_______________________________________________________________________________" 

input_file=$file_out
file_out=${file}_Spring14MiniAOD

cd $release_path/CMSSW_7_0_6_patch1/src
scram b
cd $working_dir
cmsDriver.py step1 --filein file:$input_file.root --fileout file:$file_out.root --mc --eventcontent MINIAODSIM --runUnscheduled --datatier MINIAODSIM --conditions PLS170_V7AN1::All --step PAT --python_filename EXO-Spring14miniaod-00115_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1 || exit $? ; 
cmsRun -e -j EXO-Spring14miniaod-00115_rt.xml EXO-Spring14miniaod-00115_1_cfg.py || exit $? ; 
grep "TotalEvents" EXO-Spring14miniaod-00115_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Spring14miniaod-00115_rt.xml 
grep "PeakValueRss" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventTime" EXO-Spring14miniaod-00115_rt.xml 
grep "AvgEventCPU" EXO-Spring14miniaod-00115_rt.xml 
grep "TotalJobCPU" EXO-Spring14miniaod-00115_rt.xml 
