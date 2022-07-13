#!/usr/bin/env bash
FEAT=$1
WEIGHTS=$2

./scripts/get_features.sh 0 weighted_cross_entropy $FEAT "--buildingnet_path Dataset/BuildingNet/minkowski_net \
--prefetch_data true --weighted_cross_entropy true --is_train false --save_prediction true --export_feat true --return_transformation true \
--weights $WEIGHTS"
