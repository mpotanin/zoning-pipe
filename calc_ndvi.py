import os
import sys
import gdal, ogr, os, osr
import re
import numpy as np
import time
import argparse
from common_utils import raster_proc




parser = argparse.ArgumentParser(description=
    ('This script generates ndvi GeoTiff byte raster by formulae:'
    'NDVI = 101 + 100*(NIR-RED)/(NIR+RED )'))

parser.add_argument('-red', required=True, metavar='RED band file',
                     help='red band file')
parser.add_argument('-nir', required=True, metavar='NIR band file',
                     help='NIR band file')
parser.add_argument('-o', required=True, metavar='ndvi file',
                     help='Output NDVI GeoTiff file')

if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)
args = parser.parse_args()

start = time.time()

raster_proc.create_ndvi_file(args.red,args.nir,args.o)

print (time.time()-start)