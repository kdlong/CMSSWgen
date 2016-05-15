#!/bin/env python
import sys
import shutil
import subprocess
import os
import argparse
import glob
 
def main():
    args = parseComLineArgs()
    if os.path.isfile(args.param_card):
        params = readParamsFromCard(args.param_card)
    current_path = os.getcwd()
    os.chdir(sys.path[0])
    if not os.path.isfile(args.param_card):
        args.param_card = "../cards/" + args.param_card.rsplit("/", 1)[-1]
        params = readParamsFromCard(args.param_card)
    if "pLHE" in args.step:
        doGENSIMpLHE(params)
        if args.step == "pLHEtoGENSIM":
            submitStepToCondor("GENSIM", params, "")
    else:
        opts = " --resubmit-failed-jobs " if args.resubmit else ""
        submitStepToCondor(args.step, params, opts)
    os.chdir(current_path)
# each of which are submitted to the pLHE step. If PATH_TO_FILES is
# specified, each file in the path is submitted. If LHE_FILE is specified,
# only it is submitted.
def doGENSIMpLHE(params):
    if os.path.isfile(params["LHE_FILE"]):
        split = params["LHE_FILE"].rsplit("/", 1)
        path = split[0]
        file_name = split[1]
    else:
        print "Invalid LHE file"
        exit()
    path_to_edm_files = path + "/" + params["JOB_NAME"]
    if not os.path.exists(path_to_edm_files):
        os.mkdir(path_to_edm_files)
    if not os.path.exists(path + "/xml_files"):
        os.mkdir(path + "/xml_files")
    setupCMSSW(params["PLHE_CMSSW_VERSION"], "../CMSSWrel")
    lhe_file_name = params["LHE_FILE"].rsplit("/", 1)[-1]
    out_file = path_to_edm_files + "/" + lhe_file_name.replace(".lhe", ".root")
    if params["NUM_EVENTS"] == "-1":
        params["NUM_EVENTS"] = getLHENumEvents(params["LHE_FILE"])
   
    if subprocess.call(["./helper_scripts/check_permissions.sh"]):
        exit(1)
    hdfs_dir = '/'.join(["/hdfs/store/user", params["USERNAME"], params["JOB_NAME"]])
    if os.path.isdir(hdfs_dir):
        print "The directory %s already exists! " % hdfs_dir
        print "Remove it and try again or use a new JOB_NAME"
        exit(1)
    print "Running over %s events with %s events per job" % (params["NUM_EVENTS"], params["EVENTS_PER_JOB"])

    for i in xrange(0, int(params["NUM_EVENTS"]), int(params["EVENTS_PER_JOB"])):
        current_file = out_file.replace(".root", "_%s.root" % 
            formatNumWithZeros(i/int(params["EVENTS_PER_JOB"]), 3))
        if subprocess.call(["cmsRun" 
                         + " ../config_files/%s" % params["PLHE_CFG"]
                         + " inputFiles=file:%s" % params["LHE_FILE"] 
                         + " outputFile=file:%s" % current_file
                         + " maxEvents=%s" % params["EVENTS_PER_JOB"]
                         + " skipEvents=%s" % str(i)],
                    shell=True):
            print "Error creating file %s" % current_file
        else:
            print "Created file %s" % current_file
    if not subprocess.call(["gsido", "cp", "-r", path_to_edm_files, 
            "/hdfs/store/user/%s" % params["USERNAME"]]):
        shutil.rmtree(path_to_edm_files)
        print "Files moved to /hdfs/store/user/%s" % params["USERNAME"]
    else:
        print "Failed to move files to /hdfs/store/user/%s" % params["USERNAME"]
# Submits the step in the generation according to the command line step argument
# and the information in the parameter card given. Requires grid proxy
# to allow access to HDFS. Uses rename_sim_files.sh to rename files after multiple steps 
# to prevent excessively long names.
def submitStepToCondor(step, params, opts):
    append_to_name = getPreviousStep(step, params)
    config_name = step.upper() + "_CFG"
    config_file = params[config_name] 
    cmssw_version = params[step.upper() + "_CMSSW_VERSION"]
    files_per_job = params["%s_FILES_PER_JOB" % step.upper()]
    if append_to_name != "":
        append_to_name = "-" + append_to_name
        #subprocess.call(["gsido", "helper_scripts/rename_sim_files.sh",
        #    params["JOB_NAME"], params["USERNAME"], config_name, append_to_name])
    setupCMSSW(cmssw_version, "../CMSSWrel")
    subprocess.call(["farmoutAnalysisJobs " 
                        + "/".join(["--input-dir=root://cmsxrootd.hep.wisc.edu//store/user",
                            params["USERNAME"], params["JOB_NAME"] + append_to_name])
                        + ("" if files_per_job is None else \
                            (" --input-files-per-job=%s" % files_per_job))
                        + "".join([" ", params["JOB_NAME"], opts])
                        + " ../CMSSWrel/CMSSW_" + cmssw_version
                        + " ../config_files/" + config_file
                        + " 'inputFiles=$inputFileNames'" 
                        + " 'outputFile=$outputFileName' "], 
                    shell=True)                        
