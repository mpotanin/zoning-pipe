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


"""
input:
- vector file with field borders
- ndvi geotiff files
- output folder

output:
- subfolders naming after fields' names
- each folder contains:
  - csv file with ndvi mean
  - png plot for each year
  - ndvi geotiff cropped by field border

"""

class NDVIValuesSeries :
    def __init__(self, folder):
        ndvi_files = list()
        for (dirpath, dirnames, filenames) in os.walk(folder):
            for f in filenames:
                if f.endswith('_ndvi.tif'):
                    ndvi_files.append(os.path.join(dirpath,f))

        #ndvi_files = [os.path.join(folder,f)
        #            for f in os.listdir(folder) if re.match('.*_ndvi.tif$',f)]

        self.dates = list()
        self.ndvivalues = list()
        for nf in ndvi_files:
            src_ds = gdal.Open(nf)
            srcband = src_ds.GetRasterBand(1)
            stats = srcband.GetStatistics( True, True )
            if (stats[2]!=0):
                self.dates.append(int(os.path.basename(nf)[:8]))
                self.ndvivalues.append(stats[2]-101)
    
    def save_values_to_csv (self, csv_file, year):
        with open(csv_file,'w', newline='') as file:
            writer = csv.DictWriter(file,fieldnames=['date','ndvi'])
            writer.writeheader()
            ndvi_series_data = list(zip(self.dates, self.ndvivalues))
            for date,ndvi in ndvi_series_data:
                if (int(date/10000) == year):
                    writer.writerow({'date': date,
                                    'ndvi': format(float(ndvi)/100,'.2g')})
            file.close()
        return True

    def plot_values (self, outfile, year):
        min_date = 10000*year + 320
        max_date = 10000*year + 1101
        dates_filt = list()
        values_filt = list()
        dates_filt.append(min_date)
        values_filt.append(0.0)
        for i in range(0,len(self.dates)) :
            if (self.dates[i]>min_date) and (self.dates[i]< max_date):
                dates_filt.append(self.dates[i])
                values_filt.append(self.ndvivalues[i])
        dates_filt.append(max_date)
        values_filt.append(0.0)
        plt.plot(dates_filt,values_filt)
        #plt.figure(figsize=(20,10))
        
        plt.xticks(dates_filt, rotation='vertical',fontsize=8)
        
    
        plt.xlabel('DOY', fontsize=18)
        plt.ylabel('100*NDVI', fontsize=18)
        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(outfile, dpi=100)
        #plt.savefig(outfile,dpi=150)
        plt.close('all')

    def get_values (self,year):
        print()
    def save_to_csv (self, year):
        print()


class NDVIFilesSeries :
    def __init__(self, input_folder):
        self.ndvi_files_list = [os.path.join(input_folder,f) 
                                for f in os.listdir(input_folder) if f.lower().rfind("_ndvi.tif") > 0]
           
    def get_files (self):
        return self.ndvi_files_list




################################################################################################
###MAIN
################################################################################################
parser = argparse.ArgumentParser(description=
    ('This script warps ndvi files and generates ndvi plots'))

parser.add_argument('-i', required=True, metavar='input folder',
                     help='Folder with ndvi byte geotiff files')
parser.add_argument('-f', required=True, metavar='fields',
                     help='Fields EPSG:4326, name column')
parser.add_argument('-gdal', required=True, metavar='gdal bin',
                     help='GDAL bin folder path')
parser.add_argument('-o', required=True, metavar='output',
                     help='Output folder')


if (len(sys.argv) == 1) :
    parser.print_usage()
    exit(0)
args = parser.parse_args()


input_folder = args.i
fields_vector_file = args.f
output_folder = args.o
gdalwarp_base_cmd = args.gdal + '/gdalwarp -srcnodata 0 -dstnodata 0 -of GTiff -crop_to_cutline '



print('---------------Stage I ----------------')
print('Warping NDVI files..') 

ndvi_files = NDVIFilesSeries(input_folder).get_files()
fields_data = vop.vector_file.get_all_geometry(fields_vector_file)

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

srs_4326= osr.SpatialReference()
srs_4326.ImportFromEPSG(4326)


for fd in fields_data:
    field_folder=os.path.join(output_folder,str(fd[0]))
    if not os.path.exists(field_folder) :
        os.mkdir(field_folder)
    shp_file = os.path.join(field_folder,'field_border.shp')
    #NDVIFilesSeries.create_shp(fd[1],shp_file)
    vop.vector_file.create_vector_file(fd[1],shp_file,srs_4326)
    for nf in ndvi_files :
        year = os.path.basename(nf)[0:4]
        cropped_tif = os.path.join(os.path.join(field_folder,year),
                                    os.path.basename(nf))
        if not os.path.exists(os.path.join(field_folder,year)):
            os.mkdir(os.path.join(field_folder,year))

        if os.path.exists(cropped_tif) : 
            os.remove(cropped_tif)
        
        gdalwarp_cmd = (gdalwarp_base_cmd + "-cutline " + fields_vector_file + 
                        '  -cwhere "fid='+ str(fd[0]) + '" ' +
                        nf + ' ' + cropped_tif)
        #print (gdalwarp_cmd)
        os.system(gdalwarp_cmd)

print('---------------Stage II ----------------')
print('Plotting NDVI series..') 

for fd in fields_data: 
    print ('fid = ' + str(fd[0]))
    folder = os.path.join(output_folder,str(fd[0]))
    ndvi_series = NDVIValuesSeries(folder)
    for year in range(2016,2020):
        ndvi_series.plot_values(os.path.join(folder,str(year)+"_ndvi.png"),year)
        ndvi_series.save_values_to_csv(os.path.join(folder,str(year)+'_ndvi.csv'),year)



