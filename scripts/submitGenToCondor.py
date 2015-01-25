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
    current_path = os.getcwd()
    os.chdir(os.path.dirname(sys.argv[0]))
    print os.getcwd()
    args = parseComLineArgs()
    if not os.path.isfile(args.param_card):
        args.param_card = "../cards/" + args.param_card
    params = readParamsFromCard(args.param_card)
    if "pLHE" in args.step:
        doFall13pLHE(params)
        if args.step == "pLHEtoFall13":
            submitStepToCondor("Fall13", params, "")
    else:
        opts = "--resubmit-failed-jobs" if args.resubmit else ""
        print args.step
        submitStepToCondor(args.step, params, opts)
    os.chdir(current_path)
# If LHE_FILE_TO_SPLIT is given, this file is split into NUM_SPLIT_FILES,
# each of which are submitted to the Fall13pLHE step. If PATH_TO_FILES is
# specified, each file in the path is submitted. If LHE_FILE is specified,
# only it is submitted.
def doFall13pLHE(params):
    lhe_file_list = []
    if params["LHE_FILE_TO_SPLIT"] is not None:
        if params["MLM_MATCHING"] in ["True", "true"]:
            addCMSBlock.addBlockToFile(params)
        split = params["LHE_FILE_TO_SPLIT"].rsplit("/", 1)
        path = split[0]
        print path
        file_name = split[1]
        if not os.path.exists(path + "/lhe_files"):
            os.mkdir(path + "/lhe_files")
        splitLHEFile.split(params["LHE_FILE_TO_SPLIT"], 
              path + "/lhe_files/" + file_name.replace(".lhe", "_"), 
               int(params["NUM_SPLIT_FILES"]))
        lhe_file_list = glob.glob(path + "/lhe_files/*.lhe")
    elif params["PATH_TO_LHE_FILES"] is not None:
        path = params["PATH_TO_LHE_FILES"]
        lhe_file_list = glob.glob(params["PATH_TO_LHE_FILES"] + "/*.lhe")    
    else:
        split = params["LHE_FILE_TO_SPLIT"].rsplit("/", 1)
        path = split[0]
        file_name = split[1]
        lhe_file_list = [params["LHE_FILE"]]
    path_to_edm_files = path + "/" + params["JOB_NAME"]
    if not os.path.exists(path_to_edm_files):
        os.mkdir(path_to_edm_files)
    if not os.path.exists(path + "/xml_files"):
        os.mkdir(path + "/xml_files")
    setupCMSSW("7_0_6_patch1")
    for lhe_file in lhe_file_list:
        lhe_file_name = lhe_file.split("/")[-1]
        xml_file = path + "/xml_files/" + lhe_file_name.replace(".lhe", ".xml")
        out_file = path_to_edm_files + "/" + lhe_file_name.replace(".lhe", ".root")
        subprocess.call(["cmsRun", "-e", "-j", 
                         xml_file,
                         params["BASE_DIR"] + "/config_files/" + params["PLHE_CFG"],
                         "inputFiles=file:" + lhe_file, 
                         "outputFile=file:" + out_file])
    subprocess.call(["gsido", "cp", path_to_edm_files, "/hdfs/store/user/" + params["USERNAME"], "-r"])
