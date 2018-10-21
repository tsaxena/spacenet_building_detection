import os
import shutil
import random
from six.moves import configparser
from osgeo import gdal
import subprocess

config = configparser.ConfigParser()
config.read('config.ini')
tif_path = config.get("FILE_PATHS","TIF_PATH")
TEST_SIZE = float(config.get("PARAMS","TEST_SIZE")
OUTPUT_PATH = config.get("FILE_PATHS","OUTPUT_PATH")

if not os.path.exists("output"):
    os.mkdir("output")

filelist = []
converted_file_path = os.path.join(OUTPUT_PATH,"converted_files.txt")
with open(converted_file_path, "r") as jpglist:
    for line in jpglist:
        filelist.append(line)

image_dir_path = os.path.join(OUTPUT_PATH, "images")
if not os.path.exists(image_dir_path):
    os.mkdir(image_dir_path)

fname = []
for raster in filelist:
    srcRaster = gdal.Open(tif_path+os.path.splitext(raster)[0]+".tif")
    outputRaster = image_dir_path+os.path.splitext(raster)[0]+".jpg"

    cmd = ['gdal_translate', '-ot', 'Byte', '-of', 'JPEG', '-co', 'PHOTOMETRIC=rgb']
    scaleList = []
    for bandId in range(srcRaster.RasterCount):
        bandId = bandId+1
        band=srcRaster.GetRasterBand(bandId)
        min = band.GetMinimum()
        max = band.GetMaximum()

        # if not exist minimum and maximum values
        if min is None or max is None:
            (min, max) = band.ComputeRasterMinMax(1)
        cmd.append('-scale_{}'.format(bandId))
        cmd.append('{}'.format(0))
        cmd.append('{}'.format(max))
        cmd.append('{}'.format(0))
        cmd.append('{}'.format(255))

    cmd.append(tif_path+os.path.splitext(raster)[0]+".tif")
    cmd.append(outputRaster)
    print(cmd)
    subprocess.call(cmd)
    os.remove(image_dir_path+os.path.splitext(raster)[0]+".jpg.aux.xml")

lMap = """item {
  id: 1
  name: 'building'
}
"""

with open("output/train.pbtxt", "w") as labelMap:
    labelMap.write(lMap)

shutil.copy2("output/train.pbtxt","output/test.pbtxt")
#shutil.copy2("run.sbatch","output/")
#shutil.move("ssd_train_labels.csv","output/")
#shutil.move("ssd_test_labels.csv","output/")
print("Logistics done!")
