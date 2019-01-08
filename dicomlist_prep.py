#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import shutil
import distutils
import sys

def intro(studyname,src,dest,container):
    """
    studyname = "eyegaze"
    srcdir = '/home/oldserver/eyegazetask'
    destdir = '/home/share/eyegaze_BIDS'
    container = "/home/share/Containers/tjhendrickson-BIDS_scripts-master-latest.simg"
    """
    str=[]
    tmp = "studyname = '%s'\n"%(studyname)
    str.append(tmp)
    tmp = "srcdir = '%s'\n"%(src)
    str.append(tmp)
    tmp = "destdir = '%s'\n"%(dest)
    str.append(tmp)
    tmp = "container = '%s'"%(container)
    str.append(tmp)
    return ''.join(str)

def ds_beg():
    str = "datasets = ["
    return str

def ds_entry(path,subject,session):
    str = "    ['%s', '%03d', '%04d'],"%(path,subject,session)
    return str

def ds_end():
    str = "]"
    return str

def parseStudyname(path):
    """
    Parse the studyname of the given path
    For example: /a/b/c/eyegaze_BIDS this would be eyegaze
    """
    part = path.split('/')[-1]  # get the part we want
    studyname = part.split('_')[0]
    return studyname

srcdir = os.getcwd()

# initialize these items for header
srcdir = '/home/oldserver/eyegazetask'
destdir = '/home/share/eyegaze_BIDS'
container = "/home/share/Containers/tjhendrickson-BIDS_scripts-master-latest.simg"
studyname = "eyegaze"

parser = argparse.ArgumentParser(description=
    """
    Script that prepares a dicomlist.py. The input is a list of the
    paths.  This can be generated while in the source directory
    (e.g. /home/oldserver/eyegazetask) with the following command:

    'find . -name "DICOM" > dirlist.txt'

    """)

# add arguments for beginning and end cases to process
parser.add_argument('--check',help='print diagnostics, path entries, number of entries',
                    action='store_true')
parser.add_argument('subject',help="Starting subject number",
                    type=int)
parser.add_argument('session',help="Starting session number",
                    type=int)

args = parser.parse_args()

# read in dicom directory paths from stdin
dicomdirs = []
for line in sys.stdin:
    if args.check:
        print(line.rstrip())
    dicomdirs.append(line.rstrip())

if args.check:
    print('number of entries ',len(dicomdirs))
    sys.exit()

session=args.session
subject=args.subject

# set study specific info
destdir = os.getcwd()
studyname = parseStudyname(destdir)
srcdir = os.path.join('/home/oldserver', studyname)

print(intro(studyname, srcdir, destdir, container))

print(ds_beg())
for path in dicomdirs:
    #print(path, subject, session)
    print(ds_entry(path,subject,session))
    session+=1
    subject+=1

print(ds_end())
