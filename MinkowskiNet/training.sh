#!/usr/bin/env bash
export BATCH_SIZE=32
export CUDA_VISIBLE_DEVICES='0,1'
FEAT=$1

./scripts/train.sh weighted_cross_entropy $FEAT "--buildingnet_path Dataset/BuildingNet/minkowski_net \
 --prefetch_data true --weighted_cross_entropy true --val_freq 600 --save_freq 200 --max_ngpu 2 \
 --save_param_histogram true"
