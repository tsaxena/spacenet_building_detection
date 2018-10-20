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


```bash
python generate_bbox.py
python logistics.py
```

## Training

## Evaluation
 

## References 
1. Data download help: http://lncohn.com/spacenet/spacenet_data.html
2. Download QGIS: https://www.qgis.org/en/site/forusers/download.html# 
3. Visualize the data: https://medium.com/@sumit.arora/getting-started-with-aws-spacenet-and-spacenet-dataset-visualization-basics-7ddd2e5809a2
4. https://medium.com/the-downlinq/getting-started-with-spacenet-data-827fd2ec9f53
5. https://medium.com/the-downlinq/you-only-look-twice-multi-scale-object-detection-in-satellite-imagery-with-convolutional-neural-38dad1cf7571
6. Running jupyter notebook inside docker: https://medium.com/@14prakash/playing-with-caffe-and-docker-to-build-deep-learning-models-99c9570ffc3d