# If the desired CMSSW release exists, cmsenv is called in that directory. If it
# does not exist it is first created 
# 
# NOTE: This should properly set CMS environment varialbes within this script,
# But it is much better to set the appropriate CMS release yourself before
# running the pLHE step, as external varialbes may not be set properly
def setupCMSSW(version, cmssw_dir):
    if "CMSSW_BASE" in os.environ.keys():
        if version in os.environ["CMSSW_BASE"]:
            return
    if "7" in version:
        architechure = " slc6_amd64_gcc481 "
    if not os.path.exists(cmssw_dir):
        os.mkdir(cmssw_dir)
    print "Setting up %s " % version
    command = ['bash', '-c', "source helper_scripts/setupCMSSW.sh "
                        + cmssw_dir 
                        + "".join([" ", version, " "])
                        + " slc6_amd64_gcc481"]
    proc = subprocess.Popen(command, stdout = subprocess.PIPE)
    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        os.environ[key.replace("export ", "")] = value 
    proc.communicate()    

# Reads variables given in the param card passed as a command line argument
def readParamsFromCard(card_name):
    steps = ["PLHE", "GENSIM", "DIGI", "RECO", "MINIAOD"]
    card_vars = ["JOB_NAME","USERNAME","NUM_EVENTS","EVENTS_PER_JOB","LHE_FILE"] 
    for step in steps:
        card_vars.extend(["%s_%s" % (step, x) for x in 
            ["CFG", "CMSSW_VERSION", "FILES_PER_JOB"]])
    card_params = {}
    for var in card_vars:
        card_params.update({var : None})
    with open(card_name) as card:
        for line in card:
            input = []
            if line[0] != "#":
                input = line.split("=")
            if len(input) == 2:
                if "$USER" in input[1]:
                    input[1] = input[1].replace("$USER", os.environ["USER"])
                variable = input[0].strip()
                if variable not in card_params.keys():
                    print "Invalid card variable %s" % variable
                card_params[variable] = input[1].strip()
    return card_params
# Returns the name of the previous step. Necessisary for locating the appropriate input
# directory in HDFS
def getPreviousStep(step, params):
    previous = {}
    previous.update({"GENSIM" : "" })
    config_name = lambda x: x.split("/")[-1].strip(".py")
    previous.update({"DIGI" : config_name(params["GENSIM_CFG"]) })
    previous.update({"RECO" : config_name(params["DIGI_CFG"]) })
    previous.update({"MINIAOD" : config_name(params["RECO_CFG"]) })
    return previous[step]
# Gets arguments from the command line
def getLHENumEvents(lhe_file_name):
    with open(lhe_file_name) as lhe_file:
        for line in lhe_file:
            if "#  Number of Events" in line:
                num_events = line.split(":")[-1].strip()
                return num_events
    print "Could not read number of events from LHE file."
    exit()
# formats a number to have length formatted_length regardless of it's order of
# magnitude by appending leading zeros. e.g., formatNumWithZeros(17, 5) returns
# 00017 
def formatNumWithZeros(num, formatted_length):
    formatted_num = str(num)
    while len(formatted_num) < formatted_length:
        formatted_num = "0" + formatted_num
    return formatted_num
def parseComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("step", type=str, choices=["pLHE", "pLHEtoGENSIM", "GENSIM",
                        "DIGI", "RECO", "AOD", "MINIAOD"],
                        help="Specify step in the simulation chain.")
    parser.add_argument("-r", "--resubmit", action="store_true",
                       help="resubmit failed jobs from step")
    parser.add_argument("-c", "--param_card", type=str, required=True,
                        help="name of param card") 
    args = parser.parse_args()
    return args
if __name__ == "__main__":
    main()
