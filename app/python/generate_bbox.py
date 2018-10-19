# coding: utf-8
import os
import configparser
import geojson_to_pixel_arr
import numpy as np
import pandas as pd
from osgeo import gdal

config = configparser.ConfigParser()
config.read('config.ini')

column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']

tif_path = config['FILE_PATHS']['TIF_PATH']
geojson_path = config['FILE_PATHS']['GEOJSON_PATH']

if __name__ == "__main__":
    mylist = []
    converted_files = []
    for raster in os.listdir(tif_path):
        if raster.endswith(".tif"):
            tif_file = os.path.splitext(raster)[0][15:]
            geojson_file = geojson_path+"buildings_"+tif_file+".geojson"
            if os.path.isfile(geojson_file):
                try:
                    pixel_coords, _ = geojson_to_pixel_arr.geojson_to_pixel_arr(tif_path+raster,geojson_file)
                    arr = gdal.Open(tif_path+raster, gdal.GA_ReadOnly).ReadAsArray().shape
                except:
                    print("Some exception occured in parsing geojson file: {}.".format(geojson_file))
                    continue
		converted_files.append(os.path.splitext(raster)[0]+".jpg")
                bbox = []
                for building in pixel_coords:
                    c1 = [x[0] for x in building]
                    c2 = [x[1] for x in building]
                    bbox.append([min(c1), min(c2), max(c1), max(c2)])
                for item in bbox:
                    mylist.append((os.path.splitext(raster)[0]+".jpg",arr[2], arr[1], "building", item[0], item[1],\
                                                        item[2], item[3]))
            else:
                print("geojson corresponding to {} doesn't exist.".format(raster))
    my_df = pd.DataFrame(mylist, columns=column_name)
    my_df.to_csv('ssd_train_labels.csv', index=None)
    with open("converted_files.txt","w") as jpglist:
        for filename in converted_files:
            jpglist.write("{}\n".format(filename))
    test_df = my_df.sample(frac=float(config['PARAMS']['TEST_SIZE']))
    test_df.to_csv("ssd_test_labels.csv", index=None)
    print("SSD style train-test bounding boxes created in csv!")