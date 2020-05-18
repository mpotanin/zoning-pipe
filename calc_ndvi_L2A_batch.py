import os
import sys
import gdal, ogr, os, osr
import re
import numpy as np
import time
import argparse
from common_utils import raster_proc 


input_folder = 'D:\\data\\L2\\39UVB'

for (dirpath,dirnames,filenames) in os.walk(input_folder):
    for f in filenames:
        if f.endswith('_SRE_B4.tif'):
            print(f)
            red = os.path.join(dirpath,f)
            nir = red.replace('_SRE_B4.tif','_SRE_B8.tif')
            ndvi = red.replace('_SRE_B4.tif','_SRE_NDVI.tif')
            raster_proc.create_ndvi_file(red,nir,ndvi)