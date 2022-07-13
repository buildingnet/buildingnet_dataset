# BuildingNet - MinkowskiNet implementation

This folder contains code for the MinkowskiNet experiments, based on the [Minkowski Engine](https://github.com/NVIDIA/MinkowskiEngine/tree/v0.4.3).
This implementation is an adaptation of the  [Spatio-Temporal Segmentation](https://github.com/chrischoy/SpatioTemporalSegmentation)
repository.

## Installation

### Requirements
The present code was tested on the following environment:

- Ubuntu 18.04
- CUDA 10.2.89
- cuDNN 7.6.5
- PyTorch 1.6.0
- Python 3.7

### Conda environment
You can use the ```environment.yml``` in order to initialize a working environment via ```conda```:
```bash
conda env create -f environment.yml
```
The Minkowski Engine **v0.4.3** needs to also be installed, either [manually](https://github.com/NVIDIA/MinkowskiEngine/tree/v0.4.3)
or through [pip](https://pypi.org/project/MinkowskiEngine/0.4.3/).

## BuildingNet training

### Preprocessing

First create the following folder ```Dataset/BuildingNet```. Download the dataset from the [official website](https://buildingnet.org/)
and unzip the ```POINT_CLOUDS.zip``` and ```model_data/point_cloud/point_labels.zip``` under the dataset
directory, and add the ```splits``` folder as well. The data should be organized as follows:

```bash
Dataset
└── BuildingNet
    ├── POINT_CLOUDS
    │   ├── COMMERCIALcastle_mesh0365.ply
    │   ├── COMMERCIALcastle_mesh0882.ply
     ...
    │   └── RESIDENTIALvilla_mesh6487.ply
    ├── point_labels
    │   ├── COMMERCIALcastle_mesh0365_label.json
    │   ├── COMMERCIALcastle_mesh0882_label.json
     ...
    │   └── RESIDENTIALvilla_mesh6487_label.json  
    └── splits
        ├── dataset_models.txt
        ├── test_split.txt
        ├── train_split.txt
        └── val_split.txt

```

Preprocess the point clouds and labels with the following command:
```bash
python -m lib.datasets.preprocessing.buildingnet
```
This will create the ```minkowski_net``` folder under ```Dataset/BuildingNet```, which contains the
input point cloud data to the Minkowski network.

## Training
You can train your network using:
```bash
./training.sh  <input_feat>

# <input_feat>: specify input features, e.g., normals, normals_rgba
```
Adjust the number of GPUs and the batch size, according to your computational resources. You will need to change
```export CUDA_VISIBLE_DEVICES='0,1'```, ```export BATCH_SIZE=32``` and ```--max_ngpu 2``` in the above script.

## Evaluation
For evaluating a trained model, first the following files need to be added to the dataset directory:

- ```OBJ_MODELS.zip```
- ```model_data/obj/component_labels.zip```
- ```model_data/point_cloud/point_faceindex.zip```

These files are part of the official release of the BuildingNet dataset. Unzip these files under ```Dataset/BuildingNet```.
The final structure of this directory should be the following:

```bash
Dataset
└── BuildingNet
    ├── component_labels
    ├── minkowski_net
    ├── OBJ_MODELS
    ├── POINT_CLOUDS
    ├── point_faceindex
    ├── point_labels 
    └── splits
```
Finally, run the following command in order to evaluate the model for the point cloud and mesh track:

```bash
./testing.sh <input_feat> <weights>

# <input_feat>: specify input features, e.g., normals, normals_rgba
# <weights>: specify the trained weights path

```

## Export features

Features can be exported per point and per component for each building model, with the following command:

```bash
./export_features.sh <input_feat> <weights>

# <input_feat>: specify input features, e.g., normals, normals_rgba
# <weights>: specify the trained weights path

```

The ```Dataset/BuildingNet``` folder needs to have the same structure, as in the **Evaluation** section.

## Pretrained models

| Model            | Voxel Size | Input Features          | Point Cloud Eval.           | Triangle Eval.              | Component Eval.             | Link   |
|:----------------:|:----------:|:-----------------------:|:---------------------------:|:---------------------------:|:---------------------------:|:------:|
|Res16UNet34A      |0.01        |Point normals            |pIoU=27.1, sIoU=22.3, CA=61.7|pIoU=29.3, sIoU=27.1, CA=64.3|pIoU=32.6, sIoU=36.0, CA=68.8|[download](https://drive.google.com/file/d/12oiGN41bouFXTY_4QVGfN3ZNqGDhQrjf/view?usp=sharing) |
|Res16UNet34A      |0.01        |Point normals + RGB color|pIoU=31.2, sIoU=24.3, CA=66.1|pIoU=34.2, sIoU=29.4, CA=68.4|pIoU=38.6, sIoU=39.8, CA=74.3|[download](https://drive.google.com/file/d/1woM7QWAXipikGSiBNGVfaOJdxschXyPL/view?usp=sharing) |

You can download the pretrained models using the following script:

```bash
./download_models.sh
```
