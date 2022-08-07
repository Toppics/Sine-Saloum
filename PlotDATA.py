# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:58:36 2022

@author: yan-s
"""

from KmlCSV import KmlCSV
from main import VariableGlobal

import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from cv2 import imread, imwrite, IMWRITE_PNG_COMPRESSION
from matplotlib.ticker import MultipleLocator, AutoMinorLocator


class PlotDATA(KmlCSV):
    """Plots DATA on map using Name, Latitude & Longitude (wgs84) of a DataFrame :
    
0) __init__() : If not .csv file provide, will create one using .kml file from GoogleEarth.
1) tiffJPG() : Convert .tiff file from sentinelHubDownload to .png file for using it as a basemap.
2) load() : Load map & .csv file.
3) axes() : Create axes & subplot with BBox, locator & nomenclature.
4) listy() : Create a 2nd DataFrame and move some rows from the 1st in it.
5) plot() : Plot little arrow with coordinates & annotate 'Name' beside.
6) show() : Plot newly created map in the console.
7) save() : Save newly created map locally.
8) exeSeq() : Act as an execution thread.
    
Note : Most of this methods are just containers.
    """

    def __init__(self):
        """Initialise parents class."""
        # Initialise the 'parent class'
        VariableGlobal.__init__(self)
        # Check if a .csv file is provide in __main__
        if not self.csvSrc:
            # Initialise the 'parent class' and so create -
            # a .csv file from a googleEarth .kml file
            KmlCSV.__init__(self)
        else:
            # Use the .csv file provided in __main__
            self.csvPath = self.csvSrc
        # Well,
        logging.warning('Start of DATA plotting !')

    def tiffJPG(self):
        """Convert .tiff file to .png file using cv2."""
        # Get the latest directory and therefore, the latest .tiff file
        latest = sorted([d for d in os.listdir('.') if os.path.isdir(d)],
                        key=lambda x: os.path.getctime(x), reverse=True)[:1]

        # Set path as latest downloaded sentinelHub directory
        filePath = (f'{self.workingDirectory}/{latest[0]}/')

        # Search for .tiff file in latest directory downloaded
        for infile in os.listdir(filePath):
            # Be sure that this is a .tiff file
            if infile.endswith('.tiff'):
                # Print name of .tiff file
                logging.info(f'File found : "{infile}"')
                #
                outfile = infile.split('.')[0] + '.png'
                #
                self.outfilePath = (filePath+outfile)
                # Could check this at the beginning, but just to -
                # be sure to have the right .png file
                # Check if .png file already exist
                if not os.path.exists(self.outfilePath):
                    # Read .tiff file
                    read = imread(filePath + infile)
                    # Write .png file
                    imwrite(self.outfilePath, read, [
                                int(IMWRITE_PNG_COMPRESSION), 0])
                    # Print path of newly created .png file
                    logging.debug(f'Converted succesfully in {outfile} !')
                else:
                    logging.debug(f'But.. File "{outfile}" already exist !')

    def load(self):
        """Load Data."""
        # Load csv
        try:
            dataSrc = self.csvPath
            self.df = pd.read_csv(dataSrc)
            #
            logging.info(f'Load data from "{dataSrc}".')
        except Exception as e:
            print(e)
            quit()

        # Load Map
        try:
            mapSrc = self.outfilePath
            self.loadMap = plt.imread(mapSrc)
            logging.info(f'Load map from "{mapSrc}".')
        except Exception as e:
            print(e)
            exit()

    def axes(self):
        """Create and set parameters of axes.
