#!/usr/bin/env python

from __future__ import print_function
import argparse
import os
import shutil
import distutils
import sys

def copyDicomFlat(src,dest):
    """Copy source dicom files from src to dest eliminating directories
    in the dest by prefixing files in a directory by 'XX' where XX 
    is the directory number
    """
    # get the list of directories and files in src directory
    dirs, files = getDirectoriesFiles(src)
    
    # copy files first
    copyFiles(src, dest, files)
    
    # cycle through each of the dirs
    for dir in dirs:
        srcpath = os.path.join(src,dir)
        # get dirs and files
        adirs, afiles = getDirectoriesFiles(srcpath)
        # copy the files from this directory
        copyFiles(srcpath, dest, afiles, prefix = dir)

def getDirectoriesFiles(dir):
    """Return list of directories"""
    list = os.listdir(dir)
    dirs = []
    files = []
    for entry in list:
        fullentry = os.path.join(dir, entry)
        if os.path.isdir(fullentry):
            dirs.append(entry)
        else:
            files.append(entry)
    return dirs, files
            
def copyFiles(src, dest, files, prefix=''):
    """Copy files from a src to dest, adding prefix to file at dest"""
    
    # check if prefix is not empty string, then append a '_'
    if prefix != '':
        prefix = prefix + '_'
        
    for file in files:
        srcpath = os.path.join(src,file)
        destpath = os.path.join(dest, prefix + file)
        # import pdb; pdb.set_trace()
        shutil.copyfile(srcpath, destpath)
        
dirs, files = getDirectoriesFiles('1501orig')
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
