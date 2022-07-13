import numpy as np

import torch.multiprocessing as mp
try:
  mp.set_start_method('forkserver')  # Reuse process created
except RuntimeError:
  pass

import os
import sys
import json
import logging
from easydict import EasyDict as edict

# Torch packages
import torch
from torch import nn

# Train deps
from config import get_config

import MinkowskiEngine as ME

from lib.test import test
from lib.train_multi_gpu import train
from lib.utils import get_torch_device, count_parameters
from lib.dataset import initialize_data_loader
from lib.datasets import load_dataset
from lib.export_features import get_feats

from models import load_model

ch = logging.StreamHandler(sys.stdout)
logging.basicConfig(format=os.uname()[1].split('.')[0] + ' -- %(asctime)s -- %(filename)s -- %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.INFO,
                    handlers=[ch])


def main():
  config = get_config()
  if config.resume:
    json_config = json.load(open(config.resume + '/config.json', 'r'))
    json_config['resume'] = config.resume
    config = edict(json_config)

  if config.is_cuda and not torch.cuda.is_available():
    raise Exception("No GPU found")

  if config.is_train:
    # Find maximum number of available devices
    num_devices = torch.cuda.device_count()
    num_devices = min(config.max_ngpu, num_devices)
    devices = list(range(num_devices))
    # For copying the final loss back to one GPU
    target_device = devices[0]
    logging.info('===> Multi GPU training')
    for device in devices:
      logging.info('    GPU {}: {}'.format(device, torch.cuda.get_device_name(device)))
    try:
      cuda_visible_devices = os.environ['CUDA_VISIBLE_DEVICES']
      logging.info('    CUDA_VISIBLE_DEVICES: {}'.format(cuda_visible_devices))
    except:
      pass
  else:
    target_device = get_torch_device(config.is_cuda)

  logging.info('===> Configurations')
  dconfig = vars(config)
  for k in dconfig:
    logging.info('    {}: {}'.format(k, dconfig[k]))

  DatasetClass = load_dataset(config.dataset)
  if config.test_original_pointcloud:
    if not DatasetClass.IS_FULL_POINTCLOUD_EVAL:
      raise ValueError('This dataset does not support full pointcloud evaluation.')

  if config.evaluate_original_pointcloud:
    if not config.return_transformation:
      raise ValueError('Pointcloud evaluation requires config.return_transformation=true.')

  if config.export_feat:
    get_feats(DatasetClass, config)
    exit(0)

  logging.info('===> Initializing dataloader')
  if config.is_train:
    # Devide batch size into multiple gpus
    assert(config.batch_size % num_devices == 0)
    batch_size = int(config.batch_size / num_devices)
    train_data_loader = initialize_data_loader(
        DatasetClass,
        config,
        phase=config.train_phase,
        num_workers=config.num_workers,
        shift=config.shift,
        rot_aug = config.rot_aug,
        shuffle=True,
        repeat=True,
        batch_size=batch_size,
        limit_numpoints=config.train_limit_numpoints)
    val_data_loader = initialize_data_loader(
        DatasetClass,
        config,
        num_workers=config.num_val_workers,
        phase=config.val_phase,
        shift=False,
        rot_aug=False,
        shuffle=True,
        repeat=False,
        batch_size=config.val_batch_size,
        limit_numpoints=False)
    if train_data_loader.dataset.NUM_IN_CHANNEL is not None:
      num_in_channel = train_data_loader.dataset.NUM_IN_CHANNEL
    else:
      num_in_channel = 3  # RGB color
    num_labels = train_data_loader.dataset.NUM_LABELS
  else:
    test_data_loader = initialize_data_loader(
        DatasetClass,
        config,
        num_workers=config.num_workers,
        phase=config.test_phase,
        shift=False,
        rot_aug=False,
        shuffle=False,
        repeat=False,
        batch_size=config.test_batch_size,
        limit_numpoints=False)
    if test_data_loader.dataset.NUM_IN_CHANNEL is not None:
      num_in_channel = test_data_loader.dataset.NUM_IN_CHANNEL
    else:
      num_in_channel = 3  # RGB color

    num_labels = test_data_loader.dataset.NUM_LABELS

  logging.info('===> Building model')
  NetClass = load_model(config.model)
  model = NetClass(num_in_channel, num_labels, config)
  logging.info('===> Number of trainable parameters: {}: {}'.format(NetClass.__name__, count_parameters(model)))

  logging.info(model)
  model = model.to(target_device)
  if config.is_train:
    # Synchronized batch norm
    model = ME.MinkowskiSyncBatchNorm.convert_sync_batchnorm(model)

  test_iter = 0
  # Load weights if specified by the parameter.
  if config.weights.lower() != 'none':
    logging.info('===> Loading weights: ' + config.weights)
    state = torch.load(config.weights)
    model.load_state_dict(state['state_dict'])
    if 'iteration' in state:
        test_iter = state['iteration']

  if config.is_train:
    train(model, train_data_loader, val_data_loader, devices, config)
  else:
    weights = None
    if config.weighted_cross_entropy:
      # Re-weight the loss function by assigning relatively higher costs to examples from minor classes
      weights = []
      for id in range(1, test_data_loader.dataset.NUM_LABELS + 1):
        weights.append(test_data_loader.dataset.NORM_FREQ[id])
      weights = np.asarray(weights)
      weights = 1 + np.log10(weights)
      min_weight = np.amin(weights)
      max_weight = np.amax(weights)
      weights = (weights - min_weight) / (max_weight - min_weight) + 1
      weights = torch.from_numpy(weights).float()
      weights = weights.cuda()
    v_loss, v_score, v_mIoU = test(model, test_data_loader, config, weights=weights)
    logging.info("Test split mIoU: {:.3f} at iter {}".format(v_mIoU, test_iter))
    logging.info("Test split Loss: {:.3f} at iter {}".format(v_loss, test_iter))
    logging.info("Test Score: {:.3f} at iter {}".format(v_score, test_iter))


if __name__ == '__main__':
  __spec__ = None
  main()
