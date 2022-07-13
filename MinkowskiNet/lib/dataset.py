from abc import ABC
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

import random
import numpy as np
from enum import Enum

import torch
from torch.utils.data import Dataset, DataLoader

import MinkowskiEngine as ME

from plyfile import PlyData
import lib.transforms as t
from lib.dataloader import InfSampler
from lib.voxelizer import Voxelizer


class DatasetPhase(Enum):
  Train = 0
  Val = 1
  Val2 = 2
  TrainVal = 3
  Test = 4


def datasetphase_2str(arg):
  if arg == DatasetPhase.Train:
    return 'train'
  elif arg == DatasetPhase.Val:
    return 'val'
  elif arg == DatasetPhase.Val2:
    return 'val2'
  elif arg == DatasetPhase.TrainVal:
    return 'trainval'
  elif arg == DatasetPhase.Test:
    return 'test'
  else:
    raise ValueError('phase must be one of dataset enum.')


def str2datasetphase_type(arg):
  if arg.upper() == 'TRAIN':
    return DatasetPhase.Train
  elif arg.upper() == 'VAL':
    return DatasetPhase.Val
  elif arg.upper() == 'VAL2':
    return DatasetPhase.Val2
  elif arg.upper() == 'TRAINVAL':
    return DatasetPhase.TrainVal
  elif arg.upper() == 'TEST':
    return DatasetPhase.Test
  else:
    raise ValueError('phase must be one of train/val/test')


class DictDataset(Dataset, ABC):

  IS_FULL_POINTCLOUD_EVAL = False

  def __init__(self,
               data_paths,
               prevoxel_transform=None,
               data_root='/'):
    """
    data_paths: list of lists, [[str_path_to_input, str_path_to_label], [...]]
    """
    Dataset.__init__(self)

    # Allows easier path concatenation
    if not isinstance(data_root, Path):
      data_root = Path(data_root)

    self.data_root = data_root
    self.data_paths = sorted(data_paths)

    self.prevoxel_transform = prevoxel_transform

  def load_input(self, index):
    raise NotImplementedError

  def load_target(self, index):
    raise NotImplementedError

  def get_classnames(self):
    return self.class_labels

  def reorder_result(self, result):
    return result

  def __getitem__(self, index):
    out_array = []
    for k in self.loading_key_order:
      loader, transformer = self.data_loader_dict[k]
      v = loader(index)
      if transformer:
        v = transformer(v)
      out_array.append(v)
    return out_array

  def __len__(self):
    return len(self.data_paths)


class VoxelizationDatasetBase(DictDataset, ABC):
  ROTATION_AXIS = None
  NUM_IN_CHANNEL = None
  NUM_LABELS = -1  # Number of labels in the dataset, including all ignore classes
  IGNORE_LABELS = None  # labels that are not evaluated
  IS_ONLINE_VOXELIZATION = True
  N_ROTATIONS = 1

  def __init__(self,
               data_paths,
               prevoxel_transform=None,
               prefetch_data=False,
               data_root='/',
               ignore_mask=255,
               return_transformation=False,
               rot_aug=False,
               **kwargs):
    """
    ignore_mask: label value for ignore class. It will not be used as a class in the loss or evaluation.
    """
    DictDataset.__init__(
        self,
        data_paths,
        prevoxel_transform=prevoxel_transform,
        data_root=data_root)

    self.ignore_mask = ignore_mask
    self.return_transformation = return_transformation
    self.rot_aug = rot_aug
    self.prefetch_data = prefetch_data

    if self.prefetch_data:
      self.prefetched_coords, self.prefetched_feats, self.prefetched_labels = [], [], []
      for data_ind in tqdm(range(len(self.data_paths))):
        coords, feats, labels = self.load_ply(data_ind, self.input_feat)
        self.prefetched_coords.append(coords)
        self.prefetched_feats.append(feats)
        self.prefetched_labels.append(labels)
    if self.rot_aug:
      angle = 2 * np.pi / self.N_ROTATIONS
      self.rotation_map = [(data_ind, rot_ind * angle) for data_ind in range(len(data_paths)) for rot_ind in range(self.N_ROTATIONS)]

  def __getitem__(self, index):
    raise NotImplementedError

  def load_ply(self, index, input_feat='rgb'):
    filepath = self.data_root / self.data_paths[index]
    plydata = PlyData.read(filepath)
    data = plydata.elements[0].data
    coords = np.array([data['x'], data['y'], data['z']], dtype=np.float32).T
    if input_feat == 'rgb':
      feats = np.array([data['red'], data['green'], data['blue']], dtype=np.float32).T
    if input_feat == 'rgba':
      feats = np.array([data['red'], data['green'], data['blue'], data['alpha']], dtype=np.float32).T
    elif input_feat == 'normals':
      feats = np.array([data['nx'], data['ny'], data['nz']], dtype=np.float32).T
    elif input_feat == 'normals_rgb':
      feats = np.array([data['nx'], data['ny'], data['nz'], data['red'], data['green'], data['blue']],
                       dtype=np.float32).T
    elif input_feat == 'normals_rgba':
      feats = np.array([data['nx'], data['ny'], data['nz'], data['red'], data['green'], data['blue'], data['alpha']],
                       dtype=np.float32).T
    labels = np.array(data['label'], dtype=np.int32)
    return coords, feats, labels

  def __len__(self):
    num_data = len(self.data_paths)
    if self.prefetch_data:
      num_data = len(self.prefetched_coords)
    if self.rot_aug:
     num_data *= self.N_ROTATIONS
    return num_data


