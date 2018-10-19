
from __future__ import print_function
#from matplotlib.collections import PatchCollection
from osgeo import gdal, osr, ogr, gdalnumeric
#from matplotlib.patches import Polygon
#import matplotlib.pyplot as plt
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

spacenet_utils_dir =  '/workspace/utils'
# import packages
sys.path.extend([spacenet_utils_dir])
from utils import geoTools as gT

# explore N images in 3band data
N_ims = 15

###############################################################################    
def geojson_to_pixel_arr(raster_file, geojson_file, pixel_ints=True,
                       verbose=False):
    '''
    Tranform geojson file into array of points in pixel (and latlon) coords
    pixel_ints = 1 sets pixel coords as integers
    '''
    
    # load geojson file
    with open(geojson_file) as f:
        geojson_data = json.load(f)

    # load raster file and get geo transforms
    src_raster = gdal.Open(raster_file)
    targetsr = osr.SpatialReference()
    targetsr.ImportFromWkt(src_raster.GetProjectionRef())
        
    geom_transform = src_raster.GetGeoTransform()
    if verbose:
        print ("geom_transform:", geom_transform)
    
    # get latlon coords
    latlons = []
    types = []
    for feature in geojson_data['features']:
        coords_tmp = feature['geometry']['coordinates'][0]
        type_tmp = feature['geometry']['type']
        if verbose: 
            print ("features:", feature.keys())
            print ("geometry:features:", feature['geometry'].keys())

            #print "feature['geometry']['coordinates'][0]", z
        latlons.append(coords_tmp)
        types.append(type_tmp)
        #print feature['geometry']['type']
    
    # convert latlons to pixel coords
    pixel_coords = []
    latlon_coords = []
    for i, (poly_type, poly0) in enumerate(zip(types, latlons)):
        
        if poly_type.upper() == 'MULTIPOLYGON':
            #print "oops, multipolygon"
            for poly in poly0:
                poly=np.array(poly)
                if verbose:
                    print ("poly.shape:", poly.shape)
                    
                # account for nested arrays
                if len(poly.shape) == 3 and poly.shape[0] == 1:
                    poly = poly[0]
                    
                poly_list_pix = []
                poly_list_latlon = []
                if verbose: 
                    print ("poly", poly)
                for coord in poly:
                    if verbose: 
                        print ("coord:", coord)
                    lon, lat, z = coord 
                    px, py = gT.latlon2pixel(lat, lon, input_raster=src_raster, 
                                         targetsr=targetsr, 
                                         geom_transform=geom_transform)
                    poly_list_pix.append([px, py])
                    if verbose:
                        print ("px, py", px, py)
                    poly_list_latlon.append([lat, lon])
                
                if pixel_ints:
                    ptmp = np.rint(poly_list_pix).astype(int)
                else:
                    ptmp = poly_list_pix
                pixel_coords.append(ptmp)
                latlon_coords.append(poly_list_latlon)            

        elif poly_type.upper() == 'POLYGON':
            poly=np.array(poly0)
            if verbose:
                print ("poly.shape:", poly.shape)
                
            # account for nested arrays
            if len(poly.shape) == 3 and poly.shape[0] == 1:
                poly = poly[0]
                
            poly_list_pix = []
            poly_list_latlon = []
            if verbose: 
                print ("poly", poly)
            for coord in poly:
                if verbose: 
                    print ("coord:", coord)
                lon, lat, z = coord 
                px, py = gT.latlon2pixel(lat, lon, input_raster=src_raster, 
                                     targetsr=targetsr, 
                                     geom_transform=geom_transform)
                poly_list_pix.append([px, py])
                if verbose:
                    print ("px, py", px, py)
                poly_list_latlon.append([lat, lon])
            
            if pixel_ints:
                ptmp = np.rint(poly_list_pix).astype(int)
            else:
                ptmp = poly_list_pix
            pixel_coords.append(ptmp)
            latlon_coords.append(poly_list_latlon)
            
        elif poly_type.upper() == 'POINT':
            print ("Skipping shape type: POINT in geojson_to_pixel_arr()")
            continue
        
        else:
            print ("Unknown shape type:", poly_type, " in geojson_to_pixel_arr()")
            return
            
    return pixel_coords, latlon_coords