Parameters :
    
    figSize -> Tuple ; default = (32.0, 24.0)
    # The figsize parameter takes a tuple of -
    # the height and width of the plot layout
    # Edit it, change the size of the annotations
    
    dpi -> float ; default = 100.0
    # Increase DotPerInch for higher resolutions (& more processing time)# Increase DotPerInch for higher resolutions (& more processing time)# Increase DotPerInch for higher resolutions (& more processing time)
    
    figTitle -> str ; default = 'Figure Title'
    # Create figures Title (at the top)
    
    xLabel -> float ; default = 'Label at the Bottom'
    # Create figures Label (at the bottom)
    
    grid -> Bool ; default = True
    # If True, create a grid on the figure
    
    locator -> Bool ; default = True
    # If true, plot major & minor locator
        
        xMajor -> float ; default = 0.05
        # Set x major locator ex: every 0.05°
        yMajor -> float ; default = 0.05
        # Set y major locator ex: every 0.05°
        
        xMinor -> int ; default = 4
        # Set x minor ex: 4 between every 2 major
        yMinor -> int ; default = 4
        # Set y minor ex: 4 between every 2 major
        
    scale -> Bool ; default = True
    # If True, will create a (dirty) scale on the map
    
        xy -> Tuple ; default = (-16.40, 13.6625)
        # Set one coordinates of the first tips of the double arrow
        xyText -> Tuple ; default = (-16.3495, 13.6625)
        # Set the others coordinates of the second tips of the double arrow
        
        arrowStyle -> Str ; default = '<|-|>'
        # Learn more at : https://matplotlib.org/stable/api/_as_gen/matplotlib.patches.ArrowStyle.html
        
        nomenclature -> Str ; default = '5 500m'
        # Set the nomenclature text
        xyNomenclature -> Tuple ; default = (-16.3835, 13.664)
        # Set the nomenclature text coordinates
        """
        # Create subplots with figSize & DPI
        fig, self.ax = plt.subplots(figsize=(self.figSize), dpi=self.dpi)

        # Define the Bounding Box
        self.BBox = [self.BBox[0], self.BBox[2], self.BBox[1], self.BBox[3]]
        # Print BBox
        logging.info(f'Bounding Box is : {self.BBox}.')

        # Set limit with BBox
        self.ax.set_xlim(self.BBox[0], self.BBox[1])
        self.ax.set_ylim(self.BBox[2], self.BBox[3])
        
        # Set Title & Bottom Label
        self.ax.set_title(self.figTitle)
        self.ax.set_xlabel(self.xLabel)

        # Plot Grid
        if self.grid:
            self.ax.grid()

        # Add Locator
        if self.locator:
            # Set major locator
            self.ax.xaxis.set_major_locator(MultipleLocator(self.xMajor))
            self.ax.yaxis.set_major_locator(MultipleLocator(self.yMajor))
            # Set minor locator
            self.ax.xaxis.set_minor_locator(AutoMinorLocator(self.xMinor))
            self.ax.yaxis.set_minor_locator(AutoMinorLocator(self.yMinor))

        #Add dirty Scale
        if self.scale:
            # Create the arrow
            plt.annotate(text='', xy=(self.xy), xytext=(self.xyText),
                         arrowprops=dict(arrowstyle=self.arrowStyle, shrinkA=0, shrinkB=0))
            # Create the nomenclature
            self.ax.annotate(self.nomenclature, self.xyNomenclature)

        # Print Title of Fig
        logging.info(f'Title is "{self.figTitle}".')

    def listy(self):
        """Move to a 2nd DataFrame value of listyDown.
        
Parameters :
    
    listyDown -> List ; default = ['Name']
    # Name of city name whos will be moved a litlle downward -
    # from their real coordinates point + have a little downward arrow
    # Value of list MUST be in 'Name' column of the .csv file
        """
        # Create a 2nd DataFrame for listyDown
        self.df2 = pd.DataFrame({'Name': [], 'Longitude': [],
                                 'Latitude': [], 'Altitude': []})

        # Move 'Downward Name' from df to df2
        for i in self.listyDown:
            #Find index of Name in listyDown
            x = self.df[self.df['Name'] == i].index.values.astype(int)[0]
            #Add row to df2
            self.df2 = pd.concat(
                [self.df.loc[[x]], self.df2], ignore_index=True)
            #And remove row from df
            self.df.drop(index=x, inplace=True)
        #Reset all Index of df
        self.df.reset_index(inplace=True)

    def plot(self):
        """Plot coordinates and place names.

