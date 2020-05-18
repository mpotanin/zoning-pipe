import argparse
import sys
import os
import rio_toa.reflectance
from common_utils import raster_proc
from common_utils import vector_operations as vop

################### MAIN block ##############################################
parser = argparse.ArgumentParser(description=
    ('This script calculates TOA and NDVI from L1 LC8 products in batch mode'))

parser.add_argument('-i', required=True, metavar='input path', 
                    help = 'Input folder with Landsat 8 raw downlodaed from Google products')
parser.add_argument('-o', required=True, metavar='output path', 
                    help = 'Output folder to write calculated INDVI')
parser.add_argument('-crop', required=False, metavar='crop cutline',
                     help='Vector cutline')

if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)


args = parser.parse_args()

for dir in (args.i,args.o):
    if (not os.path.exists(dir)) :
        print ("ERROR: path doesn't exist: " + dir)
        exit (1)

in_mem_cutline = None
if args.crop is not None:
    bbox = vop.BBOX.calc_BBOX_from_vector_file(args.crop)
    poly = vop.BBOX.create_ogrpolygon(bbox)
    in_mem_cutline = vop.vector_file.create_virtual_vector_file(
                        poly.ExportToWkt(),
                        vop.vector_file.get_srs_from_file(args.crop))
    poly.ExportToWkt() #TODO - why is it needed ?


for (dirpath, dirnames, filenames) in os.walk(args.i):
    for file in filenames:
        if (file.endswith('_B4.TIF')) :
            print(file)
            red_band = os.path.join(dirpath,file)
            nir_band = red_band.replace('_B4.TIF','_B5.TIF')
            MTL_file = red_band.replace('_B4.TIF','_MTL.txt')

            red_band_toa = red_band.replace('_B4.TIF','_B4_toa.TIF')
            nir_band_toa = nir_band.replace('_B5.TIF','_B5_toa.TIF')
   
            rio_toa.reflectance.calculate_landsat_reflectance([red_band],MTL_file,
                                                            red_band_toa,
                                                            None,{},[4],'uint16',1,False,True)
            rio_toa.reflectance.calculate_landsat_reflectance([nir_band],MTL_file,
                                                            nir_band_toa,
                                                            None,{},[5],'uint16',1,False,True)

            output_ndvi = os.path.join(args.o, file[17:25] + '_l8_ndvi.tif')
            
            if in_mem_cutline is not None:
                raster_proc.crop_raster_file_to_cutline(
                                    red_band_toa,
                                    red_band_toa.replace('.TIF','_cut.TIF'),
                                    in_mem_cutline,0)
                raster_proc.crop_raster_file_to_cutline(
                                    nir_band_toa,
                                    nir_band_toa.replace('.TIF','_cut.TIF'),
                                    in_mem_cutline,0)
                red_band_toa = red_band_toa.replace('.TIF','_cut.TIF')
                nir_band_toa = nir_band_toa.replace('.TIF','_cut.TIF')

            raster_proc.create_ndvi_file(red_band_toa,
                                        nir_band_toa,
                                        output_ndvi)
            
            if in_mem_cutline is not None:
                os.remove(red_band_toa)
                os.remove(nir_band_toa)
            
            #exit(0)