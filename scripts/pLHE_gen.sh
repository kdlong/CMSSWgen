#!/bin/bash

file=$1

if [ ! -e ./$file ] ; then
    echo Enter a valid lhe file name as a command line argument
    exit
fi

if [ -r CMSSW_6_2_12/src ] ; then 
    echo release CMSSW_6_2_12 already exists
else
    scram p CMSSW CMSSW_6_2_12
fi

cd CMSSW_6_2_12/src
eval `scram runtime -sh`
curl  -s https://raw.githubusercontent.com/cms-sw/genproductions/edcb3114a40826708bcd1132ea2c162e3bae7db3/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py 

scram b
cd ../../
cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --filein file:$1  --fileout file:$1_EXO-Fall13pLHE-00001.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE --python_filename EXO-Fall13pLHE-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n -1 || exit $? ; 
cmsRun -e -j EXO-Fall13pLHE-00001_rt.xml EXO-Fall13pLHE-00001_1_cfg.py || exit $? ; 
echo 10000 events were ran 
grep "TotalEvents" EXO-Fall13pLHE-00001_rt.xml 
grep "Timing-tstoragefile-write-totalMegabytes" EXO-Fall13pLHE-00001_rt.xml 
grep "PeakValueRss" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventTime" EXO-Fall13pLHE-00001_rt.xml 
grep "AvgEventCPU" EXO-Fall13pLHE-00001_rt.xml 
grep "TotalJobCPU" EXO-Fall13pLHE-00001_rt.xml 


