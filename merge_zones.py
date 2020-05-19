import glob, os
import sys
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from collections import namedtuple
import re
import csv
import argparse
from common_utils import vector_operations as vop
from common_utils import raster_proc as rp
import numpy as np


parser = argparse.ArgumentParser(description=
    ('This script merge separate field zones into large raster file'))

parser.add_argument('-i', required=True, metavar='input folder',
                     help='Input folder with separate zones')
parser.add_argument('-o', required=True, metavar='output raster',
                     help='Output raster')

if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)

args = parser.parse_args()

input_folder = args.i
output_merged_raster = args.o

if not os.path.exists(input_folder):
    print("ERROR: path doesn't exist: " + input_folder)
    exit(1)


os.chdir(input_folder)
zone_list = [os.path.join(input_folder,f) for f in glob.glob('*.tif')]

gdal.Warp(output_merged_raster,
                zone_list,
                format = 'GTiff',
                srcNodata=0,
                dstNodata=0
                )