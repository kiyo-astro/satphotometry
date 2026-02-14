#--------------------------------------------------------------------------------------------------#
# heavens_above.py                                                                                 #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Retrieve orbit data from heavens-above.com                                                       #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2026.02.13: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import requests
import re
import html
import numpy as np

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
PASSSUMMARY_URL  = "https://www.heavens-above.com/PassSummary.aspx"
PASSDETAIL_URL   = "https://www.heavens-above.com/passdetails.aspx"
PASSSKYCHART_URL = "https://www.heavens-above.com/PassSkyChart2.ashx"
SKYCHART_URL     = "https://www.heavens-above.com/wholeskychart.ashx"

def get_pass_summary(
        norad_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_timezone: str ="UCT"
        ):
    """
    Get satellite pass summary from heavens-above.com

    Parameters
    ----------
    norad_id: `int` or `str`
        NORAD catalog number
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"

    Returns
    -------
    query_result: `str`
        Satellite pass summary (HTML format)

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "satid" : f"{norad_id:.0f}",
        "lat"   : f"{obs_gd_lat_deg:.6f}",
        "lng"   : f"{obs_gd_lon_deg:.6f}",
        "loc"   : "Unspecified",
        "alt"   : f"{obs_gd_height*1000:.0f}",
        "tz"    : f"{ha_timezone}"
        }

    r = requests.get(PASSSUMMARY_URL, params=query_params)
    r.raise_for_status()
    query_result = r.text

    return query_result

def parse_summary2mjd(
        query_result: str
        ):
    """
    Parse satellite pass summary to pass MJD list

    Parameters
    ----------
    query_result: `str`
        Satellite pass summary (HTML format)

    Returns
    -------
    mjds: `np.ndarray`
        Satellite pass MJD list

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    s = html.unescape(query_result)
    mjd_strs = re.findall(r'passdetails\.aspx\?[^"\']*?\bmjd=([0-9.]+)\b', s)
    mjds = [float(x) for x in mjd_strs]
    mjds = np.array(list(dict.fromkeys(mjds)))

    return mjds

def get_pass_detail(
        norad_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_mjd: float,
        ha_timezone: str = "UCT"
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    norad_id: `int` or `str`
        NORAD catalog number
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_mjd: `float`
        MJD at start of satellite pass
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"

    Returns
    -------
    query_result: `str`
        Satellite pass detail (HTML format)

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "lat"   : f"{obs_gd_lat_deg:.6f}",
        "lng"   : f"{obs_gd_lon_deg:.6f}",
        "loc"   : "Unspecified",
        "alt"   : f"{obs_gd_height*1000:.0f}",
        "tz"    : f"{ha_timezone}",
        "satid" : f"{norad_id:.0f}",
        "mjd"   : f"{ha_mjd}",
        "type"  : "V"
        }

    r = requests.get(PASSDETAIL_URL, params=query_params)
    r.raise_for_status()
    query_result = r.text

    return query_result

def parse_detail2passid(
        query_result: str
        ):
    """
    Parse satellite pass summary to satellite pass ID for PassSkyChart query

    Parameters
    ----------
    query_result: `str`
        Satellite pass detail (HTML format)

    Returns
    -------
    pass_id: `str`
        Satellite pass ID for PassSkyChart query

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    m = re.search(r'PassSkyChart2\.ashx\?[^"\']*\bpassID=(\d+)\b', query_result)
    if not m:
        raise ValueError("Error : Pass SKY Chart not found")
    pass_id = m.group(1)

    return pass_id

def get_pass_chart(
        pass_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_timezone: str = "UCT",
        ha_imgsize: int = 800
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    pass_id: `str`
        Satellite pass ID for PassSkyChart query
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"
    ha_timezone: `int`
        Pass Chart image size [pix]. Default is 800

    Returns
    -------
    query_result: `bytes`
        Satellite pass chart image

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "passID"    : f"{pass_id}",
        "size"      : f"{ha_imgsize:.0f}",
        "lat"       : f"{obs_gd_lat_deg:.6f}",
        "lng"       : f"{obs_gd_lon_deg:.6f}",
        "loc"       : "Unspecified",
        "alt"       : f"{obs_gd_height*1000:.0f}",
        "tz"        : f"{ha_timezone}",
        "showUnlit" : "false"
        }

    r = requests.get(PASSSKYCHART_URL, params=query_params)
    r.raise_for_status()
    query_result = r.content

    return query_result

def get_wholeskychart(
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_mjd: float,
        ha_timezone: str = "UCT",
        ha_imgsize: int = 800
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_mjd: `float`
        MJD
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"
    ha_timezone: `int`
        Pass Chart image size [pix]. Default is 800

    Returns
    -------
    query_result: `bytes`
        Satellite pass chart image

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    "lat=0&lng=0&loc=Unspecified&alt=0&tz=UCT&size=800  SL=1&SN=1&BW=1&time=61085.28472&ecl=0&cb=0"
    query_params = {
        "lat"       : f"{obs_gd_lat_deg:.6f}",
        "lng"       : f"{obs_gd_lon_deg:.6f}",
        "loc"       : "Unspecified",
        "alt"       : f"{obs_gd_height*1000:.0f}",
        "tz"        : f"{ha_timezone}",
        "size"      : f"{ha_imgsize:.0f}",
        "SL"        : "1",
        "SN"        : "1",
        "BW"        : "1",
        "time"      : f"{ha_mjd}",
        "ecl"       : "0",
        "cb"        : "0"
        }

    r = requests.get(SKYCHART_URL, params=query_params)
    r.raise_for_status()
    query_result = r.content

    return query_result


#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#