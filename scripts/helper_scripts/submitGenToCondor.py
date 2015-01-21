#!/bin/env python
import sys
import subprocess
import helper_scripts/splitLHEFile as splitLHEFile
import helper_scripts/addCMSBlock as addCMSBlock
import os
import argparse

def main()
    args = getComLineArgs()
    lhe_file_list = []
    if (args.file_to_split is not None):
        if not os.path.exists("lhe_files"):
            os.mkdir("lhe_files")
        if args.addCMSBlock:
            addCMSBlock.addBlockToFile(args.file_to_split, 
                                       args.match_scheme,
                                       5, 2, 2, 0, 0) 
                                       #5.0, 10)
        splitLHEFile.split(args.file_to_split, 
                           "lhe_files/" + args.file_to_split.replace(".lhe", "_"), 20)
        lhe_file_list = glob.glob("lhe_files/*.lhe")
    elif (args.path_to_lhe_files is not None):
        lhe_file_list = glob.glob(path_to_lhe_files + "/*.lhe")
    else:
        lhe_file_list = [args.lhe_file]
    
    base_dir = "/cms/kdlong/CMSSWgen/"
    doFall13pLHE(lhe_file_list, base_dir)

def doFall13(base_dir, match_scheme, job_name)
    subprocess.call([base_dir + "/scripts/helper_scripts/setupCMSSW.sh",
                     "/cms/kdlong/CMSSWgen/CMSSWrel",
                     "CMSSW_6_2_11"
                     "slc5_amd64_gcc472"])
    if match_scheme == 1:
        config_file = "config_files/B2G-Fall13_MgM_match_cfg.py"
    else if match_scheme == 0:
        config_file = "config_files/B2G-Fall13_no_match_cfg.py"
    else
        print "Matching scheme must be MLM (1) or no matching (0)"
        exit(0)
    subprocess.call(["farmoutAnalysisJobs",
                        "job_name",
                        "$CMSSW_BASE",
                        config_file,
                        "'inputFiles=$inputFileNames'",
                        "'outputFiles=$outputFileName'"])

def doFall13pLHE(lhe_file_list, base_dir, hdfs_username, job_name):
    if not os.path.exists("config_files"):
        os.mkdir("config_files")
    if not os.path.exists("xml_files"):
        os.mkdir("xml_files")
    if not os.path.exists("pLHE_files"):
        os.mkdir("pLHE_files")
    for lhe_file in lhe_file_list:
        subprocess.call([base_dir + "/scripts/setupCMSSW.sh",
                         base_dir + "/CMSSWrel", 
                         base_dir + "6_2_11",
                         base_dir + "slc5_amd64_gcc472"])
        subprocess.call(["cmsRun", "-e", "-j", "test.xml", 
                         base_dir + "/scripts/config_files/B2G-Fall13pLHE.py",
                         "inputFiles=file:"+lhe_file, 
                         "outputFile=file:pLHE__files/" 
                            + lhe_file.replace(".lhe","_Fall13pLHE.root"])
    subprocess.call(["gsido", "mkdir", 
                     "/hdfs/store/user/" + hdfs_username + "/" + job_name])
    subprocess.call(["gsido", "mv", "pLHE_files/*",
                     "/hdfs/store/user/" hdfs_username + "/" job_name])  
def getComLineArgs()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exculsive_group(required=True)
    group.add_argument("--file_to_split", type=str, help="LHE file to be split")
    group.add_argument("--lhe_file" type=str, help="""single LHE file to be used
                       (will not be split)""")
    group.add_argument("--path_to_files", type=str, help="""path to lhe files which
                       are already divided.""")
    parser.add_argument("--addCMSBlock", action='store_true', required=true,
                        help="Add the required CMS info block to the LHE file")
    return parser.parse_args()

if __name__ == "__main__":
    main()
