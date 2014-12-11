#!/bin/bash
source  /afs/cern.ch/cms/cmsset_default.sh
export SCRAM_ARCH=slc5_amd64_gcc472
if [ -r CMSSW_6_2_3/src ] ; then 
 echo release CMSSW_6_2_3 already exists
else
scram p CMSSW CMSSW_6_2_3
fi
cd CMSSW_6_2_3/src
eval `scram runtime -sh`
curl  -s https://raw.githubusercontent.com/cms-sw/genproductions/edcb3114a40826708bcd1132ea2c162e3bae7db3/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py 

scram b
cd ../../
cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --filein file:longer_test_nc.lhe  --fileout file:longer_test_pLHE.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE --python_filename EXO-Fall13pLHE-00001_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 100 || exit $? ; 

