#!/bin/bash 
if [ "$#" -ne 1 ]; then
    echo Enter the lhe file as a command line argument
    exit
fi

file=$1
if [ ! -e ./$file ]; then
    echo Enter a valid lhe file name as a command line argument
    exit
fi

if [ -r CMSSW_6_2_5/src ] ; then
    echo release CMSSW_6_2_5 already exists
else
    scram p CMSSW CMSSW_6_2_5
fi
cd CMSSW_6_2_5/src
eval `scram runtime -sh`
git cms-merge-topic lgray:fix_lhe_reader_weights_62X
scram b

eval `scram runtime -sh`
curl -s https://raw.github.com/cms-sw/genproductions/edcb3114a40826708bcd1132ea2c162e3bae7db3/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py 
scram b
cd ../../

file_out=${file}_MR_pLHE

#echo Begin pLHE
#echo _____________________________________________________________________________

#cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_Tune4C_13TeV_generic_LHE_pythia8_cff.py --filein file:$file --fileout file:$file_out.root --mc --eventcontent LHE --datatier GEN --conditions START62_V1::All --step NONE  --customise  Configuration/DataProcessing/Utils.addMonitoring -n 50 

#cd CMSSW_6_2_5/src
#eval `scram runtime -sh`
#curl -s https://raw.github.com/cms-sw/genproductions/743593d37770cc1e8064385572d81299ee8b340d/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_cff.py --retry 2 --create-dirs -o  Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_cff.py 
#scram b

file=${file_out}
file_out=${file}_Fall13

echo Begin Fall13
echo _____________________________________________________________________________

cmsDriver.py Configuration/GenProduction/python/ThirteenTeV/Hadronizer_MgmMatchTune4C_13TeV_madgraph_pythia8_cff.py --filein file:$file.root --fileout file:$file_out.root --mc --eventcontent RAWSIM --customise SLHCUpgradeSimulations/Configuration/postLS1Customs.customisePostLS1,Configuration/DataProcessing/Utils.addMonitoring  --datatier GEN-SIM --conditions POSTLS162_V1::All --step GEN,SIM --magField 38T_PostLS1 --geometry Extended2015 -n -1 


