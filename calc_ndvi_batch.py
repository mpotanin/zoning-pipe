import os
import sys
import re
import numpy as np
import time
import argparse
import raster_proc

parser = argparse.ArgumentParser(description=
    ('This script generates ndvi files in batch mode from S2 raw scenes'))

parser.add_argument('-i', required=True, metavar='input folder',
                     help='Input folder with s2 folders')
parser.add_argument('-o', required=True, metavar='output folder',
                     help='Output folder to store in NDVI files')

if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)
args = parser.parse_args()

input_folder = args.i


for (dirpath, dirnames, filenames) in os.walk(input_folder):
    for file in filenames:
        if (file.endswith('_B04.jp2')) : 
            output_ndvi = args.o + '\\' + file[7:15] + '_ndvi.tif'
            
            raster_proc.create_ndvi_file(dirpath + '\\' + file,
                                        dirpath + '\\' + file.replace('_B04.jp2','_B08.jp2'),
                                        output_ndvi)




