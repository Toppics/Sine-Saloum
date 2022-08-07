# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:44:49 2022

@author: yan-s
"""

import os
import logging


class VariableGlobal:
    """Download satellite map from sentinelhub & plot data from googleEarth .kml file on it.

What it does :    
Script downloading with sentinelhub api map in color with minimal cloud exposure of a box (not too large) input.
Transform a .kml file from GoogleEarth into a .csv file with name and coordinates.
Finally, plot name with coordonates on the sentinelhub map download.
    
How it does:
    using https://docs.sentinel-hub.com/api/latest/

Libraries needed :
    os
    cv2
    csv
    time
    utils
    pandas
    logging
    matplotlib
    sentinelhub (https://sentinelhub-py.readthedocs.io/en/latest/install.html)
    
Minimal input:
    -Sentinelhub Credentials ; Get credentials at https://www.sentinel-hub.com/ .
    -A path to .kml file created with GoogleEarth ; https://earth.google.com/web/ .
    or a csv file with at least 3 columns untitled 'Name', 'Longitude' & 'Latitude' (case sensitive) and using wgs84 coordinate system.
    -A Boundary Box corresponding (not too large) using wgs84 coordinate system ; https://geojson.io/#map=2/20.0/0.0 .
    
Return/create :
    -Directory called "SentinelDownload" containing :
        -A finale .png file.
        -Possibly a .csv file.
        -Subdirectories from sentinelhub containing .json, .tiff & .png file.

Way of improvment :
    -System to import shapefile https://gis.stackexchange.com/a/396133 .
    -Function for calculate if coordinates outside of BBox.
    -Better documentation.
    -Customisation option.

Note :
    Use wgs84 coordinate system.
    Choose BoundaryBox not too large.
    Personnal .csv file MUST have column entitled 'Name', 'Longitude' & 'Latitude' (Case sensitive).
    Add 'Name' in :
        -self.listyDown for annotate 'Name' underneath the point (could leave empty)
        -self.listyUp for annotate 'Name' above the point.
    If 'Name' are UPPER, will annotate them in color.
    For maximum ease in customisation, all variables are in the main script (here).
    """

    def __init__(self):
        """Basically control inputs of all scripts w/ pseudo-global variables"""
        
        "Logging()"
        # Set format for logging outputs
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(levelname)s] %(asctime)s - %(message)s')
        # Block unwanted imported module logging
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('sentinelhub').setLevel(logging.WARNING)
        logging.getLogger('http.client').setLevel(logging.WARNING)
        logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
        logging.getLogger('requests.packages.urllib3').setLevel(logging.WARNING)

        "SentinelHubDownload()"
        
        # Get credentials at https://www.sentinel-hub.com/
        self.instanceID = ''
        self.clientID = ''
        self.clientSecret = ''

        # https://geojson.io/#map=2/20.0/0.0
        # Provide BBox with wgs84 coordinate system
        self.BBox = [-16.900000, 13.600000, -16.300000, 14.200000]

        # Ratio meters/pixel (With this Sat Bands, 30m is max)
        self.resolution = 30

        #Time interval of wanted imagery
        self.timeInterval = "2019-06-01"
        self.intervalTime = "2022-07-25"
        
        "KmlCSV()"
        
        # Give path to .csv file
        # Be sure that columns' name are 'Name', 'Longitude' & 'Latitude'
        # And that coordinates use wgs84 coordinate system
        self.csvSrc = r''
        # Or set path to .kml file to be converted to .csv file
        self.kmlSrc = r'../Sine Saloum 2.0.kml'
        
        "PlotDATA()"
        
        # The figsize parameter takes a tuple of -
        # the height and width of the plot layout
        # Edit it, change the size of the annotations
        self.figSize = (32.0, 24.0)
        
        # Increase DotPerInch for higher resolutions (& more processing time)
        self.dpi = 100.0
        
        #Figure Title & Label (at the bottom of Fig)
        self.figTitle = 'Le Sine Saloum'
        self.xLabel = '05/08/2022'
        
        # Want Grid, else set to false
        self.grid = True
        
        #If true, plot major & minor locator
        self.locator = True
        # Set major
        self.xMajor = 0.05
        self.yMajor = 0.05
        # Set minor
        self.xMinor = 4
        self.yMinor = 4
        
        # Dirty Scale (Set to False if don't want it)
        self.scale = True
        self.xy = (-16.40, 13.6625)
        self.xyText = (-16.3495, 13.6625)
        self.arrowStyle = '<|-|>'
        self.nomenclature = '5 500m'
        self.xyNomenclature = (-16.3835, 13.664)
        
        # Name of city name whos will be moved a litlle upward
        self.listyUp = ['Bambougar Massemba', 'Bangalere', 'Biogane', 'Mar Lodj',
                   'Palmarin Ngethé', 'Soum']
        # Name of city name whos will be moved a litlle downward
        self.listyDown = ['Bambougar Malech', 'Bassar', 'Fayako', 'Diathanor', 'Gagué Mode',
                     'Joal-Fadiout', 'Ndangane Sambou', 'Velingara']
        
        # Coordinates correction & color of "Name":
        # To prevent the "Name" from becoming entangled on the map, -
        # we move some of them a little upward, or downward  -
        # (depend if in listyUp or listyDown).
        
        # UPPER names (could be river or island)
        self.upperLonCorrection = -0.0005
        self.upperLatCorrection = 0.001
        self.upperColor = 'red'
        # Upward names
        self.upwardLonCorrection = -0.01
        self.upwardLatCorrection = 0.001
        self.upwardColor = 'black'
        # Downward names
        self.downwardLonCorrection = -0.013
        self.downwardLatCorrection = -0.004
        self.downwardColor = 'black'
        # Normals ones
        self.normalLonCorrection = 0
        self.normalLatCorrection = 0.001
        self.normalColor = 'black'
        # ArrowColor
        self.arrowColor = 'blue'        
        
        """Basic directory system."""
        # Get the name of the current directory
        currentDirectory = os.path.basename(os.getcwd())
        # Check if already in the right directory
        if currentDirectory != 'SentinelDownload':
            # Will triger only once, while the working directory 
            # will now be in the "SentinelDownload" directory
            logging.warning('Start of SentinelHub downloading !')
            try:
                # Create directory
                os.mkdir('SentinelDownload')
                logging.debug('Directory "SentinelDownload" succesfully created !')
            except FileExistsError:
                logging.debug('Directory "SentinelDownload" already exist !')
            finally:
                # Move in
                os.chdir('SentinelDownload/')
        # Update the working directory
        self.workingDirectory = os.getcwd()


#
if __name__ == '__main__':
    # Trigger the executions sequences.
    try:
        # Import other class()
        from SentinelHubDownload import SentinelHubDownload
        from PlotDATA import PlotDATA
        # Trigger the execution Sequence of SentinelHubDownload()
        exeSeq = SentinelHubDownload()
        exeSeq.exeSeq()
        # Trigger the execution Sequence of PlotData()
        exeSeq = PlotDATA()
        exeSeq.exeSeq()
    except Exception as e:
        print(e)
