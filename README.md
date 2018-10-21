# Spacenet building identification

## Data Preperation
Followed [1] to download the spacenet data from aws and explore data using QGIS
### Data Access

### Explore the data using QGIS
Download and install QGIS to explore the data. Follow the steps in [3] to visualize data using QGIS. 

### Explore the data using Jupyter notebook

```bash
docker build -t <name> .
docker run -p 8887:8888 -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/notebooks:/model1/notebooks -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/data:/model1/data -it <name>
``` 

### Transform the data to format consumed by the ML algorithms 
```bash
cd /app
docker build -t geo2 . -f ./docker/Dockerfile_py2   # will give errors but build successfully
# for fresh build docker build --no-cache -t geo2 . -f ./docker/Dockerfile_py2 
docker run  -v /Users/trsaxena/Projects/learn/demos/ImageObjectDetection/spacenet_building_detection/data:/workspace/data -it geo /bin/bash
```

Download spacenet_sample and place it in the data folder.
```bash
python generate_test_train.py
python generate_jpg_images.py
python generate_tfrecord.py --csv_input=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/train_labels.csv  --output_path=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/train.record
python generate_tfrecord.py --csv_input=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/test_labels.csv  --output_path=/workspace/data/spacenet_sample/AOI_2_Vegas_Train/output/data/test.record
```

### Train
Setup an EC2 instance

## Training

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

