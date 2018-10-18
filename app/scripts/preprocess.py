
from __future__ import print_function
from matplotlib.collections import PatchCollection
from osgeo import gdal, osr, ogr, gdalnumeric
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import shutil
import json
import glob
import sys
import os



# This is the directory where the data is located
spacenet_data_dir = '/workspace/data/spacenet_data/'

# This is the directory where this script is located
spacenet_explore_dir = os.path.dirname(os.path.realpath(__file__))

space_utils_dir =  '/workspace/utils'
# import packages
# sys.path.extend([spacenet_explore_dir])
# import geojson_to_pixel_arr, create_dist_map, create_building_mask, \
#         plot_truth_coords, plot_building_mask, plot_dist_transform, \
#         plot_all_transforms

#

# explore N images in 3band data
N_ims = 15

def main():    

    imDir = os.path.join(spacenet_data_dir, '3band')
    vecDir = os.path.join(spacenet_data_dir, 'vectorData/geoJson')
    imDir_out = os.path.join(spacenet_explore_dir, '3band')

    ground_truth_patches = []
    pos_val, pos_val_vis = 1, 255
 
    ########################
    # Create directories

    #coordsDir = spacenet_explore_dir + 'pixel_coords_mask/'
    coords_demo_dir = os.path.join(spacenet_explore_dir, 'pixel_coords_demo')

    maskDir = os.path.join(spacenet_explore_dir, 'building_mask')
    maskDir_vis = os.path.join(spacenet_explore_dir, 'building_mask_vis')
    mask_demo_dir = os.path.join(spacenet_explore_dir, 'mask_demo')

    distDir = os.path.join(spacenet_explore_dir, 'distance_trans')
    dist_demo_dir = os.path.join(spacenet_explore_dir, 'distance_trans_demo')
    
    all_demo_dir = os.path.join(spacenet_explore_dir, 'all_demo')

    # make dirs
    for p in [imDir_out, coords_demo_dir, maskDir, maskDir_vis, mask_demo_dir,
              distDir, dist_demo_dir, all_demo_dir]:
        if not os.path.exists(p):
            os.mkdir(p)

    # get input images and copy to working directory
    rasterList = glob.glob(os.path.join(imDir, '*.tif'))[10:10+N_ims]   
    for im_tmp in rasterList:
        shutil.copy(im_tmp, imDir_out)

if __name__ == '__main__':
    main()             