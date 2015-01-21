#!/bin/env python
import sys
sys.path.append("/cms/kdlong/CMSSWgen/scripts/helper_scripts")
import subprocess
import splitLHEFile
import addCMSBlock
import os
import argparse
import glob

def main():
    base_dir = "/cms/kdlong/CMSSWgen"
    args = parseComLineArgs()
    lhe_file_list = []
    if "pLHE" in args.subparser_name:
        if args.file_to_split is not None:
            if args.addCMSBlock:
                addCMSBlock.addBlockToFile(args.file_to_split, 2, 2, 5.0)
            if not os.path.exists("lhe_files"):
                os.mkdir("lhe_files")
            splitLHEFile.split(args.file_to_split, 
                "lhe_files/" + args.file_to_split.replace(".lhe", "_"), 
                args.num_split_files)
            lhe_file_list = glob.glob("lhe_files/*.lhe")
        elif args.path_to_lhe_files is not None:
            lhe_file_list = glob.glob(args.path_to_lhe_files + "/*.lhe")    
        else:
            lhe_file_list = [args.lhe_file]
        doFall13pLHE(lhe_file_list, base_dir, args.job_name, args.hdfs_username)
    if args.subparser_name == "pLHEtoFall13" or args.subparser_name == "Fall13":
        doFall13(base_dir, args.match_scheme, args.job_name)     
    if args.subparser_name == "Spring14dr_1":
        doSpring14dr_step1(base_dir, args.job_name)
    if args.subparser_name == "Spring14dr_2":
        doSpring14dr_step2(base_dir, args.job_name)
def doFall13pLHE(lhe_file_list, base_dir, job_name, hdfs_username):
    if not os.path.exists(job_name):
        os.mkdir(job_name)
    if not os.path.exists("xml_files"):
        os.mkdir("xml_files")
    subprocess.call(["source " +  base_dir + "/scripts/helper_scripts/setupCMSSW.sh "
                        + base_dir + "/CMSSWrel" 
                        + " 7_0_6_patch1 "
                        + " slc6_amd64_gcc481 "],
                     shell = True)
    for lhe_file in lhe_file_list:
        lhe_file_name = lhe_file.split("/")[-1]
        xml_file = "xml_files/" + lhe_file_name.replace(".lhe", ".xml")
        out_file = job_name + "/" + lhe_file_name.replace(".lhe", ".root")
        subprocess.call(["cmsRun", "-e", "-j", 
                         xml_file,
                         base_dir + "/config_files/B2G-Fall13pLHE.py",
                         "inputFiles=file:" + lhe_file, 
                         "outputFile=file:" + out_file])
    if hdfs_username is not None:
        subprocess.call(["gsido", "cp", 
                         job_name, 
                         "/hdfs/store/user/" + hdfs_username, "-r"])
def doFall13(base_dir, match_scheme, job_name):
    if match_scheme == 1:
        config_file = base_dir + "/config_files/B2G-Fall13_MgM_match_cfg.py"
    else:
        config_file = base_dir + "/config_files/B2G-Fall13_no_match_cfg.py" 
    subprocess.call(["source " +  base_dir + "/scripts/helper_scripts/setupCMSSW.sh "
                        + base_dir + "/CMSSWrel" 
                        + " 7_0_6_patch1 "
                        + " slc6_amd64_gcc481 "],
                     shell = True)
    subprocess.call(["farmoutAnalysisJobs " 
                        + "--input-dir=root://cmsxrootd.hep.wisc.edu//store/user/kdlong/"
                        + job_name + "-B2G-Fall13_no_match_cfg "
                        + job_name 
                        + " $CMSSW_BASE "
                        + config_file
                        + " 'inputFiles=$inputFileNames' " 
                        + " 'outputFile=$outputFileName'"], 
                    shell=True)                        
def doSpring14dr_step1(base_dir, job_name):
    config_file = base_dir + "/config_files/EXO-Spring14dr_1_cfg.py"
    subprocess.call(["source " +  base_dir + "/scripts/helper_scripts/setupCMSSW.sh "
                        + base_dir + "/CMSSWrel" 
                        + " 7_0_6_patch1 "
                        + " slc6_amd64_gcc481 "],
                     shell = True)
    subprocess.call(["farmoutAnalysisJobs " 
                        + "--input-dir=root://cmsxrootd.hep.wisc.edu//store/user/kdlong/"
                        + job_name + "-B2G-Fall13_no_match_cfg "
                        + job_name 
                        + " $CMSSW_BASE "
                        + config_file
                        + " 'inputFiles=$inputFileNames' " 
                        + " 'outputFile=$outputFileName'"], 
                    shell=True)                        
