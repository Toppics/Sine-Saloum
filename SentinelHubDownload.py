# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 09:46:12 2022

@author: yan-s
"""

from main import VariableGlobal

import os
import logging
from time import sleep
from utils import plot_image

from sentinelhub import (
    CRS,
    BBox,
    SHConfig,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SentinelHubRequest,
    bbox_to_dimensions,
)


class SentinelHubDownload(VariableGlobal):
    """Download satellite DATA using SentinelHub Api :
 
0) __init__() : Initialise parent class VariableGlobal().  
1) config() : Load  Sentinelhub credentials in config() & check it.
2) sentinelParameters() : Set resolution, BBox & prepare evalscript.
3) preRequest() : Prepare the request with config & all parameters.
4) retrieveData() : Do the actual request & use already download DATA if on computer.
5) exeSeq() : Act as an execution thread.
 
Note : Read more at https://docs.sentinel-hub.com/api/latest/
    """

    def __init__(self):
        """Initialise parent class VariableGlobal()."""
        # Initialise the 'parent class'
        VariableGlobal.__init__(self)

    def config(self):
        """Load config and check SentinelHub credentials."""
        
        # Create object from SHConfing()
        config = SHConfig()
        # Pass credetials
        config.instance_id = self.instanceID
        config.sh_client_id = self.clientID
        config.sh_client_secret = self.clientSecret

        # Check if correct credentials
        if not config.sh_client_id or not config.sh_client_secret:
            logging.warning("Warning! To use Process API, please provide the credentials (OAuth client ID and client secret).")
        return config

    def sentinelParameters(self):
        """Set resolution, BBox & prepare evalscript."""
        # Set satellite pixel resolution (with this band, 30m is minimum)
        resolution = self.resolution
        # Set Boundary Box of the wanted area
        self.sentinelBBox = BBox(bbox=self.BBox, crs=CRS.WGS84)
        self.sentinelSize = bbox_to_dimensions(
            self.sentinelBBox, resolution=resolution)

        logging.info(f"Image shape at {resolution} m resolution: {self.sentinelSize} pixels")

        # Evalscript, see more at :
        # https://docs.sentinel-hub.com/api/latest/evalscript/
        self.evalscript = """
        //VERSION=3
        function setup() {
          return {
            input: ["B02", "B03", "B04", "CLM"],
            output: 
                { bands: 3 }
          }
        }

        function evaluatePixel(sample) {
          if (sample.CLM == 1) {
            return [0.75 + sample.B04, sample.B03, sample.B02]
          }
          return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
        }
        """

    def preRequest(self):
        """Prepare request with config & parameters."""
        # Prepare sentinelhub downloading request
        self.request_true_color = SentinelHubRequest(
            data_folder=self.workingDirectory,
            evalscript=self.evalscript,
            input_data=[
                SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L1C,
                    time_interval=(self.timeInterval, self.intervalTime),
                    mosaicking_order=MosaickingOrder.LEAST_CC,
                )
            ],
            responses=[SentinelHubRequest.output_response(
                "default", MimeType.TIFF)],
            bbox=self.sentinelBBox,
            size=self.sentinelSize,
            config=self.config(),
        )

    def retrieveData(self):
        """Query for data & check if already exist on the computer.
        If yes, use local sources.
        """
        # Get data
        self.request_true_color.get_data(save_data=True)

        # Print location data
        print("\nThe output directory has been created and a tiff file "+\
              "true color was saved into the following structure:\n")

        for folder, _, filenames in os.walk(self.request_true_color.data_folder):
            for filename in filenames:
                print(os.path.join(folder, filename))

        # Get Map
        data_mask = self.request_true_color.get_data()
        # Plot Map on console with the least cloud exposure, more at :
        # https://docs.sentinel-hub.com/api/latest/user-guides/cloud-masks/
        plot_image(data_mask[0], factor=1 / 255)
        # Just some decorations
        sleep(0.5)
        print('\n')

    def exeSeq(self):
        """Trigger the execution sequence."""
        self.config()
        self.sentinelParameters()
        self.preRequest()
        self.retrieveData()
        logging.warning('End of SentinelHub downloading !\n')


if __name__ == '__main__':
    print(SentinelHubDownload.__doc__)
