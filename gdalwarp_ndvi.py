import argparse
import sys
import os

gdalwarp_base_cmd = 'gdalwarp -t_srs "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs" -ot Byte -dstnodata 0 -r cubic -tr 9.554628535647 9.554628535647 '

parser = argparse.ArgumentParser(description=
    ('This script converts ndvi from float to byte and warps to EPSG:3857'))

"""
parser.add_argument('-i', required=True, metavar='input path', 
                    help = 'input folder with float ndvi')
parser.add_argument('-o', required=True, metavar='output path', 
                    help = 'output folder to write to converted ndvi')
parser.add_argument('-g', required=False, metavar='gdal bin path', 
                    help = 'gdal path to bin')
"""
if (len(sys.argv) == 1) :
    parser.print_usage()
    #exit(0)

args = parser.parse_args()
#input_folder = args.i
#output_folder = args.o
#gdal_path = args.g

input_folder = 'C:/work/data/zoning/dila/images/ndvi_float_l8'
output_folder = 'C:/work/data/zoning/dila/images/ndvi_byte_l8'
gdal_path = 'C:/work/tilingtools/gdal223/x64/bin'

#if args.g is not null:
gdalwarp_base_cmd = gdal_path+ "/" + gdalwarp_base_cmd

#input_folder = 'C:\\work\\data\\zoning\\dila\\images\\ndvi_float'


for filename in os.listdir(input_folder):
    if filename.endswith('.tif') or filename.endswith('.TIF'):
        
        gdalwarp_cmd =  (gdalwarp_base_cmd + input_folder + '/'+filename + ' ' + 
                        output_folder + '/'+ filename)
        os.system(gdalwarp_cmd)
        


