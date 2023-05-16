# BuildingNet: Learning to Label 3D Buildings (ICCV 2021 Oral)

[Project Page](https://buildingnet.org/) | Paper ([arxiv](https://arxiv.org/abs/2110.04955), 
[ICCV](https://openaccess.thecvf.com/content/ICCV2021/html/Selvaraju_BuildingNet_Learning_To_Label_3D_Buildings_ICCV_2021_paper.html)) 
| [Dataset](https://forms.gle/jFQpoRzRkrTCaTzX8) | [Challenge](https://eval.ai/web/challenges/challenge-page/1938/overview) 

BuildingNet is a publicly available large-scale dataset of annotated 3D building models whose exteriors and surroundings 
are consistently labeled. Buildings have more challenging structural complexity compared to objects in existing benchmarks, 
thus, we hope that our dataset can nurture the development of algorithms that are able to cope with such large-scale geometric 
data for both vision and graphics tasks e.g., 3D semantic segmentation, part-based generative models, correspondences, texturing, 
and analysis of point cloud data acquired from real-world buildings.

## News
* [05/2023] We added an update implementation of the MinkowskiNet experiments, based on the latest version (v0.5.4) of the 
[MinkowskiEngine](https://github.com/NVIDIA/MinkowskiEngine/tree/v0.5.4).
* [02/2023] The BuildingNet v1 dataset is now available, with more complete and improved labelings, which can be downloaded 
by filling [this form](https://forms.gle/jFQpoRzRkrTCaTzX8).
* [02/2023] The BuildingNet challenge will be hosted at the Second Workshop on 
[Structural and Compositional Learning on 3D Data](https://struco3d.github.io/cvpr2023/) @ CVPR 2023 Vancouver (Canada).
Please visit our challenge's website ([EvalAI](https://eval.ai/web/challenges/challenge-page/1938/overview)) for more information.

## BuildingGNN

BuildingGNN is a graph neural network for labeling 3D meshes by taking advantage of pre-existing mesh structure
in the form of subgroups. The main idea of the network is to take into account spatial and structural relations between
subgroups to promote more coherent mesh labeling.

### Requirements:
This project was built using Cuda 10.1 and Python 3.8. For other requirements, look into requirements.txt. The conda 
environment is in `buildingnet.yml`.

### Model features:
The model features are combinations of a pretrained network model features and building prior information features.
In this paper we have used [MinkowskiNet](https://arxiv.org/abs/1904.08755) to train for the pretrained features.

### Run the model:

1. After downloading the dataset (fill in the form on our official project page to get access) place the contents of ```model_data/GNN``` 
under the ```data``` folder in the project

2. To run this model, execute command in run.txt
```
python3 train.py --datadir="data" --epoch 200 --outputdir 'Output' --ckpt_dir 'checkpoint' --normalization 'GN' --modeltype 'Edge' --edgetype 'all' --lr 1e-4 --nodetype 'node+minkownormal' --pretrainedtype 'fc3_avg' --IOU_checkpoint=5
```
This gives Shape and part IOU every 5 epochs.

## MinkowskiNet Experiments
Follow this [guide](MinkowskiNet/README.md), for the MinkowskiNet experiments on the BuildingNet v0 dataset.

