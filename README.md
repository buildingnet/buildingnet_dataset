# BuildingNet

This is the implementation of the BuildingNet architecture described in this paper:

## Paper:
[BuildingNet: Learning to Label 3D Buildings](https://drive.google.com/file/d/1aD5AIkx58k7EyK8Utg8vKv2Y_UMZ--pv/view)

### Arxiv version:
**link**

## Project Page:
[BuildingNet](https://buildingnet.org/)

## Requirements:
This project was built using cuda10.1 and python3. <br/>
For other requirements, look into requirements.txt

## Model features:
The model features are combinations of a pretrained network model features and building prior information features. <br/>
In this paper we have used minkowskiNet to train for the pretrained features. <br/>
[Minkowski CNN](https://arxiv.org/abs/1904.08755)

## Run the model:

* 1. Download the pretrained features from [data](https://drive.google.com/drive/folders/1ixOFib3WjHBEKGQXIWHEcodR9qawNHvu?usp=sharing) and save it in the "data" folder in the project

* 2. To run this model, execute command in run.txt <br/>
python3 train.py --datadir="data" --epoch 200 --outputdir 'Output' --ckpt_dir 'checkpoint' --normalization 'GN' --modeltype 'Edge' --edgetype 'all' --lr 1e-4 --nodetype 'node+minkownormal' --pretrainedtype 'fc3_avg' --save_checkpoint=5


