# BuildingNet - MinkowskiNet implementation

This folder contains code for the MinkowskiNet experiments, based on the [Minkowski Engine](https://github.com/NVIDIA/MinkowskiEngine).
This implementation is an adaptation of the  [Spatio-Temporal Segmentation](https://github.com/chrischoy/SpatioTemporalSegmentation)
repository.

## Installation

### Requirements
The present code was tested on the following environment:

- Ubuntu 20.04
- CUDA 11.3.109
- cuDNN 8.2.0
- PyTorch 1.10.1
- Python 3.8

### Conda environment
You can use the ```environment.yml``` in order to initialize a working environment via ```conda```:
```bash
conda env create -f environment.yml
```
The Minkowski Engine **v0.5.4** needs to also be installed, either [manually](https://github.com/NVIDIA/MinkowskiEngine)
or through [pip](https://pypi.org/project/MinkowskiEngine/).

## BuildingNet v1 Dataset

### Preprocessing

First create the following folder ```Dataset/BuildingNet```. Download the **v1 version** of the dataset from the [official website](https://buildingnet.org/)
and unzip the ```POINT_CLOUDS.zip``` and ```model_data/point_cloud/point_labels.zip``` under the dataset
directory, and add the ```splits``` folder as well. The data should be organized as follows:

```bash
Dataset
└── BuildingNet
    ├── POINT_CLOUDS
    │   ├── COMMERCIALcastle_mesh0365.ply
    │   ├── COMMERCIALcastle_mesh0904.ply
     ...
    │   └── RESIDENTIALvilla_mesh6487.ply
    ├── point_labels
    │   ├── COMMERCIALcastle_mesh0365_label.json
    │   ├── COMMERCIALcastle_mesh0904_label.json
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

### Training
You can train your network using:
```bash
./training.sh  <input_feat>

# <input_feat>: specify input features, e.g., normals, normals_rgb
```

Adjust the batch size, according to your computational resources. For our experiments we set ```batch_size=32```, and
the NVIDIA A5000 GPU was used (```VRAM=24GB```). 

### Evaluation - Validation Split
For evaluating a trained model on the **validation** split, first the following files need to be added to the dataset directory:

- ```OBJ_MODELS.zip```
- ```model_data/obj/face_labels.zip```
- ```model_data/point_cloud/point_faceindex.zip```

These files are part of the official release of the BuildingNet dataset. Unzip these files under ```Dataset/BuildingNet```.
The final structure of this directory should be the following:

```bash
Dataset
└── BuildingNet
    ├── face_labels
    ├── minkowski_net
    ├── OBJ_MODELS
    ├── POINT_CLOUDS
    ├── point_faceindex
    ├── point_labels 
    └── splits
```
Finally, run the following command in order to evaluate the model for the point cloud and mesh phase:

```bash
./evaluate_val_split.sh <input_feat> <weights>

# <input_feat>: specify input features, e.g., normals, normals_rgb
# <weights>: specify the trained weights path
```

### Online Challenge (EvalAI)
You can export the per-point and per-face predicted labels in `.npz` format, for the validation and test split by 
executing the `export_predictions.sh` script:

(Before running the next command make sure that the `Dataset/BuildingNet` directory has the right contents - see the
**Evaluation - Validation Split** section)

```bash
./export_predictions.sh <input_feat> <weights>

# <input_feat>: specify input features, e.g., normals, normals_rgb
# <weights>: specify the trained weights path
```

You can upload each generated `.npz` file to the appropriate evaluation phase to our [online challenge (EvalAI)](https://eval.ai/web/challenges/challenge-page/1938/overview).
The submitted file will be evaluated either on the validation or the test ground truth annotations. Check the *"My Submissions"* 
page to view your evaluation score.

### Export features for BuildingGNN

Features can be exported per-component for each building model, with the following command:

(Before running the next command make sure that the `Dataset/BuildingNet` directory has the right contents - see the
**Evaluation - Validation Split** section)

```bash
./export_features.sh <input_feat> <weights>

# <input_feat>: specify input features, e.g., normals, normals_rgb
# <weights>: specify the trained weights path
```

### Pretrained model

|    Model     | Voxel Size |      Input Features       | Point Cloud Eval. (Val split) |  Triangle Eval. (Val split)   |   Component Eval. (Val split)   | Link   |
|:------------:|:----------:|:-------------------------:|:-----------------------------:|:-----------------------------:|:-------------------------------:|:------:|
| Res16UNet34C |    0.01    | Point normals + RGB Color | pIoU=33.5, sIoU=25.1, CA=74.1 | pIoU=35.5, sIoU=31.7, CA=75.4 | pIoU=39.8, sIoU=47.0, CA=79.4 |[download](https://drive.google.com/file/d/1DhUAKPlrEVickIOQ37gLYoYR0VeZsSps/view?usp=share_link) |

You can download the pretrained model using the following script:

```bash
./download_pretrained_model.sh
```