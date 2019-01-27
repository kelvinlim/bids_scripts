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
    
def createNoRunCmd(startpath):
    """
    
    """
    cmd = 'find %s -name "*.json"'%(startpath)
    cmd += "| grep -v run | grep -v DELTA | grep sub- "
    cmd += "| grep -v tmp_dcm2bids "
    return cmd

def getNoRunFiles(destdir, file = 'norunlist.txt'):
    """
    read in lines from norunlist file
    """
    # do file exists check
    fp = os.path.join(destdir, file)
    
    try:
        with open(file) as fp:
            # do something with file
            rawlines = fp.readlines()
            fp.close()
            # remove newline
            lines = []
            for line in rawlines:
                lines.append( line.rstrip())
            return lines   
    except IOError:
        print("could not read", file)
    
#  add cwd to beginning of path to insure import is from current directory
sys.path.insert(0, os.getcwd())

import dicomlist

#Paremeters are read from the dicomlist.py file for this study
srcdir = dicomlist.srcdir
destdir = dicomlist.destdir
container = dicomlist.container
study_name = dicomlist.studyname

#===========================================================================
tmpdcm = 'tmp_dcm'  # temporary dicom directory in destdir
tmpdcmdir = os.path.join(destdir, tmpdcm)
bidsdir = os.path.join(destdir, "BIDS")
workdir = os.path.join(destdir, 'Work')

parser = argparse.ArgumentParser(description=
    """
    Finds and fixes imaging related files (json, nii.gz, tsv) that are
    missing the run-xx field in the file name.\n
    If there are files that have a run-01, they are deleted and then
    the files without run-xx are renamed with run-01 added to the
    filename.\n
    
    Use command to generate a file containing the  files witn no run-xx
    
    'find BIDS_output -name "*.json"| grep -v run | grep -v DELTA | grep sub- | grep -v tmp_dcm2bids > norunlist.txt '
    """)

# add arguments for beginning and end cases to process
parser.add_argument('range',
                    help="string like '0-2,5,9-12' specifying index of subjects",
                    type=str)
parser.add_argument('--debug',help='turn python debugger',
                    action='store_true')
parser.add_argument('--verbose',help='give more messages during execution',
                    action='store_true')
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')
#parser.add_argument('--full',help='use the full list from dicomlist.py',
#                   action='store_true')
parser.add_argument('--listing',help='list the sessions with index',
                    action='store_true')
args = parser.parse_args()

if args.debug==True:
    import pdb; pdb.set_trace()
    
# get the list of  no run files
norunlist = getNoRunFiles(destdir)

if args.listing==True:
    count = 0
    for file in norunlist:
        print(count,file)
        count += 1
    exit()

# list of items to process
itemlist = parse_range(args.range)

# go through the files defined in norunlist
for i in itemlist:
    item = norunlist[i]
    # get basename and dirname
    basename = os.path.basename(item)
    dirname = os.path.dirname(item)
    fulldir = os.path.join(destdir,dirname) # full directory path
    
    # get the parts 
    p = basename.split('.json')[0].split('_')
    baseWithoutRun = basename.split('.json')[0]
    baseWithRun = '_'.join(p[0:len(p)-1])
    baseWithRun += '_run-01_'
    baseWithRun += p[-1]
    
    # loop over suffix to rename
    for suffix in ['.json','.nii.gz']:
        srcFullPath = os.path.join(fulldir, baseWithoutRun + suffix )
        desFullPath = os.path.join(fulldir, baseWithRun + suffix )
  
        # check if srcFullPath exists
        if os.path.exists(srcFullPath):
            if args.verbose == True:
                print("File found ", srcFullPath)
            if not args.dryrun:
                os.rename(srcFullPath, desFullPath)
        else:
            if args.verbose == True:
                print("File NOT found ", srcFullPath)
                


