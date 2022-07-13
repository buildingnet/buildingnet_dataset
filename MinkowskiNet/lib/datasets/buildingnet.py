import logging
import os
import sys
import json
from pathlib import Path

import numpy as np
from scipy import spatial

from lib.dataset import VoxelizationDataset, DatasetPhase, str2datasetphase_type
from lib.pc_utils import read_plyfile, save_point_cloud
from lib.utils import read_txt

CLASS_LABELS = ('wall', 'window', 'vehicle', 'roof', 'plant', 'door', 'tower', 'furniture',
                'ground', 'beam', 'stairs', 'column', 'banister', 'floor', 'chimney', 'ceiling',
                'fence', 'pool', 'corridor', 'balcony', 'garage', 'dome', 'road', 'gate',
                'parapet', 'buttress', 'dormer', 'lighting', 'arch', 'awning', 'shutters')

VALID_CLASS_IDS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28,
                   29, 30, 31)

BUILDINGNET_COLOR_MAP = {
    0: (0, 0, 0),
    1: (255, 69, 0),
    2: (0, 0, 255),
    3: (57, 96, 115),
    4: (75, 0, 140),
    5: (250, 128, 114),
    6: (127, 0, 0),
    7: (214, 242, 182),
    8: (13, 33, 51),
    9: (32, 64, 53),
    10: (255, 64, 64),
    11: (96, 185, 191),
    12: (61, 64, 16),
    13: (115, 61, 0),
    14: (64, 0, 0),
    15: (153, 150, 115),
    16: (255, 0, 255),
    17: (57, 65, 115),
    18: (85, 61, 242),
    19: (191, 48, 105),
    20: (48, 16, 64),
    21: (255, 145, 128),
    22: (153, 115, 145),
    23: (255, 191, 217),
    24: (0, 170, 255),
    25: (138, 77, 153),
    26: (64, 255, 115),
    27: (140, 110, 105),
    28: (204, 0, 255),
    29: (178, 71, 0),
    30: (255, 187, 221),
    31: (13, 211, 255),
}

NORMALIZED_FREQ = {
    1: 1,
    2: 9.3881,
    3: 73.6199,
    4: 2.09293,
    5: 20.0008,
    6: 52.77571,
    7: 15.26988,
    8: 103.09889,
    9: 3.43945,
    10: 35.35736,
    11: 78.68262,
    12: 64.82034,
    13: 129.65081,
    14: 7.11018,
    15: 108.05064,
    16: 17.01521,
    17: 29.84063,
    18: 30.18609,
    19: 29.79754,
    20: 51.42419,
    21: 155.69354,
    22: 49.74032,
    23: 22.5733,
    24: 798.24279,
    25: 145.46404,
    26: 146.36735,
    27: 363.90137,
    28: 5364.96081,
    29: 288.8162,
    30: 670.37904,
    31: 1363.54926,
}


