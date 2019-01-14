#!/usr/bin/env python

import argparse
import os
import glob
import fnmatch
import sys


def parse_range(astr):
    """
    parse_range('0-2, 5, 9-11')
    Out[163]: [0, 1, 2, 5, 9, 10, 11]
    """

    result=set()
    for part in astr.split(','):
        x=part.split('-')
        result.update(range(int(x[0]),int(x[-1])+1))
    return sorted(result)

def getTaskRun(bidsfilename):
    """
    Get the task and run info from the bids generated filename

    sub-801_ses-1501_task-rest_run-01_bold.nii.gz
    """
    parts = bidsfilename.split('_')
    return {'task': parts[2], 'run': int(parts[3].split('-')[1])}

def getNiftiFiles(dir, strmatch):
    """
    Retrieve files from dir matching strmatch, sort and return
    """
    matchlist = []
    listOfFiles = os.listdir(dir)
    pattern = "*" + strmatch + "*1.nii.gz"
    for entry in listOfFiles:
        if fnmatch.fnmatch(entry, pattern):
            matchlist.append(entry)
    # sort the list
    matchlist.sort()
    return matchlist

def removeBadFiles(bidspath, filename):
    """Remove the bad nii and json file"""
    niipath = os.path.join(bidspath, filename)
    jsonfile = filename.split(".nii")[0]+".json"
    jsonpath = os.path.join(bidspath, jsonfile)
    
    if os.path.exists(niipath):
        # remove the file
        os.remove(niipath)
        
    if os.path.exists(jsonpath):
        # remove the file
        os.remove(jsonpath)        
  
def fixFileRun(bidspath, filename):
    # do cleanup, check to see if the new file generated has run-xx or not
    
    # check if filename exists without the run-xx field
    # 'sub-800_ses-1500_task-eyegaze_run-02_bold.nii.gz'
    if 'run' in filename:
        # assemble new filename without the run part
        part1 = filename.split('_')[0:3]
        part2 = filename.split('_')[4]
        norun = '_'.join(part1+[part2])
        
        # see if the norun file exists
        if os.path.exists(os.path.join(bidspath, norun)):
            # need to rename with the run in the filename
            
            origpath = os.path.join(bidspath, norun)
            newpath = os.path.join(bidspath,filename)
            # rename the file
            os.rename(origpath, newpath)
            
            # now do the same for json file
            # create the respective json files
            norun_json = norun.split('.nii')[0] + '.json'
            file_json = filename.split('.nii')[0] + '.json'
            
            origpath = os.path.join(bidspath, norun_json)
            newpath = os.path.join(bidspath,file_json)
            # rename the json file
            os.rename(origpath, newpath)

def fixNoRunFiles(bidspath):
    """fix the files that have no run-xx in their filenames"""
    # rename files without a run-xx to include run-01   
    # get list of files
    # doesn't handle the event.tsv files
    filepathlist = glob.glob(os.path.join(bidspath, '*bold*'))
    
    for filepath in filepathlist:
        if not 'run' in os.path.basename(filepath):
            # found a file without a run
            # recreate the filename with a run-01 inserted
            # split the filename
            filename = os.path.basename(filepath)
            part1, part2 = filename.split('bold')
            newfilename = part1 + 'run-01_bold' + part2
            os.rename(os.path.join(bidspath, filename),
                      os.path.join(bidspath, newfilename))
    
    
#  add cwd to beginning of path to insure import is from current directory
sys.path.insert(0, os.getcwd())

import dicomlist
import redolist

#Paremeters are read from the dicomlist.py file for this study
srcdir = dicomlist.srcdir
destdir = dicomlist.destdir
container = dicomlist.container
study_name = dicomlist.studyname

#===========================================================================
tmpdcm = 'tmp_dcm'  # temporary dicom directory in destdir
tmpdcmdir = os.path.join(destdir, tmpdcm)
bidsdir = os.path.join(destdir, "BIDS_output")
workdir = os.path.join(destdir, 'Work')



# get the number of sessions  defined in dicomlist.py
print('number of sessions ',len(redolist.cases))

parser = argparse.ArgumentParser(description=
    """Redo nifti conversion where bids_validator has identified bad
    cases. Uses dicomlist.py and redolist.py. """)

# add arguments for beginning and end cases to process
parser.add_argument('range',
                    help="string like '0-2,5,9-12' specifying index of subjects",
                    type=str)
parser.add_argument('--debug',help='turn python debugger',
                    action='store_true')
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')
#parser.add_argument('--full',help='use the full list from dicomlist.py',
#                   action='store_true')
parser.add_argument('--forcenifti',help='force conversion of dicom data to nifti',
                    action='store_true')
parser.add_argument('--listing',help='list the sessions with index',
                    action='store_true')
args = parser.parse_args()

if args.debug==True:
    import pdb; pdb.set_trace()
    
if args.listing==True:
    count = 0
    for case in redolist.cases:
        info = case[0][2:].split('/')  # drop the initial ./
        sub = info[0] # extract sub
        ses = info[1] # extract ses
        file = info[-1]
        print(count, sub, ses, file)
        count += 1
    exit()

# list of items to process
itemlist = parse_range(args.range)

# go through the datasets defined in redolist.py
for item in itemlist:
    case = redolist.cases[item]
    info = case[0][2:].split('/')  # drop the initial ./
    sub = info[0] # extract sub
    ses = info[1] # extract ses
    datatype = info[2]  # extract out 'func' or 'anat', etc
    subDigits = sub.split('-')[1]
    sesDigits = ses.split('-')[1]
    filename = info[-1]

    dicomdir = os.path.join(tmpdcmdir, subDigits, sesDigits)
    replacedir = os.path.join(destdir, 'Replaced')

    # create the replacedir
    if not os.path.exists(replacedir):
        os.makedirs(replacedir)

    print(filename)
    print(sub, ses, subDigits, sesDigits, datatype)
    print(srcdir, dicomdir, bidsdir)
    #import pdb; pdb.set_trace()

    
    # dcm2bids -d DICOM_DIR -p PARTICIPANT_ID -s SESSION_ID -c CONFIG_FILE -o BIDS_DIR
    ## dcm2bids -d DICOM_DIR -p PARTICIPANT_ID -s SESSION_ID -c CONFIG_FILE -o BIDS_DIR
    cmd1="dcm2bids -d %s -p %s  -s %s -c config.json -o %s --forceDcm2niix --clobber"%(dicomdir, subDigits, sesDigits, bidsdir)
    print(cmd1)

    if not args.dryrun:
        # rm the bad file and the json file
        bidspath = os.path.join(bidsdir, sub, ses, datatype)
        removeBadFiles(bidspath, filename)
        os.system(cmd1)
        
        # do cleanup, check to see if the new file generated has run-xx
        fixNoRunFiles(bidspath)