class VoxelizationDataset(VoxelizationDatasetBase):
  """This dataset loads RGB point clouds and their labels as a list of points
  and voxelizes the pointcloud with sufficient data augmentation.
  """
  # Voxelization arguments
  VOXEL_SIZE = 0.05  # 5cm

  # Augment coords to feats
  AUGMENT_COORDS_TO_FEATS = False

  def __init__(self,
               data_paths,
               prevoxel_transform=None,
               data_root='/',
               ignore_label=255,
               return_transformation=False,
               rot_aug=False,
               config=None,
               **kwargs):

    self.config = config
    VoxelizationDatasetBase.__init__(
        self,
        data_paths,
        prevoxel_transform=prevoxel_transform,
        prefetch_data=self.config.prefetch_data,
        data_root=data_root,
        ignore_mask=ignore_label,
        return_transformation=return_transformation,
        rot_aug=rot_aug,
        input_feat=self.input_feat)

    # Prevoxel transformations
    self.voxelizer = Voxelizer(
        voxel_size=self.VOXEL_SIZE,
        ignore_label=ignore_label)

    # map labels not evaluated to ignore_label
    label_map = {}
    n_used = 0
    for l in range(self.NUM_LABELS):
      if l in self.IGNORE_LABELS:
        label_map[l] = self.ignore_mask
      else:
        label_map[l] = n_used
        n_used += 1
    label_map[self.ignore_mask] = self.ignore_mask
    self.label_map = label_map
    self.NUM_LABELS -= len(self.IGNORE_LABELS)

  def _augment_coords_to_feats(self, coords, feats, labels=None):
    norm_coords = coords - coords.mean(0)
    # color must come first.
    if isinstance(coords, np.ndarray):
      feats = np.concatenate((feats, norm_coords), 1)
    else:
      feats = torch.cat((feats, norm_coords), 1)
    return coords, feats, labels

  def __getitem__(self, index):
    if self.rot_aug:
      index, angle = self.rotation_map[index]
      t.RotationAugmentation.update_angle(angle)
    if self.config.prefetch_data:
      coords = np.copy(self.prefetched_coords[index])
      feats = np.copy(self.prefetched_feats[index])
      labels = np.copy(self.prefetched_labels[index])
    else:
      coords, feats, labels = self.load_ply(index)

    # Prevoxel transformations
    if self.prevoxel_transform is not None:
      coords, feats, labels = self.prevoxel_transform(coords, feats, labels)

    coords, feats, labels, transformation = self.voxelizer.voxelize(
        coords, feats, labels)

    # map labels not used for evaluation to ignore_label
    if self.IGNORE_LABELS is not None:
      labels = np.array([self.label_map[x] for x in labels], dtype=np.int)

    # Use coordinate features if config is set
    if self.AUGMENT_COORDS_TO_FEATS:
      coords, feats, labels = self._augment_coords_to_feats(coords, feats, labels)

    return_args = [coords, feats, labels]
    if self.return_transformation:
      return_args.append(transformation.astype(np.float32))

    try:
      assert(not np.isnan(coords).any())
    except AssertionError:
      print(self.data_root / self.data_paths[index])
      raise
    try:
      assert(not np.isnan(feats).any())
    except AssertionError:
      print(self.data_root / self.data_paths[index])
      raise
    try:
      assert(not np.isnan(labels).any())
    except AssertionError:
      print(self.data_root / self.data_paths[index])
      raise
    return tuple(return_args)


def initialize_data_loader(DatasetClass,
                           config,
                           phase,
                           num_workers,
                           shuffle,
                           repeat,
                           shift,
                           rot_aug,
                           batch_size,
                           limit_numpoints):
  if isinstance(phase, str):
    phase = str2datasetphase_type(phase)

  if config.return_transformation:
    collate_fn = t.cflt_collate_fn_factory(limit_numpoints)
  else:
    collate_fn = t.cfl_collate_fn_factory(limit_numpoints)

  prevoxel_transform_train = []
  if rot_aug:
    prevoxel_transform_train.append(t.RotationAugmentation(True if 'normals' in config.input_feat else False))
  if shift:
    prevoxel_transform_train.append(t.RandomShift(*DatasetClass.SHIFT_PARAMS))

  if len(prevoxel_transform_train) > 0:
    prevoxel_transforms = t.Compose(prevoxel_transform_train)
  else:
    prevoxel_transforms = None

  dataset = DatasetClass(
      config,
      prevoxel_transform=prevoxel_transforms,
      rot_aug=rot_aug,
      phase=phase)

  data_args = {
      'dataset': dataset,
      'num_workers': num_workers,
      'batch_size': batch_size,
      'collate_fn': collate_fn,
  }

  if repeat:
    data_args['sampler'] = InfSampler(dataset, shuffle)
  else:
    data_args['shuffle'] = shuffle

  data_loader = DataLoader(**data_args)

  return data_loader
