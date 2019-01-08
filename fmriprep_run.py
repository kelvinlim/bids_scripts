#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import shutil
import distutils
import sys

#  add cwd to beginning of path to insure import is from current directory
sys.path.insert(0, os.getcwd()) 
import dicomlist

def uniq(input):
  output = []
  for x in input:
    if x not in output:
      output.append(x)
  return output


maindir = os.getcwd()
bids_dir = os.path.join(maindir, 'BIDS_output') # fullpath for BIDS_output
fmriprep_dir = os.path.join(maindir, 'fmriprep_output') # fullpath for fmriprep
container = '/home/share/Containers/fmriprep-1.2.5.simg'

# get the participant labels  defined in dicomlist.py
tmplist = []
for i in dicomlist.datasets:
    tmplist.append(i[1])

labels = uniq(tmplist)  # remove duplicate labels
print('number of subjects ',len(labels))

parser = argparse.ArgumentParser(description=
  'Script that applies the fmriprep processing pipeline to labels in  dicomlist.py')

# add arguments for beginning and end cases to process
parser.add_argument('beg',help="first element of label array to start, 0 indexed",
                    type=int)
parser.add_argument('end',help="last element of label array to end",
                    type=int)
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')
parser.add_argument('--listing',help='list the subjects with index',
                    action='store_true')
args = parser.parse_args()

if args.listing==True:
    count = 0
    for label in labels:
        print(count, label)
        count += 1
    exit()

# limit the size of labels array based on beg and end arguments
# for 31 element array, to split in two, 0:16, 16:31
labels = labels[args.beg:args.end]

for label in labels:

    #import pdb; pdb.set_trace()

    # sample command
    """
    singularity run -B $BIDS/BIDS_output/:/work -B $BIDS/fmriprep_output:/output \
    $CONTAINER /work /output participant \
    --participant_label 013 \
    --fs-license-file /output/license.txt \
    --use-aroma \
    --use-syn-sdc
    """

    cmd = "singularity run -B %s:/work -B %s:/output \
    -B %s:/main \
    %s /work /output participant \
    --participant_label %s\
    --fs-license-file /main/license.txt \
    --use-aroma \
    -w /main/Work \
    --use-syn-sdc"%(bids_dir, fmriprep_dir, maindir, container, label)

    if args.dryrun:
      print(cmd)
    else:
      print(cmd)
      os.system(cmd)
