#!/usr/bin/env python

import argparse
import os
import shutil
import fnmatch
import distutils

import sys

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


#  add cwd to beginning of path to insure import is from current directory
sys.path.insert(0, os.getcwd())

import dicomlist
import rerun

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
print('number of sessions ',len(rerun.cases))

parser = argparse.ArgumentParser(description=
    """Redo nifti conversion where bids_validator has identified bad
    cases. Uses dicomlist.py and rerun.py. """)

# add arguments for beginning and end cases to process
parser.add_argument('beg',help="first element of session array to start, 0 indexed",
                    type=int)
parser.add_argument('end',help="last element of session array to end",
                    type=int)
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')
parser.add_argument('--forcenifti',help='force conversion of dicom data to nifti',
                    action='store_true')
parser.add_argument('--listing',help='list the sessions with index',
                    action='store_true')
args = parser.parse_args()

if args.listing==True:
    count = 0
    for case in rerun.cases:
        info = case[0][2:].split('/')  # drop the initial ./
        sub = info[0] # extract sub
        ses = info[1] # extract ses
        file = info[-1]
        print(count, sub, ses, file)
        count += 1
    exit()

# limit the size of labels array based on beg and end arguments
# for 31 element array, to split in two, 0:16, 16:31
cases = rerun.cases[args.beg:args.end]

# go through the datasets defined in dicomlist.py
for case in cases:
    info = case[0][2:].split('/')  # drop the initial ./
    sub = info[0] # extract sub
    ses = info[1] # extract ses
    datatype = info[2]  # extract out 'func' or 'anat', etc
    #import pdb; pdb.set_trace()
    subDigits = sub.split('-')[1]
    sesDigits = ses.split('-')[1]
    filename = info[-1]

    srcdir = os.path.join(tmpdcmdir,subDigits)
    dicomdir = os.path.join(srcdir, sesDigits)
    niftidir = os.path.join(srcdir, sesDigits+'n')
    newdir = os.path.join(bidsdir, sub, ses, datatype)
    replacedir = os.path.join(destdir, 'Replaced')

    # create the replacedir
    if not os.path.exists(replacedir):
        os.makedirs(replacedir)

    print(filename)
    print(sub, ses, subDigits, sesDigits, datatype)
    print(srcdir, dicomdir, niftidir, newdir, replacedir)
    #import pdb; pdb.set_trace()

    if args.forcenifti:  # force nifti conversion
        # check if dir exists then delete it
        if os.path.exists(niftidir):
            shutil.rmtree(niftidir)  # remove if it exists
        # create the new destinaton directory
        os.makedirs(niftidir)

    else:
        if not os.path.exists(niftidir):
            # make directory if needed
            os.makedirs(niftidir)

    # nifti conversion command
    # dcm2niix output customized with '=' separators to facilitate parsing
    # use %% to escape a % character in a formatted string (2.7)
    cmd1 = "dcm2niix -z y -o %s -f '%%f=%%d=%%s' %s"%(niftidir, dicomdir)
    print(cmd1)

    if not args.dryrun:
        # do nifti conversion
        os.system(cmd1)

    # retrieve task and run of case in question
    caseinfo = getTaskRun(filename)
    # get the matching string for this task
    niftistring = rerun.filemaps[caseinfo['task']]

    # get the list of the non bids nifti files matching the string
    # import pdb; pdb.set_trace()
    niftifiles = getNiftiFiles(niftidir, niftistring)
    niftifile = niftifiles[caseinfo['run'] - 1 ] # zero indexed so subtract 1


    if not args.dryrun:
        # move the bad case to the replacedir if it doesn't exist
        badbidsfile = os.path.join(bidsdir, case[0])
        replacefile = os.path.join(replacedir, "bad_" + filename)
        if not os.path.exists(replacefile):
            # move the bad bidsfile
            shutil.move(badbidsfile, replacefile)
        # copy the good niftifile into the bids directory
        goodfile = os.path.join(niftidir, niftifile)
        shutil.copyfile( goodfile, badbidsfile)