def doSpring14dr_step2(base_dir, job_name):
    config_file = base_dir + "/config_files/EXO-Spring14dr_2_cfg.py"
    subprocess.call(["source " +  base_dir + "/scripts/helper_scripts/setupCMSSW.sh "
                        + base_dir + "/CMSSWrel" 
                        + " 7_0_6_patch1 "
                        + " slc6_amd64_gcc481 "],
                     shell = True)
    subprocess.call(["farmoutAnalysisJobs " 
                        + "--input-dir=root://cmsxrootd.hep.wisc.edu//store/user/kdlong/"
                        + job_name + "-EXO-Spring14dr_1_cfg "
                        + job_name 
                        + " $CMSSW_BASE "
                        + config_file
                        + " 'inputFiles=$inputFileNames' " 
                        + " 'outputFile=$outputFileName'"], 
                    shell=True)                        
def parseComLineArgs():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser_name")
    
    pLHE = subparsers.add_parser("pLHE")
    lhe_input = pLHE.add_mutually_exclusive_group(required=True)
    lhe_input.add_argument("--lhe_file", type=str, help="""lhe file to convert to
                           to EDM. Will not be split""")
    lhe_input.add_argument("--path_to_lhe_files", type=str, help="""path to many
                           lhe files to convert to pLHE""")
    lhe_input.add_argument("--file_to_split", type=str, help="""lhe_file to be split
                           before running EDM conversion on each split file""")
    pLHE.add_argument("--num_split_files", type=int, required=False,
                      help="number of split files to make from <file_to_split>")
    pLHE.add_argument("-n", "--job_name", type=str, required=True,
                      help="Number of files to make from <file_to_split>") 
    pLHE.add_argument("--hdfs_username", type=str, help="""EDM files will be placed 
                      in /hdfs/store/<hdfs_username>/<job_name> if provided""") 
    pLHE.add_argument("--addCMSBlock", action='store_true') 
    
    pLHEtoFall13 = subparsers.add_parser("pLHEtoFall13")
    lhe_input = pLHEtoFall13.add_mutually_exclusive_group(required=True)
    lhe_input.add_argument("--lhe_file", type=str, help="""lhe file to convert to
                           to EDM and Hadronize. Will not be split""")
    lhe_input.add_argument("--path_to_lhe_files", type=str, help="""path to many
                           lhe files to convert to pLHE and Hadronize""")
    lhe_input.add_argument("--file_to_split", type=str, help="""lhe_file to be split
                           before running EDM conversion and Hadronization on each 
                           split file""")
    pLHEtoFall13.add_argument("--num_split_files", type=int, required=False,
                              help="Number of files to make from <file_to_split>") 
    pLHEtoFall13.add_argument("--addCMSBlock", action='store_true', help="""add 
                              required CMS block to LHE file. This should be true 
                              unless the block has already been added""") 
    pLHEtoFall13.add_argument("-n", "--job_name", type=str, required=True,
                              help="Name of folder where files will be stored") 
    pLHEtoFall13.add_argument("--hdfs_username", type=str, help="""EDM files will be 
                              placed in /hdfs/store/<hdfs_username>/<job_name> if
                              provided""")
    pLHEtoFall13.add_argument("--match_scheme", type=int, choices=[0,1], 
                              required=True,
                              help="1 for MLM jet matching, 0 for no matching") 
    
    fall13 = subparsers.add_parser("Fall13")
    fall13.add_argument("-n", "--job_name", type=str, required=True,
                              help="Name of folder where files will be stored") 
    fall13.add_argument("--hdfs_username", type=str, help="""EDM files will be 
                              placed in /hdfs/store/<hdfs_username>/<job_name> if
                              provided""")
    fall13.add_argument("--match_scheme", type=int, choices=[0,1], 
                              required=True,
                              help="1 for MLM jet matching, 0 for no matching") 
    spring14dr_1 = subparsers.add_parser("Spring14dr_1")
    spring14dr_1.add_argument("-n", "--job_name", type=str, required=True,
                              help="Name of folder where files will be stored") 
    spring14dr_1.add_argument("--hdfs_username", type=str, help="""EDM files will be 
                              placed in /hdfs/store/<hdfs_username>/<job_name> if
                              provided""")
    spring14dr_2 = subparsers.add_parser("Spring14dr_2")
    spring14dr_2.add_argument("-n", "--job_name", type=str, required=True,
                              help="Name of folder where files will be stored") 
    spring14dr_2.add_argument("--hdfs_username", type=str, help="""EDM files will be 
                              placed in /hdfs/store/<hdfs_username>/<job_name> if
                              provided""")
 
    args = parser.parse_args()
    if args.subparser_name == "pLHE" or args.subparser_name == "pLHEtoFall13":
        if args.num_split_files is not None:
            if args.file_to_split is None:
                print "--num_split_files is only allowed when --file_to_split is specified"
                exit(0)
        elif args.file_to_split is not None:
            print "You must specify a number of split files to make if --file_to_split is specified"
            exit(0)
    return args
if __name__ == "__main__":
    main()
