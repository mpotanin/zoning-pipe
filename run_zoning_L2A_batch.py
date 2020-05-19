import os
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

"""
def warp_all_zones (gdalwarp, input_folder, output_gtiff, ends_with):
    warp_cmd = gdalwarp + ' -of GTiff '
    for (dirpath,dirnames,filenames) in os.walk(input_folder):
        for f in filenames:
            if (f.endswith(ends_with)):
                warp_cmd+=os.path.join(dirpath,f) + ' '
    warp_cmd+=output_gtiff
    os.system(warp_cmd)
"""


def clone_with_units_fill (input_raster_file):
    input_ds = gdal.Open(input_raster_file)
    input_band = input_ds.GetRasterBand(1)
    input_array = input_band.ReadAsArray()
    #np.put(input_array,1)
    input_array.fill(1)
    prj_wkt=input_ds.GetProjection()
    geotr = input_ds.GetGeoTransform()
    new_vrt_filename = rp.generate_virtual_random_tif_path()

    #new_vrt_filename = 'C:/work/python/zoning-pipe/rt/zones/units.tif'

    rp.array2raster(new_vrt_filename,[geotr[0],geotr[3]],geotr[1],-geotr[1],prj_wkt,input_array)


    input_ds = None
    return new_vrt_filename




"""
intput:
- folder (L2A + NDVI)
- vector
- output folder
- period
- min ndvi mean value

output:
- zones in raster format 


algorithm:
- loop through vector objects
- filter ndvi by period, mask, ndvi mean
- save vector obj into separate file
- run zoning

"""

#warp_all_zones('gdalwarp','C:\\work\\data\\zoning\\rt\\zones','C:\\work\\data\\zoning\\rt\\zones\\merged_zones.tif','.png')


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
parser.add_argument('-sd', required=True, metavar='mmdd - start day',
                     help='Start day to analyze images')
parser.add_argument('-ed', required=True, metavar='mmdd - end day',
                     help='End day to analyze images')


if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)

args = parser.parse_args()
input_folder = args.i
output_folder = args.o
input_vector = args.v
zoning_path = args.z
start_day = int(args.sd)
end_day = int(args.ed)
min_ndvi = 0.35

if not os.path.exists(input_vector):
    print ("ERROR: file doesn't exist: " + input_vector)
    exit(1)

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

srs_4326 = osr.SpatialReference()
res = srs_4326.ImportFromEPSG(4326)

vector_objects = vop.vector_file.get_all_geometry_in_wkt(input_vector,srs_4326)

for geom in vector_objects:
    tmp_geojson = os.path.join(output_folder,str(geom[0])+'.geojson')
    vop.vector_file.create_vector_file(geom[1],tmp_geojson,srs_4326)

    print(str(geom[0]))
    count = 0
    warp_error = False
    NDVI_valid_files = list()
    for (dirpath,dirnames,filenames) in os.walk(input_folder):
        for f in filenames:
            if f.endswith('_NDVI.tif'):
                day = (int(f[11:19]) % 10000)
                if ((day<start_day) or (day>end_day)): break
                #filter band 4: all pixels > 0
                #filter cloud mask: all pixels = 0 or 131
                #filter NDVI: mean value > min_ndvi
                #wapr NDVI, save geojson
                #zoning
                ndvi_file = os.path.join(dirpath,f)
                cloud_mask = os.path.join(dirpath,'MASKS/' + f.replace('_SRE_NDVI.tif','_CLM_R1.tif' ))
                B4_file = ndvi_file.replace('_NDVI.tif','_B4.tif')

                tmp_vrt_file = rp.generate_virtual_random_tif_path()
                
                #tmp_vrt_file = 'C:/work/python/zoning-pipe/rt/zones/with_zeros.tif'

                #TODO1: extract BBOX from input raster and check if it intersects with field vector

                
                if not rp.crop_raster_file_to_cutline(B4_file,tmp_vrt_file,tmp_geojson,None,0):
                    warp_error = True
                    break
                tmp_vrt_file_units = clone_with_units_fill(tmp_vrt_file)
                rp.crop_raster_file_to_cutline(tmp_vrt_file,tmp_vrt_file_units,tmp_geojson,20000,None)
                B4_ds = gdal.Open(tmp_vrt_file_units)
                B4_band= B4_ds.GetRasterBand(1)
                B4_array = B4_band.ReadAsArray()
                B4_ds = None
                if not np.all((B4_array>0)): break
                #else: print('B4: ' + f)
                

                tmp_vrt_file = rp.generate_virtual_random_tif_path()
                rp.crop_raster_file_to_cutline(cloud_mask,tmp_vrt_file,tmp_geojson,0,0)
                mask_ds = gdal.Open(tmp_vrt_file)
                mask_band= mask_ds.GetRasterBand(1)
                mask_array = mask_band.ReadAsArray()
                mask_ds = None
                if not np.all((mask_array == 0)): break
                #else: print('MASK: ' + f)


                tmp_vrt_file = rp.generate_virtual_random_tif_path()
                rp.crop_raster_file_to_cutline(ndvi_file,tmp_vrt_file,tmp_geojson,0,0)
                ndvi_ds = gdal.Open(tmp_vrt_file)
                ndvi_band = ndvi_ds.GetRasterBand(1)
                ndvi_stats = ndvi_band.GetStatistics( True, True )
                ndvi_ds = None
                if (ndvi_stats[2]<min_ndvi*100 + 101): break
                #else: print ('NDVI: ' + f)
                count+=1
                NDVI_valid_files.append(ndvi_file)
                
        if (warp_error):
            print ('WARP_ERROR')
            break

    print ('VALID: ' + str(count))
    if (count > 0):
    #TODO1: exclude redundant NDVI files by date
        sid_param = str()
        for nf in NDVI_valid_files:
            sid_param+=nf + ','
        sid_param = sid_param[:-1]
        cmd_zoning = (zoning_path + ' -filt 10 -m quantiles -v ' + tmp_geojson + 
                        ' -sid ' + sid_param + ' -o_tif ' + tmp_geojson.replace('.geojson','.tif'))
        print(cmd_zoning)	
        os.system(cmd_zoning)






