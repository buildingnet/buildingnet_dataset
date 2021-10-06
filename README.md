# BuildingNet
** BuildingNet **

This is the implementation of the BuildingNet architecture described in this paper:

**Paper link**

Project Page:
**link**

Arxiv version:
**link**

--
The model features are combination of a pretrained network model features and building prior information features.
You can pretrain the dataset in  model ( mesh, point cloud, viewpoint )

In this paper we have used minkowskiNet to train for the pretrained features.
**Paper link**

--
##Requirements##
This project was built using cuda10.1 and python3
For other requirements, look into requirements.txt

1. Download the pretrained features from **link** and save it in the "data" folder in the project

2. To run this model, execute command in run.txt
python3 train.py --datadir="data" --epoch 200 --outputdir 'Output' --ckpt_dir 'checkpoint' --normalization 'GN' --modeltype 'Edge' --edgetype 'all' --lr 1e-4 --nodetype 'node+minkownormal' --pretrainedtype 'fc3_avg' --save_checkpoint=5


