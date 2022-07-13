#!/usr/bin/env bash
FEAT=$1
WEIGHTS=$2

./scripts/test.sh 0 weighted_cross_entropy $FEAT "--buildingnet_path Dataset/BuildingNet/minkowski_net \
 --prefetch_data true --weighted_cross_entropy true --is_train false --test_original_pointcloud true \
 --return_transformation true --save_prediction true --weights $WEIGHTS"
