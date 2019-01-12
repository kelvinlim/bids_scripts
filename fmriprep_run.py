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
parser.add_argument('range',
                    help="string like '0-2,5,9-12' specifying index of subjects",
                    type=str)
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

itemlist = parse_range(args.range)

for item in itemlist:
    label = labels[item]

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
