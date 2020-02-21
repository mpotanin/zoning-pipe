import os
import sys
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from collections import namedtuple
import argparse

def run_zoning (vector_file, proc_fields_folder, tiles_folder, output_folder, zoning):
    ds = gdal.OpenEx(vector_file, gdal.OF_VECTOR )
    if ds is None:
        print ("Open failed: " + vector_file)
        sys.exit( 1 )
    zoning_base_cmd = zoning + ' -filt 10 -m quantiles'

    lyr = ds.GetLayer(0)
    lyr.ResetReading()
    for feat in lyr:
        fid_str = str(feat.GetField('fid'))
        print(fid_str)
        zoning_cmd = (zoning_base_cmd + ' -o_geojson ' + 
                        os.path.join(output_folder,fid_str + '.geojson '))
        zoning_cmd += '-v ' + proc_fields_folder + '/' + fid_str + '/field_border.shp '
        zoning_cmd += '-sid \"'
        for i in range(1,7):
            ndvi_date = feat.GetField('img_'+str(i))
            if (ndvi_date is not None) and (ndvi_date!=''):
                zoning_cmd+=os.path.join(tiles_folder,ndvi_date+'_ndvi.tiles') + ','
        
        zoning_cmd=zoning_cmd[:-1] + '\"'
        os.system(zoning_cmd)



################################################################################################
###MAIN
################################################################################################
parser = argparse.ArgumentParser(description=
    ('Runs zoning in batch mode'))

parser.add_argument('-f', required=True, metavar='fields',
                     help='Fields all vector')
parser.add_argument('-p', required=True, metavar='plots folder',
                     help='Plots folder')
parser.add_argument('-n', required=True, metavar='tiles folder',
                     help='Tiles folder')
parser.add_argument('-o', required=True, metavar='output',
                     help='Output folder')
parser.add_argument('-z', required=True, metavar='zoning path',
                     help='Zoning binary path')


if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)
args = parser.parse_args()


run_zoning(args.f,args.p,args.n,args.o,args.z)
exit(0)
