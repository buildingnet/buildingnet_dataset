#!/usr/bin/env bash
BATCH_SIZE=32
MAX_EPOCH=200
DATA_PATH=./Dataset/BuildingNet/minkowski_net
GPU=0
LOSS=weighted_cross_entropy
INPUT_FEAT=$1
WEIGHTS=$2

./scripts/test.sh $GPU $LOSS $INPUT_FEAT $BATCH_SIZE $MAX_EPOCH "--buildingnet_path $DATA_PATH \
--prefetch_data true  --avg_feat True --opt_speed True --weighted_cross_entropy True --is_train False \
--evaluate True --weights $WEIGHTS"
