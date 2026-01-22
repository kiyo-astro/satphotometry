#--------------------------------------------------------------------------------------------------#
# fitsparser.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Handle FITS metadata                                                                             #
# This code is written for ASTR 499 undergraduate research with Dr. Meredith                       #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.11.23: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
from astropy.io import fits
from astropy.wcs import WCS
from astropy.table import Table

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
class LEOfitsparser:
    """
    Functions for FITS with LEO objects
    
    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    def parse_metadata(main_header,ccd_header,main_keys=[],ccd_keys=[],wcs=False,return_table=False):
        """
        Parse FITS metadata for satellite streak analysis (primary for DECam)

        Parameters
        ----------
        main_header: `astropy.io.fits.header.Header`
            primary header
        ccd_header: `astropy.io.fits.header.Header`
            detector header
        main_keys: `list`, optional
            custome keys to read for primary header. Default is []
        ccd_keys: `list`, optional
            custome keys to read for detector header. Default is []
        wcs: `bool`, optional
            if True, output includes WCS related keys. Default is False
        return_table: `bool`, optional
            if True, return as astropy Table format. Default is False


        Returns
        -------
        metadata: `astropy.io.fits.header.Header` or `astropy.table.table.Table`
            metadata for satellite streak analysis

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
        """
        keys = [
            "OBSID",        # noirlab ID
            "EXPNUM",       # expnum
            "INSTRUME",     # Instrument
            "TELESCOP",     # telescope
            "OBSERVAT",     # observatory
            "OBS-LONG",     # longitude
            "OBS-LAT",      # latitude
            "OBS-ELEV",     # elevation
            "OBSERVER",     # observer
            "PROPID",       # Proposal ID
            "DATE-OBS",     # timestamp (start)
            "MJD-OBS",      # timestamp (MJD start)
            "MJD-END",      # timestamp (MJD end)
            "TIMESYS",      # time system
            "EXPREQ",       # Requested exposure duration
            "EXPTIME",      # Exposure duration
            "EXPDUR",       # Exposure duration
            "FILTER",       # filter
            "PIXSCAL1",     # pixel scale axis1
            "PIXSCAL2",     # pixel scale axis2
            "AIRMASS",      # airmass
            "SEEING",       # seeing [arcsec]
            "SEEINGP",      # seeing [pix]
            "MAGZERO",      # zeropoint
            "WINDSPD",      # wind speed
            "WINDDIR",      # wind direction
            "SKYNOISE",     # sky noise [adu]
        ]

        keys.extend(main_keys)

        if return_table is True:
            data_dict = {}
            for key in keys:
                data_dict[key] = [main_header.get(key, ccd_header.get(key, None)),main_header.comments[key] if key in main_header else (ccd_header.comments[key] if key in ccd_header else None)]
        else:
            metadata = fits.Header()
            for key in keys:
                value = main_header.get(key, ccd_header.get(key, 'NaN     '))
                comment = main_header.comments[key] if key in main_header else (ccd_header.comments[key] if key in ccd_header else "")
                metadata.set(key, value, comment)

        keys = [
            "CCDNUM",       # ccdnum
            "DETPOS",       # detector position ID
            "NAXIS",        # NAXIS
        ]

        keys.extend(ccd_keys)

        if return_table is True:
            for key in keys:
                data_dict[key] = [ccd_header.get(key, main_header.get(key, None)),ccd_header.comments[key] if key in ccd_header else (main_header.comments[key] if key in main_header else None)]
        else:
            for key in keys:
                value = ccd_header.get(key, main_header.get(key, 'NaN     '))
                comment = ccd_header.comments[key] if key in ccd_header else (main_header.comments[key] if key in main_header else "")
                metadata.set(key, value, comment)

        if wcs is True:
            try:
                naxis = data_dict["NAXIS"][0] if return_table is True else metadata["NAXIS"]
                for i in range(0,naxis):
                    key = "NAXIS{0}".format(str(i+1))
                    value = ccd_header.get(key, 'NaN     ')
                    comment = ccd_header.comments[key] if key in ccd_header else ""
                    if return_table is True:
                        data_dict[key] = [value,comment]
                    else:
                        metadata.set(key, value, comment)
            except KeyboardInterrupt:
                pass
            
            try:
                wcs_header = WCS(ccd_header).to_header(relax=True)
                for key in wcs_header:
                    value = wcs_header[key]
                    comment = wcs_header.comments[key]
                    if return_table is True:
                        data_dict[key] = [value,comment]
                    else:
                        metadata.set(key, value, comment)
            except:
                pass
        
        if return_table is True:
            metadata = Table(data_dict)
        
        return metadata

class ASTR499:
    """
    Functions for ASTR499 Undergraduate Research Project for Kiyoaki Okudaira supervised by Dr. Meredith Rawls
    
    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    def integrate_ALEX_metadata(metadata,streak_list_row):
        """
        Integrate metadata from FITS file with DECam streak list data

        Parameters
        ----------
        metadata: `astropy.io.fits.header.Header`
            metadata for satellite streak analysis
        streak_list_row: `astropy.table.table.Table`
            one row of the DECam streak list read as astropy table

        Returns
        -------
        metadata: `astropy.io.fits.header.Header`
            integrated metadata for satellite streak analysis

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
        """
        metadata.set("MD5SUM", streak_list_row["md5sum"], "Checksum of file at NOIRLab API")
        metadata.set("FILENAME", streak_list_row["archive_filename"], "Archive filename at NOIRLab API")

        metadata.set("SAT-STID", streak_list_row["streakID"], "Satellite streak ID")

        metadata.set("SAT-RA1", streak_list_row["ra_1"], "[deg] Right ascension of satellite streak")
        metadata.set("SAT-DEC1", streak_list_row["dec_1"], "[deg] Declination of satellite streak")
        metadata.set("SAT-RA2", streak_list_row["ra_2"], "[deg] Right ascension of satellite streak")
        metadata.set("SAT-DEC2", streak_list_row["dec_2"], "[deg] Declination of satellite streak")
        metadata.set("SAT-RA3", streak_list_row["ra_3"], "[deg] Right ascension of satellite streak")
        metadata.set("SAT-DEC3", streak_list_row["dec_3"], "[deg] Declination of satellite streak")
        metadata.set("SAT-RA4", streak_list_row["ra_4"], "[deg] Right ascension of satellite streak")
        metadata.set("SAT-DEC4", streak_list_row["dec_4"], "[deg] Declination of satellite streak")

        metadata.set("SAT-WID", streak_list_row["width"], "[arcsec] Width of satellite streak")
        metadata.set("SAT-LEN", streak_list_row["height"], "[arcsec] Length of satellite streak")

        return metadata

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#