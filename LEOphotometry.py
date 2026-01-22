#--------------------------------------------------------------------------------------------------#
# LEOphotometry.py                                                                                 #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Photometry LEO satellite streaks                                                                 #
# This code is written for ASTR 499 undergraduate research with Dr. Meredith                       #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.11.22: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import numpy as np
import matplotlib as plt
from scipy.optimize import curve_fit
import itertools
from astropy.coordinates import SkyCoord
import astropy.units as u

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
def radec_to_pixel(ra_deg,dec_deg,wcs_obj,origin=0):
    """
    Convert coordinate from RA-Dec to pixel X-Y

    Parameters
    ----------
    ra_deg: `float`
        Right Ascension [deg]
    dec_deg: `float`
        Declination [deg]
    wcs_obj: `astropy.wcs.wcs.WCS`
        wcs object
    origin: `int`, optional
        origin of list. Default is 0

    Returns
    -------
    [x_pix,y_pix]: `list`
        pixel coordinate X-Y

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    skycoord = SkyCoord(ra_deg * u.deg, dec_deg * u.deg, frame='icrs')
    
    x_pix, y_pix = wcs_obj.world_to_pixel(skycoord)
    if origin == 1:
        x_pix += 1
        y_pix += 1

    return [x_pix,y_pix]

def img_mask(image_data,threshold=None):
    """
    Apply a mask to an image using a threshold

    Parameters
    ----------
    image_data: `np.ndarray`
        image data in a NumPy array
    threshold: `int` or `float`, optional
        image data in a NumPy array. Default is None (Automatically determine threshold by 3 sigma)

    Returns
    -------
    masked_data: `np.ndarray`
        masked data in a NumPy array

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    if threshold is None:
        threshold = np.mean(image_data) + 3*np.std(image_data)
    masked_data = np.ma.array(image_data,mask=(threshold<image_data))
    return masked_data

def count_1d(image_data,count_axis=1):
    """
    Calculate the total of the axial count values

    Parameters
    ----------
    image_data: `np.ndarray`
        image data in a NumPy array
    count_axis: `int`, optional
        axis of counting direction. Default is 1

    Returns
    -------
    counts: `np.ndarray`
        list of count values
    coordinates: `np.ndarray`
        list of given axial coordinates

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    counts = np.ma.mean(image_data,axis=count_axis)
    coordinates = np.arange(len(counts))
    return counts,coordinates

def gauss_fitting(counts,coordinates,disp=False):
    """
    apply Gaussian fitting to the count values and find the boundaries of streaks

    Parameters
    ----------
    counts: `np.ndarray`
        list of count values
    coordinates: `np.ndarray`
        list of given axial coordinates
    disp: `bool`, optional
        display results. Default is False

    Returns
    -------
    popt: `np.ndarray`
        Gaussian fitting result parameters
    fitting: `np.ndarray`
        results of Gaussian fitting
    range_min: `float`
        lower bound value of the streak range
    range_max: `float`
        upper bound value of the streak range

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    # define gaussian destribution function
    def gauss_func(x, a, mu, sigma, b):
        return a*np.exp(-(x-mu)**2/(2*sigma**2)) + b

    # param_ini = [counts.max(),np.mean(coordinates),1,np.median(counts)]
    param_ini = [counts.max(),counts.argmax(),1,np.median(counts)]
    popt,_ = curve_fit(gauss_func, coordinates, counts, p0=param_ini,maxfev=1000)
    fitting = gauss_func(coordinates,popt[0],popt[1],popt[2],popt[3])

    range_min = int(popt[1] - 3 * popt[2])
    range_max = int(popt[1] + 3 * popt[2])

    if disp is True:
        print("Fitting results : [x, a, mu, sigma, b] = {0}".format(popt))
        plt.figure(figsize=(10, 10))
        plt.plot(coordinates,counts,label="1D Count")
        plt.plot(coordinates,fitting,label="Gaussian fitting",color='red',linestyle='--')
        plt.axvline(range_min, color='black', linestyle='--', label='streak boarder')
        plt.axvline(range_max, color='black', linestyle='--')
        plt.legend()
    
    return popt,fitting,range_min,range_max

def photometry(image_data,range_min,range_max,arc_per_pix=0.27,zeropoint=None):
    """
    measure the brightness of LEO satellite streak

    Parameters
    ----------
    image_data: `np.ndarray`
        image data in a NumPy array. Must include both background and streak
    range_min: `float`
        lower bound value of the streak range
    range_max: `float`
        upper bound value of the streak range
    arc_per_pix: `float`, optional
        field of view of the telescope [arc/pix] Default is 0.27 (DECam)
    zeropoint: `float`, optional
        zeropoint. Default is None.

    Returns
    -------
    count_pix2: `float`
        brightness of satellite streak [count/(pix^2)]
    count_arc2: `float`
        brightness of satellite streak [count/(arc^2)]
    mag_pix2: `float`, None
        brightness of satellite streak [mag/(pix^2)] Return None if zeropoint is unavailable.
    mag_arc2: `float`, None
        brightness of satellite streak [mag/(arc^2)] Return None if zeropoint is unavailable.

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    streak_region_data = np.array([image_data[i] for i in range(range_min,range_max+1)])
    off_region_data = np.array([image_data[i] for i in itertools.chain(range(0,range_min),range(range_max+1,len(image_data)))])

    sum_off_region = np.sum(off_region_data)
    pixel_off_region = len(off_region_data)*len(off_region_data[0])
    pixcount_off_region = sum_off_region/pixel_off_region

    pixel_streak_region = len(streak_region_data)*len(streak_region_data[0])
    sum_streak_region = np.sum(streak_region_data) - pixcount_off_region*pixel_streak_region

    count_pix2 = sum_streak_region / pixel_streak_region
    count_arc2 = count_pix2 / (arc_per_pix**2)

    if zeropoint is None or zeropoint == "NaN":
        mag_pix2 = None
        mag_arc2 = None
    else:
        mag_pix2 = -2.5*np.log10(count_pix2) + zeropoint
        mag_arc2 = -2.5*np.log10(count_arc2) + zeropoint
    
    return count_pix2,count_arc2,mag_pix2,mag_arc2

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#

