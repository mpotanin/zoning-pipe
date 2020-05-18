import argparse
import sys
import os

imagetiling_base_cmd = ' -of gmxtiles -tt png -nd 0 -r nearest -z 14 '

parser = argparse.ArgumentParser(description=
    ('This script converts ndvi from float to byte and warps to EPSG:3857'))


parser.add_argument('-i', required=True, metavar='input path', 
                    help = 'input folder with float ndvi')
parser.add_argument('-o', required=True, metavar='output path', 
                    help = 'output folder to write to converted ndvi')
parser.add_argument('-it', required=False, metavar='imagetiling path', 
                    help = 'Imagetiling util path')

if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)

args = parser.parse_args()
input_folder = args.i
output_folder = args.o
imagetiling_path = args.it
#gdal_path = args.g

#input_folder = 'C:/work/data/zoning/kyubgau/images/ndvi'
#output_folder = 'C:/work/data/zoning/kyubgau/images/ndvi'
#imagetiling_path = 'C:/work/tilingtools/x64/release'

#if args.g is not null:
imagetiling_base_cmd = imagetiling_path + imagetiling_base_cmd

#input_folder = 'C:\\work\\data\\zoning\\dila\\images\\ndvi_float'


for filename in os.listdir(input_folder):
    if filename.lower().endswith('_ndvi.tif') :
        imagetiling_cmd =  imagetiling_base_cmd + ' -i ' + os.path.join(input_folder,filename)
        print(imagetiling_cmd)
        os.system(imagetiling_cmd)
        