###############################################################################
def create_building_mask(rasterSrc, vectorSrc, npDistFileName='', 
                            noDataValue=0, burn_values=1):

    '''
    Create building mask for rasterSrc,
    Similar to labeltools/createNPPixArray() in spacenet utilities
    '''
    
    ## open source vector file that truth data
    source_ds = ogr.Open(vectorSrc)
    source_layer = source_ds.GetLayer()

    ## extract data from src Raster File to be emulated
    ## open raster file that is to be emulated
    srcRas_ds = gdal.Open(rasterSrc)
    cols = srcRas_ds.RasterXSize
    rows = srcRas_ds.RasterYSize

    ## create First raster memory layer, units are pixels
    # Change output to geotiff instead of memory 
    memdrv = gdal.GetDriverByName('GTiff') 
    dst_ds = memdrv.Create(npDistFileName, cols, rows, 1, gdal.GDT_Byte, 
                           options=['COMPRESS=LZW'])
    dst_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    dst_ds.SetProjection(srcRas_ds.GetProjection())
    band = dst_ds.GetRasterBand(1)
    band.SetNoDataValue(noDataValue)    
    gdal.RasterizeLayer(dst_ds, [1], source_layer, burn_values=[burn_values])
    dst_ds = 0
    
    return 

###############################################################################
def create_dist_map(rasterSrc, vectorSrc, npDistFileName='', 
                           noDataValue=0, burn_values=1, 
                           dist_mult=1, vmax_dist=64):

    '''
    Create building signed distance transform from Yuan 2016 
    (https://arxiv.org/pdf/1602.06564v1.pdf).
    vmax_dist: absolute value of maximum distance (meters) from building edge
    Adapged from createNPPixArray in labeltools
    '''
    
    ## open source vector file that truth data
    source_ds = ogr.Open(vectorSrc)
    source_layer = source_ds.GetLayer()

    ## extract data from src Raster File to be emulated
    ## open raster file that is to be emulated
    srcRas_ds = gdal.Open(rasterSrc)
    cols = srcRas_ds.RasterXSize
    rows = srcRas_ds.RasterYSize

    geoTrans, poly, ulX, ulY, lrX, lrY = gT.getRasterExtent(srcRas_ds)
    transform_WGS84_To_UTM, transform_UTM_To_WGS84, utm_cs \
                                                = gT.createUTMTransform(poly)
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(geoTrans[0], geoTrans[3])
    line.AddPoint(geoTrans[0]+geoTrans[1], geoTrans[3])

    line.Transform(transform_WGS84_To_UTM)
    metersIndex = line.Length()

    memdrv = gdal.GetDriverByName('MEM')
    dst_ds = memdrv.Create('', cols, rows, 1, gdal.GDT_Byte)
    dst_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    dst_ds.SetProjection(srcRas_ds.GetProjection())
    band = dst_ds.GetRasterBand(1)
    band.SetNoDataValue(noDataValue)

    gdal.RasterizeLayer(dst_ds, [1], source_layer, burn_values=[burn_values])
    srcBand = dst_ds.GetRasterBand(1)

    memdrv2 = gdal.GetDriverByName('MEM')
    prox_ds = memdrv2.Create('', cols, rows, 1, gdal.GDT_Int16)
    prox_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    prox_ds.SetProjection(srcRas_ds.GetProjection())
    proxBand = prox_ds.GetRasterBand(1)
    proxBand.SetNoDataValue(noDataValue)

    opt_string = 'NODATA='+str(noDataValue)
    options = [opt_string]

    gdal.ComputeProximity(srcBand, proxBand, options)

    memdrv3 = gdal.GetDriverByName('MEM')
    proxIn_ds = memdrv3.Create('', cols, rows, 1, gdal.GDT_Int16)
    proxIn_ds.SetGeoTransform(srcRas_ds.GetGeoTransform())
    proxIn_ds.SetProjection(srcRas_ds.GetProjection())
    proxInBand = proxIn_ds.GetRasterBand(1)
    proxInBand.SetNoDataValue(noDataValue)
    opt_string2 = 'VALUES='+str(noDataValue)
    options = [opt_string, opt_string2]
    #options = ['NODATA=0', 'VALUES=0']

    gdal.ComputeProximity(srcBand, proxInBand, options)

    proxIn = gdalnumeric.BandReadAsArray(proxInBand)
    proxOut = gdalnumeric.BandReadAsArray(proxBand)

    proxTotal = proxIn.astype(float) - proxOut.astype(float)
    proxTotal = proxTotal*metersIndex
    proxTotal *= dist_mult

    # clip array
    proxTotal = np.clip(proxTotal, -1*vmax_dist, 1*vmax_dist)

    if npDistFileName != '':
        # save as numpy file since some values will be negative
        np.save(npDistFileName, proxTotal)
        #cv2.imwrite(npDistFileName, proxTotal)

    #return proxTotal
    return

###############################################################################
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