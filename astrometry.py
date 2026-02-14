#--------------------------------------------------------------------------------------------------#
# astrometry.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Functions related to plate solve by astrometry                                                   #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2026.01.22: 1st coding                                                                    #
# update 2026.01.26: support tqdm with solve-field                                                 #
# bugfix 2026.01.27: avoid unexpected error when over-writing output file existed                  #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import subprocess
from os import remove, path

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
def platesolve(
        filePATH: str,
        solve_option: dict,
        async_process: bool = False,
        jupyter_env: bool = False 
        ):
    """
    Plate solve an image by astrometry.net (local)

    Parameters
    ----------
    filePATH: `str`
        PATH of image file
    solve_option: `dict`
        options for astrometry
    async_process: `bool`
        run solve field as asynchronous process. Default is False
    jupyter_env: `bool`
        using jupyter notebook enviroment. Default is False

    Returns
    -------
    result_path: `str`
        PATH of output FITS file with WCS
    astrometry_result: `bool`
        solve field succeed or not

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
    """
    cmd = "solve-field" + " " + filePATH.replace(' ',r'\ ')
    for f in solve_option:
        if solve_option[f] == True:
            cmd = cmd + " " + f
        elif solve_option[f] == False or solve_option[f] == None:
            continue
        else:
            cmd = cmd + " " + f + " " + str(solve_option[f]).replace(' ',r'\ ')
    
    result_path = solve_option["-N"]
    remove(result_path) if path.exists(result_path) else None

    if async_process:
        if jupyter_env:
            from tqdm.notebook import tqdm
        else:
            from tqdm import tqdm
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE
            )
        while True:
            # Display progress
            line = proc.stdout.readline()
            if line:
                tqdm.write(line.decode(),end="")
            
            if line.decode()[0:15] == "Field 1: solved":
                astrometry_result = True
            
            # Success
            if (not line and proc.poll() is not None):
                astrometry_result = True
                break

            # Failed or timeout
            elif line.decode()[0:22] == "Field 1 did not solve.":
                astrometry_result = False
                tqdm.write("")
                break
    else:
        subprocess.run(
            cmd,
            shell=True
            )
        astrometry_result = path.exists(result_path)
    
    return result_path,astrometry_result

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#