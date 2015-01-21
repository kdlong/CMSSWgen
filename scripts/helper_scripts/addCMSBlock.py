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
    block_params = readParamsFromLHEFile(lhe_file_name)
    with open("temp.lhe","w") as temp_file:           
        for line in fileinput.input(lhe_file_name):
            if "</MGRunCard>" not in line:
                temp_file.write(line)
            else:
                temp_file.write(line)
                temp_file.write("<MGParamCMS>\n")
                temp_file.write("# All parameters that are given here can be selected to be set from this\n")
                temp_file.write("# header by setting the # corresponding CMSSW config parameter to -1\n")
                temp_file.write("# In case this is done, the entries here must exist of an error message\n")
                temp_file.write("# is given.\n")
                temp_file.write("             %s = ickkw" % block_params['ickkw'])
                temp_file.write("\n             %s = nqmatch    ! Max Jet Flavor " % block_params["maxjetflavor"])
                temp_file.write("\n             %s = maxjets    ! Largest number (inclusive ktMLM matching multipl.)" % max_jets)
                temp_file.write("\n             %s = minjets    ! Smallest number of additional light flavour jets" % min_jets)
                temp_file.write("\n           %s = etaclmax   ! Maximum pseudorapidity for particles to cluster" % eta_clus)
                temp_file.write("\n            %s = qcut" % block_params["xqcut"])
                temp_file.write("\n</MGParamCMS>\n")
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
    
if __name__ == "__main__":
    main()             
