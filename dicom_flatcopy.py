#!/usr/bin/env python

import argparse
import os
import shutil
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


#===========================================================================


parser = argparse.ArgumentParser(description=
    "Copy source dicom files from src to dest eliminating directories \
    in the dest by prefixing files in a directory by 'XX' where XX \
    is the directory number")

# add arguments for beginning and end cases to process
parser.add_argument('srcdir',
                    help="source DICOM directory", type=str)
parser.add_argument('desdir',
                    help="destination DICOM directory", type=str)

parser.add_argument('--debug',help='set to debug',
                    action='store_true')
parser.add_argument('--dryrun',help='show cmd but do not run',
                    action='store_true')

args = parser.parse_args()

copyDicomFlat(args.srcdir, args.desdir)
