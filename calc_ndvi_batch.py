import os
import sys
import re
import numpy as np
import time
import argparse
from common_utils import raster_proc
from common_utils import vector_operations as vop

parser = argparse.ArgumentParser(description=
    ('This script generates ndvi files in batch mode from S2 raw scenes'))

parser.add_argument('-i', required=True, metavar='input folder',
                     help='Input folder with s2 folders')
parser.add_argument('-o', required=True, metavar='output folder',
                     help='Output folder to store in NDVI files')
parser.add_argument('-crop', required=False, metavar='crop cutline',
                     help='Vector cutline')


if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)
args = parser.parse_args()

input_folder = args.i

in_mem_cutline = None
if args.crop is not None:
    bbox = vop.BBOX.calc_BBOX_from_vector_file(args.crop)
    poly = vop.BBOX.create_ogrpolygon(bbox)
    in_mem_cutline = vop.vector_file.create_virtual_vector_file(
                        poly.ExportToWkt(),
                        vop.vector_file.get_srs_from_file(args.crop))
    poly.ExportToWkt() #TODO - why is it needed ?
    

for (dirpath, dirnames, filenames) in os.walk(input_folder):
    for file in filenames:
        if (file.endswith('_B04.jp2')) : 
            output_ndvi = os.path.join(args.o,file[7:15] + '_ndvi.tif')

            red_band = os.path.join(dirpath,file)
            nir_band = os.path.join(dirpath,file.replace('_B04.jp2','_B08.jp2'))

            if in_mem_cutline is not None:
                raster_proc.crop_raster_file_to_cutline(red_band,
                                                        red_band.replace('.jp2','_cut.tif'),
                                                        in_mem_cutline,0)
                raster_proc.crop_raster_file_to_cutline(nir_band,
                                                        nir_band.replace('.jp2','_cut.tif'),
                                                        in_mem_cutline,0)
                red_band = red_band.replace('.jp2','_cut.tif')
                nir_band = nir_band.replace('.jp2','_cut.tif')
                        
            raster_proc.create_ndvi_file(red_band,nir_band,output_ndvi)

            if in_mem_cutline is not None:
                os.remove(red_band)
                os.remove(nir_band)