# Submits the step in the generation according to the command line step argument
# and the information in the parameter card given. Requires grid information
# to allow access to HDFS. Uses rename_sim_files.sh to rename files after multiple 
# to prevent excessively long names.
def submitStepToCondor(step, params, opts):
    print "in submittocondor function"
    print os.getcwd()
    
    append_to_name = getPreviousStep(step, params)
    config_name = step.upper() + "_CFG"
    if "Spring14dr_1" in step:
        config_name = config_name.replace("_1", "_STEP1")
    elif "Spring14dr_2" in step:
        config_name = config_name.replace("_2", "_STEP2")
    elif step == "Fall13":
        if params["MLM_MATCHING"] in ["True", "true"]:
            config_name = config_name.replace("FALL13", "FALL13_MLM_MATCHING")
        else:
            config_name = config_name.replace("FALL13", "FALL13_NO_MATCHING")
    config_file = params[config_name] 
    if append_to_name != "":
        append_to_name = "-" + append_to_name
        subprocess.call(["gsido", "helper_scripts/rename_sim_files.sh",
            params["JOB_NAME"], params["USERNAME"], step, append_to_name])
    setupCMSSW("7_0_6_patch1")
    subprocess.call(["farmoutAnalysisJobs " 
                        + "--input-dir=root://cmsxrootd.hep.wisc.edu//store/user/"
                        + "".join([params["USERNAME"], "/", params["JOB_NAME"], append_to_name])
                        + "".join([" ", params["JOB_NAME"], " ", opts, " "])
                        + " $CMSSW_BASE "
                        + "../config_files/" + config_file
                        + " 'inputFiles=$inputFileNames' " 
                        + " 'outputFile=$outputFileName' "], 
                    shell=True)                        
# If the desired CMSSW release exists, cmsenv is called in that directory. If it
# does not exist it is first created.
def setupCMSSW(version):
    if version in os.environ["CMSSW_BASE"]:
        return
    if version == "7_0_6_patch1":
        architechure = " slc6_amd64_gcc481 "
    cmssw_dir = params["BASE_DIR"] + "/CMSSWrel"
    if not os.exists(cmssw_dir):
        os.mkdir(cmssw_dir)
    subprocess.call(["source " +  params["BASE_DIR"] + "/scripts/helper_scripts/setupCMSSW.sh "
                        + cmssw_dir 
                        + "".join([" ", version, " "])
                        + " slc6_amd64_gcc481 "],
                     shell = True)   
# Reads variables given in the param card passed as a command line argument
def readParamsFromCard(card_name):
    vars = ["JOB_NAME","MLM_MATCHING","USERNAME","BASE_DIR","CMSSW_PATH","LHE_FILE_TO_SPLIT", 
        "NUM_SPLIT_FILES","PATH_TO_LHE_FILES","LHE_FILE","PLHE_CFG","FALL13_MLM_MATCHING_CFG",
        "FALL13_NO_MATCHING_CFG", "SPRING14DR_STEP1_CFG", "SPRING14DR_STEP2_CFG", "SPRING14MINIAOD_CFG"] 
    card_params = {}
    for var in vars:
        card_params.update({var : None})
    with open(card_name) as card:
        for line in card:
            if line[0] != "#":
                input = line.split("=")
            if len(input) == 2:
                if "$USER" in input[1]:
                    input[1] = input[1].replace("$USER", os.environ["USER"])
                card_params[input[0].strip()] = input[1].strip()
    return card_params
# Returns the name of the previous step. Necessisary to for located the appropriate input
# directory in HDFS
def getPreviousStep(step, params):
    match = False
    if params["MLM_MATCHING"] in ["True", "true"]:
        match = True
    previous = {}
    previous.update({"Fall13" : "" })
    if match:
        previous.update({"Spring14dr_1" : params["FALL13_MLM_MATCHING_CFG"].strip(".py")}) 
    else:
        previous.update({"Spring14dr_1" : params["FALL13_NO_MATCHING_CFG"].strip(".py") })
    previous.update({"Spring14dr_2" : params["SPRING14DR_STEP1_CFG"].strip(".py") })
    previous.update({"Spring14miniaod" : params["SPRING14DR_STEP2_CFG"].strip(".py") })
    return previous[step]
# Gets arguments from the command line
def parseComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=str, choices=["pLHE", "pLHEtoFall13", "Fall13",
                        "Spring14dr_1", "Spring14dr_2", "Spring14miniaod"],
                        help="Specify step in the simulation chain.")
    parser.add_argument("-r", "--resubmit", action="store_true",
                       help="resubmit failed jobs from step")
    parser.add_argument("-c", "--param_card", type=str, required=True,
                        help="name of param card") 
    args = parser.parse_args()
    return args
if __name__ == "__main__":
    main()
