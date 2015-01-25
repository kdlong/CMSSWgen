#!/bin/env python
import sys
import fileinput
import glob
import os
import argparse
import shutil

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("lhe_file_name", type=str,
                        help="LHE file to which the CMS block should be added")  
    args = parser.parse_args()
    addBlockToFile(args.lhe_file_name, 2, 2, 5.0)

def addBlockToFiles(path_to_files,  max_jets, min_jets, eta_clus):
    file_list = glob.glob("".join(path_to_files,"*.lhe"))
    for file in file_list:
        addBlockToFile(file, max_jets, min_jets, eta_clus) 
def addBlockToFile(lhe_file_name, max_jets, min_jets, eta_clus):
    temp_file_name = "temp.lhe"
    parms = readParamsFromLHEFile(lhe_file_name)
    block_location = False
    has_block = False
    with open("temp.lhe","w") as temp_file:           
        for line in fileinput.input(lhe_file_name):
            if block_location:
                if "<MGParamCMS>" in line:
                    print "MadGraph CMS block already included in file. Will be overwritten."
                    has_block = True
                    continue
                if has_block:
                    if "</MGParamCMS>" in line:
                        has_block = False
                    else:
                        continue
                else:
                    temp_file.write(getCMSBlock(params))
                    block_location = False
            elif "</MGRunCard>" not in line:
                temp_file.write(line)
            else:
                temp_file.write(line)
                block_location = True
    shutil.move(temp_file_name, lhe_file_name)
def readParamsFromLHEFile(lhe_file_name):
    params = ["ickkw", "maxjetflavor", "xqcut"]
    header_info = {}
    with open(lhe_file_name) as lhe_file:
        line = lhe_file.readline()
        while("</MGRunCard" not in line):
            line = lhe_file.readline()
            for param in params:
                if "= " + param in line:
                    pos = line.find("=")
                    header_info[param] = line[0:pos].strip()
                    params.remove(param)
    return header_info
def getCMSBlock(params):
    MG_CMS_block = "\n<MGParamCMS>" \
        + "\n# All parameters that are given here can be selected to be set from this" \
        + "\n# header by setting the # corresponding CMSSW config parameter to -1" \
        + "\n# In case this is done, the entries here must exist of an error message" \
        + "\n# is given." \
        + "\n             %s = ickkw" % params['ICKKW'] \
        + "\n             %s = nqmatch    ! Max Jet Flavor " % parms["NQMATCH"] \
        + "\n             %s = maxjets    ! Largest number (inclusive ktMLM matching multipl.)" % params[MAXJETS] \
        + "\n             %s = minjets    ! Smallest number of additional light flavour jets" % params[MINJETS] \
        + "\n           %s = etaclmax   ! Maximum pseudorapidity for particles to cluster" % params[ETACLMAX] \
        + "\n            %s = qcut" % parms["QCUT"] \
        + "\n</MGParamCMS>"
    
if __name__ == "__main__":
    main()             
