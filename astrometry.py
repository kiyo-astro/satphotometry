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
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import subprocess

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
def platesolve(
        filePATH: str,
        solve_option: dict,
        async_process: bool = False
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

    Returns
    -------
    constants: `numpy.ndarray`
        List of plantetary constants requested

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
    """
    cmd = "solve-field" + " " + filePATH.replace(' ',r'\ ')
    for f in solve_option:
        if solve_option[f] is None:
            cmd = cmd + " " + f
        else:
            cmd = cmd + " " + f + " " + str(solve_option[f]).replace(' ',r'\ ')
    
    result_path = solve_option["-N"]

    if async_process:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT,
            stdout=subprocess.PIPE
            )
    else:
        subprocess.run(
            cmd,
            shell=True
            )
        proc = None
    
    return result_path,None

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#