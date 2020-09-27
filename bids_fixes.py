import os
import shutil

# code for fixing bids problems with philips imaging data

def mergeNiftiRuns(fp, destrun = '01', runstr='_run-100_', tmpdir='mergetmp'):
    """
    input is a filepath that includes the run 
    Sometimes dcm2niix saves the each volume as a run
    instead of a single 4D file.
    This function merges all the run-* files together.
    A minor wrinkle is that there some of the files have 
    two digits (e.g. 01-99) or three digits (e.g. 100-350).
    So we have to do these merges separately and then combine
    them into one final file with the specified run
    """

    #fp = '.abc/sub-800_ses_1500_task-resting_run-100_bold.nii.gz'
    
    # get the filename
    fn = os.path.basename(fp)
    part1, part2 = fn.split(runstr)

    # create the temp directory
    os.mkdir(tmpdir)

    # fslmerge commands with run-?? and run-???
    # this is to get the files in proper order for fslmerge
    glob1 = "%s_run-??_%s"%(part1, part2)
    glob2 = "%s_run-???_%s"%(part1, part2)


    niifile1 = os.path.join(tmpdir, part1 + '_1')
    niifile2 = os.path.join(tmpdir, part1 + '_2')
    destfile  = "%s_run-%s_%s"%(part1, destrun, part2)

    # merge the run-?? 
    cmd1 = "fslmerge %s %s"%(glob1, niifile1)
    # merge the run-???
    cmd2 = "fslmerge %s %s"%(glob2, niifile2)
    # merge the two parts into final nii with run-01
    cmd3 = "fslmerge %s %s %s"%(niifile1, niifile2, 
            os.path.join(tmpdir,destfile))

    os.system(cmd1)
    os.system(cmd2)
    os.system(cmd3)

    # do error check if everything OK
    # remove original nifti run files
    globAllRuns = "%s_run-*_%s"%(part1, part2)
    cmdRmFiles = "rm -rf %s"%(globAllRuns)
    os.system(cmdRmFiles)

    # move the new run-01 file from tmpdir to cwd
    os.rename(os.path.join(tmpdir,destfile), destfile)

    # delete the temporary files
    os.remove(niifile1)
    os.remove(niifile2)

    # remove the temp dir
    os.rmdir(tmpdir)



def renameToRun01(filepath):
    """
    dcm2bids bids converter - if there is only one run, 
    it doesn't include the run-01 in the filename.
    This function fixes this problem given a filepath without
    the run-01, it renames all the files:
    including events.tsv, nii and json
    """

