#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
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
bids_dir = os.path.join(maindir, 'BIDS') # fullpath for BIDS_output
output_dir = os.path.join(maindir,'Derivs','mriqc') # fullpath output
work_dir = os.path.join(maindir,'Work') # fullpath output

container = dicomlist.container_mriqc


# get the participant labels  defined in dicomlist.py
tmplist = []
for i in dicomlist.datasets:
    tmplist.append(i[1])

labels = uniq(tmplist)  # remove duplicate labels
print('number of subjects ',len(labels))

parser = argparse.ArgumentParser(description=
  'Runs the mriqc on labels in  dicomlist.py')

# add arguments for beginning and end cases to process
parser.add_argument('range',
                    help="string like '0-2,5,9-12' specifying \
                    index of subjects or 'all' to run all subjects and \
                    do the group analysis or 'group' to do the \
                    group analysis only",
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

if args.range == 'all':
    
    # do all the participants and group analysis
    cmd = "singularity run --cleanenv \
        -B %s:/data:ro \
        -B %s:/out \
        -B %s:/work \
        %s \
        /data \
        /out \
        participant \
        -w /work \
        --n_procs 8"%(bids_dir, output_dir, work_dir,container)
    
    if args.dryrun:
        print(cmd)
    else:
        print(cmd)
        os.system(cmd)     
    
elif args.range == 'group':
    # do all the participants and group analysis
    cmd = "singularity run --cleanenv \
        -B %s:/data:ro \
        -B %s:/out \
        -B %s:/work \
        %s \
        /data \
        /out \
        group \
        -w /work \
        --n_procs 8"%(bids_dir, output_dir, work_dir,container)
    
    if args.dryrun:
        print(cmd)
    else:
        print(cmd)
        os.system(cmd) 
        
else:
    # just do specific participants
    itemlist = parse_range(args.range)

    for item in itemlist:
        label = labels[item]
    
        #import pdb; pdb.set_trace()
    
        # sample command
        """
        
        http://www.thememolab.org/resources/2018/02/05/running-bidsapps-on-cluster/
    
        Below didn't work without using the -B option to singularity
        singularity run \
        /data/ritcheym/singularity/poldracklab_mriqc_latest-2018-01-18-9c5425cc1abb.img \
        /data/ritcheym/data/fmri/orbit/data/sourcedata/ \
        /data/ritcheym/data/fmri/orbit/data/derivs/mriqc/ \
        participant \
        --participant-label s001 \
        -w /data/ritcheym/data/fmri/orbit/data/work/mriqc/ \
        --n_procs 8
        """
     
        cmd = "singularity run --cleanenv \
            -B %s:/data:ro \
            -B %s:/out \
            -B %s:/work \
            %s \
            /data \
            /out \
            participant \
            --participant-label %s \
            -w /work \
            --n_procs 8"%(bids_dir, output_dir, work_dir,container,label)
        
     
        if args.dryrun:
            print(cmd)
        else:
            print(cmd)
            os.system(cmd)


   