class BuildingNetVoxelizationDataset(VoxelizationDataset):

  # Voxelization arguments
  VOXEL_SIZE = 0.05

  # Augmentation arguments
  SHIFT_PARAMS = (0.01, 0.05) # ((sigma, clip)
  N_ROTATIONS = 12

  ROTATION_AXIS = 'y'
  NUM_LABELS = 32  # Will be converted to 31 as defined in IGNORE_LABELS.
  IGNORE_LABELS = tuple(set(range(NUM_LABELS)) - set(VALID_CLASS_IDS))
  IS_FULL_POINTCLOUD_EVAL = True
  NORM_FREQ = NORMALIZED_FREQ
  class_labels = CLASS_LABELS

  # If trainval.txt does not exist, copy train.txt and add contents from val.txt
  DATA_PATH_FILE = {
      DatasetPhase.Train: 'train.txt',
      DatasetPhase.Val: 'val.txt',
      DatasetPhase.Test: 'test.txt'
  }

  def __init__(self,
               config,
               prevoxel_transform=None,
               rot_aug=False,
               phase=DatasetPhase.Train):
    if isinstance(phase, str):
      phase = str2datasetphase_type(phase)
    # Use cropped rooms for train/val
    data_root = config.buildingnet_path
    data_paths = read_txt(os.path.join(data_root, self.DATA_PATH_FILE[phase]))
    logging.info('Loading {}: {}'.format(self.__class__.__name__, self.DATA_PATH_FILE[phase]))
    self.input_feat = config.input_feat.lower()
    if self.input_feat == 'rgb' or self.input_feat == 'normals' :
      self.NUM_IN_CHANNEL = 3
    elif self.input_feat == 'rgba':
      self.NUM_IN_CHANNEL = 4
    elif self.input_feat == 'normals_rgb':
      self.NUM_IN_CHANNEL = 6
    elif self.input_feat == 'normals_rgba':
      self.NUM_IN_CHANNEL = 7
    else:
      print("Unknown input features {feat:s}" .format(feat=self.input_feat))
      exit(-1)

    super().__init__(
        data_paths,
        data_root=data_root,
        prevoxel_transform=prevoxel_transform,
        ignore_label=config.ignore_label,
        return_transformation=config.return_transformation,
        rot_aug=rot_aug,
        config=config)

  def test_pointcloud(self, pred_dir):
    print('Running BUILDINGNET full pointcloud evaluation.')
    eval_path = pred_dir
    os.makedirs(eval_path, exist_ok=True)
    # Test independently for each building
    sys.setrecursionlimit(100000)  # Increase recursion limit for k-d tree.
    save_iter = 0
    for i, data_path in enumerate(self.data_paths):
      model_name = data_path.split('/')[-1][:-4]
      print("Get per point features for building {name:s} ({iter:d}/{total:d})"
            .format(name=model_name, iter=i+1, total=len(self.data_paths)))
      pred = np.load(os.path.join(pred_dir, 'pred_%04d.npy' % (i)))
      os.remove(os.path.join(pred_dir, 'pred_%04d.npy' % (i)))

      if (i+1) < save_iter:
        # save voxelized pointcloud predictions
        save_point_cloud(
            np.hstack((pred[:, :3], np.array([BUILDINGNET_COLOR_MAP[i] for i in pred[:, -1]]))),
            f'{eval_path}/{model_name}_voxel.ply',
            verbose=False)

      fullply_f = self.data_root / data_path
      query_pointcloud = read_plyfile(fullply_f)
      query_xyz = query_pointcloud[:, :3]
      query_label = query_pointcloud[:, -1]
      # Run test for each room.
      pred_tree = spatial.cKDTree(pred[:, :3], leafsize=500)
      # Inverse distance weighting using 4-nn
      k, pow = 4, 2
      dist, k_nn = pred_tree.query(query_xyz, k=k)
      dist_pow = dist ** pow
      norm = np.sum(1 / dist_pow, axis=1, keepdims=True)
      norm = np.tile(norm, [1, k])
      weights = (1 / dist_pow) / norm
      assert (np.isclose(np.sum(weights, axis=1, keepdims=True), np.ones_like(norm)).all())
      feats = np.multiply(weights[..., np.newaxis], pred[k_nn, 3:-1])
      inter_feat = np.sum(feats, axis=1).astype(np.float32)
      ptc_pred = np.argmax(inter_feat, axis=1).astype(int)
      if self.IGNORE_LABELS:
        decode_label_map = {}
        for k, v in self.label_map.items():
          decode_label_map[v] = k
        ptc_pred = np.array([decode_label_map[x] for x in ptc_pred], dtype=np.int)

      if (i + 1) < save_iter:
        # Save prediciton in colored pointcloud for visualization.
        save_point_cloud(
            np.hstack((query_xyz, np.array([BUILDINGNET_COLOR_MAP[i] for i in query_label]))),
            f'{eval_path}/{model_name}_gt.ply',
            verbose=False)
        save_point_cloud(
            np.hstack((query_xyz, np.array([BUILDINGNET_COLOR_MAP[i] for i in ptc_pred]))),
            f'{eval_path}/{model_name}_pred.ply',
            verbose=False)

      # Save per point output features to be used for evaluation
      np.save(os.path.join(eval_path, model_name + ".npy"), inter_feat)


class BuildingNetVoxelization0_02Dataset(BuildingNetVoxelizationDataset):
  VOXEL_SIZE = 0.02

class BuildingNetVoxelization0_01Dataset(BuildingNetVoxelizationDataset):
  VOXEL_SIZE = 0.01

class BuildingNetVoxelization0_005Dataset(BuildingNetVoxelizationDataset):
  VOXEL_SIZE = 0.005
