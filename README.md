# Spacenet building identification

## Data 

### Explore the data using QGIS

Followed [1] to download the spacenet data from aws and explore data using QGIS. Download and install QGIS to explore the data. Follow the steps in [3] to visualize data using QGIS. 

### Explore the data using Jupyter notebook

```bash
docker build -t <name> .
docker run -p 8887:8888 -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/notebooks:/model1/notebooks -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/data:/model1/data -it <name>
``` 

### Download spacenet_sample 
Download data from google drive and place it in the data folder 

### Transform to TFRecords

We are going to use Tensorflow object detection for this project. We need to transform the data to TFRecords before we can train. We build the docker image and then login to the container and run the scripts.
 
```bash
cd /app
docker build -t geo2 . -f ./docker/Dockerfile_py2   # will give errors but build successfully
# for fresh build docker build --no-cache -t geo2 . -f ./docker/Dockerfile_py2 
docker run  -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/data:/workspace/data -it geo /bin/bash
```
Once in the container we run the following scripts in this order. These scripts will  convert images to `jpg`, split data in train and test and create TFRecords for test and train set.

```bash
cd /app 
python generate_bbox.py
python generate_jpg_images.py
python generate_tfrecord.py --csv_input=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/train_labels.csv  --output_path=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/train.record
python generate_tfrecord.py --csv_input=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/test_labels.csv  --output_path=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/test.record
```

## Training
 

### Download pretrained model
For training, I used `ssd_mobilenet_v1_pets.config` as basis. I needed to adjust the num_classes to one and also set the path (PATH_TO_BE_CONFIGURED) for the model checkpoint, the train and test data files as well as the label map. In terms of other configurations like the learning rate, batch size and many more, I used their default settings.

The directory structure looks like this: 
```
+data
  - label_map file
  - train.record # TFRecord file
  - train_labels.csv
  - test.record # TFRecord file
  - test_labels.csv
+models
  + model
    -pipeline config file
    +train
    +eval
```



### Train Locally 
Follow the steps in [10]


## Set up AWS 


## Evaluation
 

## References 
1. Data download help: http://lncohn.com/spacenet/spacenet_data.html
2. Download QGIS: https://www.qgis.org/en/site/forusers/download.html# 
3. Visualize the data: https://medium.com/@sumit.arora/getting-started-with-aws-spacenet-and-spacenet-dataset-visualization-basics-7ddd2e5809a2
4. https://medium.com/the-downlinq/getting-started-with-spacenet-data-827fd2ec9f53
5. https://medium.com/the-downlinq/you-only-look-twice-multi-scale-object-detection-in-satellite-imagery-with-convolutional-neural-38dad1cf7571
6. Running jupyter notebook inside docker: https://medium.com/@14prakash/playing-with-caffe-and-docker-to-build-deep-learning-models-99c9570ffc3d
7. Object detection using Tensorflow: https://towardsdatascience.com/how-to-train-your-own-object-detector-with-tensorflows-object-detector-api-bec72ecfe1d9
8. https://becominghuman.ai/tensorflow-object-detection-api-tutorial-training-and-evaluating-custom-object-detector-ed2594afcf73
9. https://hackernoon.com/keras-with-gpu-on-amazon-ec2-a-step-by-step-instruction-4f90364e49ac
10. Training locally: https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/running_locally.md
11. Pretrained model: http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_2018_01_28.tar.gz
12. Retrain https://cv-tricks.com/tensorflow-tutorial/save-restore-tensorflow-models-quick-complete-tutorial/