Parameters :
    
    listyUp -> List ; default = ['Name']
    # Name of city name whos will be moved a litlle downward -
    # from their real coordinates point
    # Value of list MUST be in 'Name' column of the .csv file    
    
    # UPPER names (=Specials Ones) :
    
        upperLonCorrection -> float ; default = -0.0005
        # Set longitude correction
        upperLatCorrection -> float ; default = 0.001
        # Set latitude correction
        upperColor -> str ; default = 'red'
        # Set text color
    
    # Upward names (=Will be move a little upward) :
    
        upwardLonCorrection -> float ; default = -0.01
        # Set longitude correction
        upwardLatCorrection -> float ; default = 0.001
        # Set latitude correction
        upwardColor -> str ; default = 'black'
        # Set text color
    
    # Downward names (=Will be move a little downward) :
    
        downwardLonCorrection -> float ; default = -0.013
        # Set longitude correction
        downwardLatCorrection -> float ; default = -0.004
        # Set latitude correction
        downwardColor -> str ; default = 'black'
        # Set text color
    
    # Normals ones :
    
        normalLonCorrection -> float ; default = 0
        # Set longitude correction
        normalLatCorrection -> float ; default = 0.001
        # Set latitude correction
        normalColor -> str ; default = 'black'
        # Set text color
    
    arrowColor -> str ; default = 'blue'
    # Set color of all arrows
        """
        # Annotate city name with arrow p
        # Annotate city name with arrow pointing up (listyUp & 'Normals')
        for idx, dat in self.df.iterrows():
            # If name UPPER = river or island
            if dat.Name.isupper():
                # Annotate in red
                self.ax.annotate(dat.Name, ((dat.Longitude + self.upperLonCorrection),
                                (dat.Latitude + self.upperLatCorrection)), color=self.upperColor)
            else:
                if dat.Name in self.listyUp:
                    # Annotate the city name a little upward
                    self.ax.annotate(dat.Name, ((dat.Longitude + self.upwardLonCorrection),
                                (dat.Latitude + self.upwardLatCorrection)), color=self.upwardColor)
                else:
                    # Annotate the 'Normals Ones'
                    self.ax.annotate(dat.Name, ((dat.Longitude + self.normalLonCorrection),
                                (dat.Latitude + self.normalLatCorrection)), color=self.normalColor)
                    
            # Create the upward arrow
            self.ax.scatter(dat.Longitude, dat.Latitude, zorder=1,
                            alpha=0.8, color=self.arrowColor, s=10, marker='^')

        # Annotate city name with arrow pointing down (listyDown)
        for idx, dat in self.df2.iterrows():
            # Annotate the city name a little downward
            self.ax.annotate(dat.Name, ((dat.Longitude + self.downwardLonCorrection),
                        (dat.Latitude + self.downwardLatCorrection)), color=self.downwardColor)
            
            # Create the downward arrow
            self.ax.scatter(dat.Longitude, dat.Latitude, zorder=1,
                            alpha=0.8, color=self.arrowColor, s=10, marker='v')

    def show(self):
        """Plot map in console."""
        self.ax.imshow(self.loadMap, zorder=0,
                       extent=self.BBox, aspect='equal')

    def save(self):
        """Save file."""
        plt.savefig(f'{self.figTitle}.png', bbox_inches='tight')
        # Print location of the new map
        logging.info(f'Name of file : "{self.workingDirectory}/{self.figTitle}.png"')

    def exeSeq(self):
        """Trigger the execution sequence."""
        self.tiffJPG()
        self.load()
        self.axes()
        self.listy()
        self.plot()
        self.show()
        self.save()
        logging.warning('End of DATA plotting !')


if __name__ == '__main__':
    print(PlotDATA.__doc__)
