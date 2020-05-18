import os
import sys
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from collections import namedtuple
import matplotlib.pyplot as plt
import re
import csv
import argparse
from common_utils import vector_operations as vop

parser = argparse.ArgumentParser(description=
    ('This script generates zoning maps from L2A input series'))

parser.add_argument('-i', required=True, metavar='input folder',
                     help='Input folder with L2A products and NDVI files')
parser.add_argument('-o', required=True, metavar='output folder',
                     help='Output folder to store in zoning raster maps')
parser.add_argument('-v', required=True, metavar='input vector',
                     help='Input vector with field borders')
parser.add_argument('-z', required=True, metavar='zoning util',
                     help='Zoning binary util full path')
parser.add_argument('-sd', required=True, metavar='mm-dd - start day',
                     help='Start day to analyze images')
parser.add_argument('-ed', required=True, metavar='mm-dd - end day',
                     help='End day to analyze images')


if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)

args = parser.parse_args()
input_folder = args.i
output_folder = args.o
input_vector = args.v
zoning_path = args.z
start_date = args.sd
end_date = args.ed

