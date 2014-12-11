#!/bin/bash

# B2G-chain_Fall13_flowF13PU20bx25-00001 
# https://cms-pdmv.cern.ch/mcm/chained_requests?prepid=B2G-chain_Fall13_flowF13PU20bx25-00001&page=0&shown=15 
if [ "$#" -ne 1 ]; then
    echo "Enter the lhe file as a command line argument"
    exit
fi

file=$1
if [ ! -e ./$file ]; then
    echo Enter a valid lhe file name as a command line argument
    exit
fi
if [ -r CMSSW_6_2_11/src ] ; then 
 echo release CMSSW_6_2_11 already exists
else
scram p CMSSW CMSSW_6_2_11
fi
cd CMSSW_6_2_11/src
eval `scram runtime -sh`

scram b
cd ../../

file_out=${file}_B2G-Fall13pLHE
cmsDriver.py step1 --filein file:$file  --fileout file:$file_out.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE --python_filename B2G-Fall13pLHE-00027_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100 || exit $? ; 
cmsRun -e -j B2G-Fall13pLHE-00027_rt.xml B2G-Fall13pLHE-00027_1_cfg.py || exit $? ; 
grep "TotalEvents" B2G-Fall13pLHE-00027_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" B2G-Fall13pLHE-00027_rt.xml 
grep "PeakValueRss" B2G-Fall13pLHE-00027_rt.xml 
grep "AvgEventTime" B2G-Fall13pLHE-00027_rt.xml 
grep "AvgEventCPU" B2G-Fall13pLHE-00027_rt.xml 
grep "TotalJobCPU" B2G-Fall13pLHE-00027_rt.xml 

input_file=$file_out
file_out=${file}_BG2-Fall13

cd CMSSW_6_2_11/src
eval `scram runtime -sh`
curl  -s https://raw.githubusercontent.com/cms-sw/genproductions/4cf7516f3f6d9ff8908c90663dbb2135c3e57c9e/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py 
[ -s Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py ] || exit $?;

export X509_USER_PROXY=$HOME/private/personal/voms_proxy.cert

scram b
cd ../../
cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_Tauola_cff.py --filein file$input_file.root --fileout file:$file_root.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM --conditions POSTLS162_V1::All --step GEN,SIM --magField 38T_PostLS1 --geometry Extended2015 --python_filename B2G-Fall13-00035_1_cfg.py --no_exec -n 38 || exit $? ; 
cmsRun -e -j B2G-Fall13-00035_rt.xml B2G-Fall13-00035_1_cfg.py || exit $? ; 
grep "TotalEvents" B2G-Fall13-00035_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" B2G-Fall13-00035_rt.xml 
grep "PeakValueRss" B2G-Fall13-00035_rt.xml 
grep "AvgEventTime" B2G-Fall13-00035_rt.xml 
grep "AvgEventCPU" B2G-Fall13-00035_rt.xml 
grep "TotalJobCPU" B2G-Fall13-00035_rt.xml  
