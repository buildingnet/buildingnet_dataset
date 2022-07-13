import logging
import os
import shutil
import tempfile
import warnings

import numpy as np
import torch
import torch.nn as nn

from lib.utils import Timer, AverageMeter, precision_at_one, fast_hist, per_class_iu, \
    get_prediction, get_torch_device, save_output_features_buildingnet

from MinkowskiEngine import SparseTensor


def print_info(iteration,
               max_iteration,
               data_time,
               iter_time,
               has_gt=False,
               losses=None,
               scores=None,
               ious=None,
               hist=None,
               class_names=None):
  debug_str = "{}/{}: ".format(iteration + 1, max_iteration)
  debug_str += "Data time: {:.4f}, Iter time: {:.4f}".format(data_time, iter_time)

  if has_gt:
    acc = hist.diagonal() / hist.sum(1) * 100
    debug_str += "\tLoss {loss.val:.3f} (AVG: {loss.avg:.3f})\t" \
        "Score {top1.val:.3f} (AVG: {top1.avg:.3f})\t" \
        "mIOU {mIOU:.3f} mAcc {mAcc:.3f}\n".format(
            loss=losses, top1=scores, mIOU=np.nanmean(ious),
            mAcc=np.nanmean(acc))
    if class_names is not None:
      debug_str += "\nClasses: " + " ".join(class_names) + '\n'
    debug_str += 'IOU: ' + ' '.join('{:.03f}'.format(i) for i in ious) + '\n'
    debug_str += 'mAcc: ' + ' '.join('{:.03f}'.format(i) for i in acc) + '\n'

  logging.info(debug_str)


def test(model, data_loader, config, has_gt=True, weights=None):
  device = get_torch_device(config.is_cuda)
  dataset = data_loader.dataset
  num_labels = dataset.NUM_LABELS
  global_timer, data_timer, iter_timer = Timer(), Timer(), Timer()
  if config.weighted_cross_entropy:
    criterion = nn.CrossEntropyLoss(ignore_index=config.ignore_label, weight=weights)
  else:
    criterion = nn.CrossEntropyLoss(ignore_index=config.ignore_label)
  losses, scores, ious = AverageMeter(), AverageMeter(), 0
  hist = np.zeros((num_labels, num_labels))

  logging.info('===> Start testing')

  global_timer.tic()
  data_iter = data_loader.__iter__()
  max_iter = len(data_loader)
  max_iter_unique = max_iter

  # Fix batch normalization running mean and std
  model.eval()

  # Clear cache (when run in val mode, cleanup training cache)
  torch.cuda.empty_cache()

  if config.save_prediction:
    save_pred_dir = config.save_pred_dir
    os.makedirs(save_pred_dir, exist_ok=True)
  else:
    save_pred_dir = tempfile.mkdtemp()
  if os.listdir(save_pred_dir):
    raise ValueError(f'Directory {save_pred_dir} not empty. '
                     'Please remove the existing prediction.')

  with torch.no_grad():
    for iteration in range(max_iter):
      data_timer.tic()
      if config.return_transformation:
        coords, input, target, transformation = data_iter.next()
      else:
        coords, input, target = data_iter.next()
        transformation = None
      data_time = data_timer.toc(False)

      # Preprocess input
      iter_timer.tic()

      sinput = SparseTensor(input, coords).to(device)

      # Feed forward
      soutput = model(sinput)
      output = soutput.F

      pred = get_prediction(dataset, output, target).int()
      iter_time = iter_timer.toc(False)

      if config.save_prediction:
        save_output_features_buildingnet(coords, output, pred, transformation, dataset, config, iteration, save_pred_dir)

      if has_gt:
        target_np = target.numpy()

        num_sample = target_np.shape[0]

        target = target.to(device)

        cross_ent = criterion(output, target.long())
        losses.update(float(cross_ent), num_sample)
        scores.update(precision_at_one(pred, target), num_sample)
        hist += fast_hist(pred.cpu().numpy().flatten(), target_np.flatten(), num_labels)
        ious = per_class_iu(hist) * 100
        ious = np.nan_to_num(ious)

      if iteration % config.test_stat_freq == 0 and iteration > 0:
        reordered_ious = dataset.reorder_result(ious)
        class_names = dataset.get_classnames()
        print_info(
            iteration,
            max_iter_unique,
            data_time,
            iter_time,
            has_gt,
            losses,
            scores,
            reordered_ious,
            hist,
            class_names=class_names)

      if iteration % config.empty_cache_freq == 0:
        # Clear cache
        torch.cuda.empty_cache()

  global_time = global_timer.toc(False)

  reordered_ious = dataset.reorder_result(ious)
  class_names = dataset.get_classnames()
  print_info(
      iteration,
      max_iter_unique,
      data_time,
      iter_time,
      has_gt,
      losses,
      scores,
      reordered_ious,
      hist,
      class_names=class_names)

  if config.test_original_pointcloud:
    logging.info('===> Start testing on original pointcloud space.')
    dataset.test_pointcloud(save_pred_dir)

  logging.info("Finished test. Elapsed time: {:.4f}".format(global_time))

  return losses.avg, scores.avg, np.nanmean(per_class_iu(hist)) * 100
