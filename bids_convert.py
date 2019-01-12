#!/usr/bin/env python

import argparse
import os
import shutil
import sys

# to do
# add capability to do conversion directly from dicom directory using dm2bids

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
bidsdir = os.path.join(destdir, "BIDS_output")
workdir = os.path.join(destdir, 'Work')
heuristicspath = os.path.join(destdir, "heuristics.py")
# get the number of sessions  defined in dicomlist.py
print('number of sessions ',len(dicomlist.datasets))

parser = argparse.ArgumentParser(description=
    "Converts raw DICOM files in directories to BIDS format based on mapping \
    described in dicomlist.py")

# add arguments for beginning and end cases to process
parser.add_argument('range',
                    help="string like '0-2,5,9-12' specifying index of sessions",
                    type=str)
parser.add_argument('--dcm2bids',help='Use dcm2bids instead of heudiconv',
                    action='store_true')
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')
parser.add_argument('--forcecopy',help='force copy of dicom data',
                    action='store_true')
parser.add_argument('--listing',help='list the sessions with index',
                    action='store_true')
args = parser.parse_args()

if args.listing==True:
    count = 0
    for i in dicomlist.datasets:
        shortpath = i[0]
        subjid = i[1]
        eventid = i[2]
        print(count, subjid,eventid)
        count += 1
    exit()

# go through the datasets defined in dicomlist.py
itemlist = parse_range(args.range)

for d in itemlist:
    i = dicomlist.datasets[d]
    shortpath = i[0]
    subjid = i[1]
    eventid = i[2]
    print(shortpath, subjid,eventid)

    fp_tmpdcm = os.path.join(destdir, tmpdcm) # fullpath of tmp dicom directory
    fp_srcdir = os.path.join(srcdir, shortpath)
    fp_destdir = os.path.join(destdir, tmpdcm, subjid, eventid)

    #import pdb; pdb.set_trace()

    if args.forcecopy:  # whether to copy directory
        # check if fp_destdir exists then delete it
        if os.path.exists(fp_destdir):
            shutil.rmtree(fp_destdir)  # remove if it exists
        # create the new destinaton directory
        os.makedirs(fp_destdir)
        # copy the contents of the fp_srcdir
        # distutils.dir_util.copy_tree(fp_srcdir, fp_destdir) #didn't work
        cmd1 = "cp -rf %s/* %s"%(fp_srcdir, fp_destdir)
    else:
        if not os.path.exists(fp_destdir):
            os.makedirs(fp_destdir)
            # copy the contents of the fp_srcdir
            # distutils.dir_util.copy_tree(fp_srcdir, fp_destdir) #didn't work
            cmd1 = "cp -rf %s/* %s"%(fp_srcdir, fp_destdir)
        else:
            cmd1 = "echo No copy!"

    # cmd to do the conversion
    cmd2 = "singularity run -B %s:/heuristic.py \
    -B %s:/temp_dir \
    -B %s:/output_dir \
    %s \
    --output_dir /output_dir \
    --temp_dir /temp_dir \
    --study_name %s \
    --proc_id %s --subj_id %s  \
    --heuristic /heuristic.py"%(heuristicspath, tmpdcmdir,
        destdir, container, study_name,  eventid, subjid)

    # dcm2bids -d DICOM_DIR -p PARTICIPANT_ID -s SESSION_ID -c CONFIG_FILE -o BIDS_DIR
    ## dcm2bids -d DICOM_DIR -p PARTICIPANT_ID -s SESSION_ID -c CONFIG_FILE -o BIDS_DIR
    cmd3="dcm2bids -d %s -p %s  -s %s -c config.json -o %s --forceDcm2niix --clobber"%(fp_destdir, subjid, eventid, bidsdir)
    
    print(cmd1)
    print(cmd2)
    print(cmd3)
    
    if not args.dryrun:
        os.system(cmd1)
        
        # check which bids conversion program to use
        if args.dcm2bids==True:
            os.system(cmd3)
        else:
            os.system(cmd2)
