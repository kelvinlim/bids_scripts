#!/usr/bin/env python

# Kelvin O. Lim 20181231

import argparse
import os
import shutil
import distutils

import sys

#  add cwd to beginning of path to insure import is from current directory
sys.path.insert(0, os.getcwd()) 
import dicomlist

print(dicomlist.studyname)
