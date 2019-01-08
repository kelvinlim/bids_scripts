#!/usr/bin/env python

import argparse
import os
import shutil
import distutils
import  pdb
import sys

parser = argparse.ArgumentParser(description=
    """
    Create the rerun.py containing basd nifti that need to be replaced.
    These are identified by using bids_validator. This is to deal with
    nifti files that produce errors such as Bold scans must be 4 dimensional.

    The input is a text file with pathnames of the bad bold scan nifti files.

    Command to create:
    grep -v Bold < rawrerun.list | grep -v Evidence > rerunlist.txt

    Command:  ../Containers/rerunfile_create.py < rerunlist.txt > rerun.py
    
    filemaps = {
        'task-eyegaze': 'FMRI_EYE_GAZ',
        'task-rest': 'RESTING_FMRI_38_slices'
    }

    cases = [
        ["sub-801/ses-1501/func/sub-801_ses-1501_task-rest_run-01_bold.nii.gz"],
        ["sub-802/ses-1502/func/sub-802_ses-1502_task-eyegaze_run-02_bold.nii.gz"],
        ["sub-803/ses-1503/func/sub-803_ses-1503_task-rest_run-01_bold.nii.gz"],
    ]

    """
    )

# add arguments for beginning and end cases to process
parser.add_argument('--check',help='run check',
                    action='store_true')
args = parser.parse_args()

#pdb.set_trace()

# output filemaps
print("filemaps = {")
print("    'task--eyegaze': 'FMRI_EYE_GAZ',")
print("    'task-rest': 'RESTING_FMRI_38_slices'")
print("}")

# read in the case paths from stdin
cases = []
for line in sys.stdin:
    if args.check:
        print(line.strip())
    cases.append(line.strip())


# go through the cases
print("cases = [")

for case in cases:
    print("    ['%s'],"%(case))
#end of cases
print("]")
