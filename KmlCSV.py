# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:55:08 2022

@author: yan-s
"""

from main import VariableGlobal

import logging
from csv import writer
from os.path import exists


class KmlCSV(VariableGlobal):
    """Create a csv file from a googleEarth kml file.

0) __init__() : Initialise, act like a 'main', create DataFrame from list of list from filePrinter(), and save it as .csv file.
1) filePrinter() : Input .kml file & return a list of list ready to be transformed in a .csv file.

Note : Really high chance that it may breaks in the future..
    """

    def __init__(self):
        """Initialise parent, verify if a .kml file is input, 
create a DataFrame from the .kml file using filePrinter() & savec it in a .csv file.
        """
        
        # Initialise the 'parent class' 
        VariableGlobal.__init__(self)
        #
        logging.warning('Start of conversion from kml to csv !')
        
        # Path of kml file
        if not self.kmlSrc:
            # Ask for .kml file path if not provided in __main__
            self.kmlSrc = input(r'Path to googleEarth .kml file :').replace("'", '').replace('"', '')  

        # The basic usage is to first define the rows of the csv file:
        row_list = self.filePrinter(self.kmlSrc)
        
        # Set path of soon to be created .csv file
        self.csvPath = f'{self.workingDirectory}/{self.title}.csv'      
        
        # And then use the following to create the csv file:
        with open(self.csvPath, 'w', newline='', encoding=('utf8')) as file:
            csvWriter = writer(file)
            csvWriter.writerows(row_list)
        logging.warning('End of conversion from kml to csv !\n')

    def filePrinter(self, path):
        """"Return a [list] of every Names and corresponding coordinates,
by reading line by line, corresponding DATA.
        """
        # Create frame of 'return [list]' (=names of Columns)
        out = [["Name", "Longitude", "Latitude", "Altitude"]]
        try:
            # Just a safeguard
            if not exists(path):
                logging.error('This file doesn\'t exist !')
                quit()
            else:
                # Open .kml file
                with open(path, 'r', encoding=('utf8')) as file:
                    logging.debug('Start of file !')
                    # Set [line] for
                    line = []
                    # Read line by line
                    for ligne in file:
                        # Search for tag <title> in file
                        if ligne[:7] == '	<name>':
                            self.title = ligne[7:-8]
                            # And print the title of the file
                            logging.debug(f'Titre : {self.title}')

                        # Search for tag <desription> in file
                        if ligne[:14] == '	<description>':
                            description = ligne[14:-15]
                            # And print the Description of the file
                            logging.debug(f'Description : {description}')

                        # Search for tag <name> in file
                        if ligne[:8] == '		<name>':
                            name = ligne[8:-8]
                            # Retrieve data & add to line
                            line.append(name)

                        # Search for tag <coordinates> in file and -
                        # retrieve Longitude, Latitude & Altitude
                        if ligne[:16] == '			<coordinates>':
                            lonLatAlt = ligne[16:-15]
                            lonLatAlt = lonLatAlt.split(sep=',')
                            # Add each coordinates individually in [line]
                            for i in lonLatAlt:
                                line.append(i)

                        # 1 Name, and 3 coordinates per row
                        if len(line) >= 4:
                            # Add [line] in [out]
                            out.append(line[-4:])
                            # Reset [line]
                            line = []

                    logging.debug('End of file !')
                # Return list of list [out]
                return out
        except Exception as e:
            logging.error('Something gone wrong !')
            print(e)


if __name__ == '__main__':
    print(KmlCSV.__doc__)
