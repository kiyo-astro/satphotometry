#--------------------------------------------------------------------------------------------------#
# noirlab.py (formaly Check_DECam_Data_Availability.py)                                            #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Check DECam data availability from NOIRLab API with EXPNUM                                       #
# This code is based on RECA project "get_decam_data.py" as a partial reference                    #
# This code is written for ASTR 499 undergraduate research with Dr. Meredith                       #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.11.01: 1st coding                                                                    #
# update 2025.11.02: add parallelization & retries                                                 #
# update 2025.11.09: add image download function (retrieve_fits)                                   #
# copied 2025.11.22: for satphotometry module                                                      #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import requests
import json

from astropy.utils.data import download_file
import shutil

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
def retrieve_info(expnum):
    """
    Retrieve DECam image metadata from NOIRLab API

    Parameters
    ----------
    expnum: `int`
        exposure number of DECam image

    Returns
    -------
    query_result: `dict`
        DECam image metadata

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    natroot = 'https://astroarchive.noirlab.edu'
    adsurl = f'{natroot}/api/adv_search'

    jj = {
        "outfields" : [
            "md5sum",           # FOR URL
            "archive_filename", # FILE NAME
            "filesize",         # FILE SIZE
            "dateobs_center",   # OBSERVATION DATE (CENTER)
            "dateobs_min",      # OBSERVATION DATE (START)
            "dateobs_max",      # OBSERVATION DATE (END)
            "EXPNUM",           # EXPNUM
            "MAGZERO",          # ZEROPOINT MAGNITUDE
            "AIRMASS",          # AIRMASS
            "SEEING",           # SEEING
        ],
        "search" : [
            ["instrument", "decam"],
            ["proc_type", "instcal"],
            ["EXPNUM", expnum, expnum],  # requires a range
            ["prod_type", "image"],
        ]
    }
    apiurl = f'{adsurl}/find/?limit=20'
    # print(f'Connecting noirlab API (URL : {apiurl})')
    response = requests.post(apiurl, json=jj)
    data = json.loads(response.text)
    try:
        query_result = data[1:][0]  # there should be just 1 row
        if len(query_result) == 0:
            query_result = None
    except:
        query_result = None

    return query_result

def retrieve_infos(expnum_min,expnum_max,instrument="decam",proc_type="instcal",prod_type="image"):
    """
    Retrieve DECam image metadata from NOIRLab API

    Parameters
    ----------
    expnum_min: `int`
        minimum value of range of exposure number of DECam image to search
    expnum_max: `int`
        maximum value of range of exposure number of DECam image to search
    instrument: `str`, optional
        Intrument for DECam image to search. Default is "decam"
    proc_type: `str`, optional
        Proc type for DECam image to search. Default is "instcal"
    prod_type: `str`, optional
        Prod type for DECam image to search. Default is "image"

    Returns
    -------
    query_result: `dict`
        multiple DECam image metadata

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    natroot = 'https://astroarchive.noirlab.edu'
    adsurl = f'{natroot}/api/adv_search'

    jj = {
        "outfields": [
            "md5sum",           # FOR URL
            "archive_filename", # FILE NAME
            "filesize",         # FILE SIZE
            "dateobs_center",   # OBSERVATION DATE (CENTER)
            "dateobs_min",      # OBSERVATION DATE (START)
            "dateobs_max",      # OBSERVATION DATE (END)
            "EXPNUM",           # EXPNUM
            "AIRMASS",          # AIRMASS
            "SEEING",           # SEEING
            "MAGZERO",          # ZEROPOINT MAGNITUDE
        ],
        "search": [
            ["instrument", instrument],
            ["proc_type", proc_type],
            ["EXPNUM", expnum_min, expnum_max+1],  # requires a range in adv_search
            ["prod_type", prod_type],
        ]
    }
    apiurl = f'{adsurl}/find/?limit={0}'.format(expnum_max-expnum_min+1)
    # print(f'Connecting noirlab API (URL : {apiurl})')
    response = requests.post(apiurl, json=jj)
    data = json.loads(response.text)
    try:
        query_result = data[1:]  # there should be just 1 row
        if len(query_result) == 0:
            query_result = None
    except:
        query_result = None
    
    return query_result

def retrieve_fits(md5sum,save_path,detector=None):
    """
    Retrieve image metadata from NOIRLab API

    Parameters
    ----------
    md5sum: `str`
        md5sum
    save_path: `str`
        FITS file save PATH (including file name and extension)
    detector: `int`, optional
        detector number. Default is None (retrive all detectors' images and save as one FITS file)

    Returns
    -------
    save_path: `str`
        FITS file save PATH (including file name and extension)

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    natroot = 'https://astroarchive.noirlab.edu'
    if detector is None:
        access_url = f'{natroot}/api/retrieve/{md5sum}'
    else:
        access_url = f'{natroot}/api/retrieve/{md5sum}/?hdus={detector}'
    
    # will be modified in the future to use requests
    filename = download_file(access_url, cache=True)
    shutil.copy(filename,save_path)

    return save_path

import requests
import shutil

def retrieve_fits_nocash(md5sum, save_path, detector=None):
    """
    Retrieve image metadata from NOIRLab API without leaving any cash file

    Parameters
    ----------
    md5sum: `str`
        md5sum
    save_path: `str`
        FITS file save PATH (including file name and extension)
    detector: `int`, optional
        detector number. Default is None (retrieve all detectors' images)

    Returns
    -------
    save_path: `str`
        FITS file save PATH (including file name and extension)

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """

    natroot = 'https://astroarchive.noirlab.edu'
    if detector is None:
        access_url = f'{natroot}/api/retrieve/{md5sum}'
    else:
        access_url = f'{natroot}/api/retrieve/{md5sum}/?hdus={detector}'

    # --- Use requests instead of download_file ---
    try:
        response = requests.get(access_url, stream=True)
        response.raise_for_status()  # HTTPエラー時に例外を発生

        # Save to file
        with open(save_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        return save_path

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to retrieve FITS from {access_url}")
        print(e)
        return None

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#
# query_result = retrieve_infos(145425,148689)
# query_result = retrieve_info(148689)
# breakpoint()
# with open('/Users/kiyoaki/VScode/ASTR499/input/decam_streak_list/streaks_metadata_backup.json','w') as metadata_backup:
#     json.dump(query_result, metadata_backup, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))