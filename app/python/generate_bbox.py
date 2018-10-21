# coding: utf-8
import os
from six.moves import configparser
import geojson_to_pixel_arr
import numpy as np
import pandas as pd
from osgeo import gdal

config = configparser.ConfigParser()
config.read('config.ini')

column_name = ['filename', 'width', 'height', 'class', 'xmin', 'ymin', 'xmax', 'ymax']

tif_path = config.get("FILE_PATHS","TIF_PATH")
geojson_path = config.get("FILE_PATHS","GEOJSON_PATH")
output_path = config.get("FILE_PATHS","OUTPUT_PATH")

if __name__ == "__main__":
    mylist = []
    converted_files = []
    for tif_file in os.listdir(tif_path):
        if tif_file.endswith(".tif"):
            file_name = os.path.splitext(tif_file)[0]
            print(file_name)

            # tif file 
            tif_file_path = os.path.join(tif_path, tif_file)

            # geojson file
            geojson_file = "buildings_"+file_name[15:]+".geojson"
            geojson_file_path = os.path.join(geojson_path, geojson_file)
            print(geojson_file_path)
            if os.path.isfile(geojson_file_path):
                try:
                    pixel_coords, _ = geojson_to_pixel_arr.geojson_to_pixel_arr(tif_file_path,geojson_file_path)
                    arr = gdal.Open(tif_file_path, gdal.GA_ReadOnly).ReadAsArray().shape
                except:
                    print("Some exception occured in parsing geojson file: {}.".format(geojson_file))
                    continue
		converted_files.append(os.path.splitext(tif_file)[0]+".jpg")
                bbox = []
                for building in pixel_coords:
                    c1 = [x[0] for x in building]
                    c2 = [x[1] for x in building]
                    bbox.append([min(c1), min(c2), max(c1), max(c2)])
                for item in bbox:
                    mylist.append((os.path.splitext(tif_file)[0]+".jpg",arr[2], arr[1], "building", item[0], item[1],\
                                                        item[2], item[3]))
            else:
                print("geojson corresponding to {} doesn't exist.".format(tif_file))
        if (len(mylist) == 2):
            break
        

    # train data
    my_df = pd.DataFrame(mylist, columns=column_name)
    train_file_path = os.path.join(output_path,'ssd_train_labels.csv' )
    my_df.to_csv(train_file_path, index=None)

    # test data
    test_df = my_df.sample(frac=float(config.get("PARAMS","TEST_SIZE")))
    test_file_path = os.path.join(output_path,'ssd_test_labels.csv' )
    test_df.to_csv( test_file_path, index=None)

    # file to convert to jpg
    convert_file_path = os.path.join(output_path,'converted_files.txt' )
    with open(convert_file_path,"w") as jpglist:
        for filename in converted_files:
            jpglist.write("{}\n".format(filename))

   
    print("SSD style train-test bounding boxes created in csv!")