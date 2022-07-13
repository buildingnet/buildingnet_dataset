import logging
import os.path as osp
import numpy as np

import torch
from torch import nn
import torch.nn.parallel as parallel

from tensorboardX import SummaryWriter

from lib.test import test
from lib.utils import checkpoint, precision_at_one, \
    Timer, AverageMeter, get_prediction, get_torch_device
from lib.solvers import initialize_optimizer, initialize_scheduler

from MinkowskiEngine import SparseTensor


def validate(model, val_data_loader, writer, curr_iter, config, weights=None):
  v_loss, v_score, v_mIoU = test(model, val_data_loader, config, weights=weights)
  writer.add_scalar('validation/mIoU', v_mIoU, curr_iter)
  writer.add_scalar('validation/loss', v_loss, curr_iter)
  writer.add_scalar('validation/precision_at_1', v_score, curr_iter)

  return v_mIoU, v_loss, v_score


def train(model, data_loader, val_data_loader, devices, config):
  # Set up the train flag for batch normalization
  model.train()
  # Set target device
  target_device = devices[0]

  # Configuration
  writer = SummaryWriter(log_dir=config.log_dir)
  data_timer, iter_timer = Timer(), Timer()
  data_time_avg, iter_time_avg = AverageMeter(), AverageMeter()
  losses, scores = AverageMeter(), AverageMeter()

  optimizer = initialize_optimizer(model.parameters(), config)
  scheduler = initialize_scheduler(optimizer, config)
  weights = None
  if config.weighted_cross_entropy:
    # Re-weight the loss function by assigning relatively higher costs to examples from minor classes
    weights = []
    for id in range(1, data_loader.dataset.NUM_LABELS + 1):
      weights.append(data_loader.dataset.NORM_FREQ[id])
    weights = np.asarray(weights)
    weights = 1 + np.log10(weights)
    min_weight = np.amin(weights)
    max_weight = np.amax(weights)
    weights = (weights - min_weight) / (max_weight - min_weight) + 1
    weights = torch.from_numpy(weights).float()
    weights = weights.cuda()
    criterion = nn.CrossEntropyLoss(ignore_index=config.ignore_label, weight=weights)
  else:
    criterion = nn.CrossEntropyLoss(ignore_index=config.ignore_label)
  # Copy the loss layer
  criterions = parallel.replicate(criterion, devices)

  # Train the network
  logging.info('===> Start training')
  best_val_miou, best_val_iter, best_val_loss, best_val_loss_iter, best_val_acc, best_val_acc_iter, curr_iter, epoch, is_training = \
    0, 0, np.Inf, 0, 0, 0, 1, 1, True

  if config.resume:
    checkpoint_fn = config.resume + '/weights.pth'
    if osp.isfile(checkpoint_fn):
      logging.info("=> loading checkpoint '{}'".format(checkpoint_fn))
      state = torch.load(checkpoint_fn)
      curr_iter = state['iteration'] + 1
      epoch = state['epoch']
      model.load_state_dict(state['state_dict'])
      if config.resume_optimizer:
        scheduler = initialize_scheduler(optimizer, config, last_step=curr_iter)
        optimizer.load_state_dict(state['optimizer'])
      if 'best_val' in state:
        best_val_miou = state['best_val']
        best_val_iter = state['best_val_iter']
      if 'best_val_loss' in state:
        best_val_loss = state['best_val_loss']
        best_val_loss_iter = state['best_val_loss_iter']
      if 'best_val_acc' in state:
        best_val_acc = state['best_val_acc']
        best_val_acc_iter = state['best_val_acc_iter']
      logging.info("=> loaded checkpoint '{}' (epoch {})".format(checkpoint_fn, state['epoch']))
    else:
      raise ValueError("=> no checkpoint found at '{}'".format(checkpoint_fn))

  if config.save_param_histogram:
    # Log parameters
    logging.info("Log network parameters")
    model_name = model.__class__.__name__
    for name, weight in model.named_parameters():
      writer.add_histogram(model_name + '/' + name, weight, curr_iter)
      if weight.grad is not None:
        writer.add_histogram(model_name + '/' + name + '.grad', weight.grad, curr_iter)

  data_iter = data_loader.__iter__()
  num_gpus = len(devices)
  num_data = len(data_loader)
  while is_training:
    for iteration in range(num_data // num_gpus):
      optimizer.zero_grad()
      data_time, batch_loss = 0, 0
      iter_timer.tic()

      # Get new data
      inputs, all_labels = [], []
      data_timer.tic()
      for sub_iter in range(num_gpus):
        # Get training data
        coords, input, target = data_iter.next()

        with torch.cuda.device(devices[sub_iter]):
          inputs.append(SparseTensor(input, coords).to(devices[sub_iter]))
        all_labels.append(target.long().to(devices[sub_iter]))
      data_time += data_timer.toc(False)

      # Feed forward
      # The raw version of the parallel_apply
      replicas = parallel.replicate(model, devices)
      outputs = parallel.parallel_apply(replicas, inputs, devices=devices)

      # Extract features from the sparse tensors to use a pytorch criterion
      out_features = [output.F for output in outputs]
      parallel_losses = parallel.parallel_apply(criterions, tuple(zip(out_features, all_labels)), devices=devices)
      loss = parallel.gather(parallel_losses, target_device, dim=0).mean()

      # Compute and accumulate gradient
      batch_loss += loss.item()
      loss.backward()
      torch.cuda.empty_cache()

      # Update number of steps
      optimizer.step()
      if config.scheduler != "ReduceLROnPlateau":
        scheduler.step()

      data_time_avg.update(data_time)
      iter_time_avg.update(iter_timer.toc(False))

      score, all_labels_size = 0, 0
      for sub_iter in range(num_gpus):
        all_labels_size += all_labels[sub_iter].size(0)
        pred = get_prediction(data_loader.dataset, out_features[sub_iter], all_labels[sub_iter])
        score += precision_at_one(pred, all_labels[sub_iter])
      score /= float(num_gpus)
      losses.update(batch_loss, all_labels_size)
      scores.update(score, all_labels_size)

      if curr_iter >= config.max_iter:
        is_training = False
        break

      if curr_iter % config.stat_freq == 0 or curr_iter == 1:
        lrs = ', '.join(['{:.3e}'.format(optimizer.param_groups[0]['lr'])])
        debug_str = "===> Epoch[{}]({}/{}): Loss {:.4f}\tLR: {}\t".format(
            epoch, curr_iter,
            len(data_loader) // num_gpus, losses.avg, lrs)
        debug_str += "Score {:.3f}\tData time: {:.4f}, Total iter time: {:.4f}".format(
            scores.avg, data_time_avg.avg, iter_time_avg.avg)
        logging.info(debug_str)
        # Reset timers
        data_time_avg.reset()
        iter_time_avg.reset()
        # Write logs
        writer.add_scalar('training/loss', losses.avg, curr_iter)
        writer.add_scalar('training/precision_at_1', scores.avg, curr_iter)
        writer.add_scalar('training/learning_rate', optimizer.param_groups[0]['lr'], curr_iter)
        losses.reset()
        scores.reset()

      # Save current status, save before val to prevent occational mem overflow
      if curr_iter % config.save_freq == 0:
        checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
                   best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
                   best_val_acc_iter=best_val_acc_iter)

      # Validation
      if curr_iter % config.val_freq == 0:
        val_miou, val_loss, val_score = validate(model, val_data_loader, writer, curr_iter, config, weights)
        if val_miou > best_val_miou:
          best_val_miou = val_miou
          best_val_iter = curr_iter
          checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
                     best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
                     best_val_acc_iter=best_val_acc_iter, postfix='best_val')
        if val_loss < best_val_loss:
          best_val_loss = val_loss
          best_val_loss_iter = curr_iter
          checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
                     best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
                     best_val_acc_iter=best_val_acc_iter, postfix='best_loss')
        if val_score > best_val_acc:
          best_val_acc = val_score
          best_val_acc_iter = curr_iter
          checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
                     best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
                     best_val_acc_iter=best_val_acc_iter, postfix='best_acc')

        logging.info("Current best mIoU: {:.3f} at iter {}".format(best_val_miou, best_val_iter))
        logging.info("Current best Loss: {:.3f} at iter {}".format(best_val_loss, best_val_loss_iter))
        logging.info("Current best Score: {:.3f} at iter {}".format(best_val_acc, best_val_acc_iter))

        # Recover back
        model.train()

      # End of iteration
      curr_iter += 1

    if config.scheduler == "ReduceLROnPlateau":
      try:
        scheduler.step(val_loss)
      except UnboundLocalError:
        pass

    if config.save_param_histogram and epoch % config.param_histogram_freq == 0:
      # Log parameters
      logging.info("Log network parameters")
      model_name = model.__class__.__name__
      for name, weight in model.named_parameters():
        writer.add_histogram(model_name + '/' + name, weight, curr_iter)
        if weight.grad is not None:
          writer.add_histogram(model_name + '/' + name + '.grad', weight.grad, curr_iter)

    # Enc of epoch
    epoch += 1

  # Explicit memory cleanup
  if hasattr(data_iter, 'cleanup'):
    data_iter.cleanup()

  # Save the final model
  val_miou, val_loss, val_score = validate(model, val_data_loader, writer, curr_iter, config, weights)
  if val_miou > best_val_miou:
    best_val_miou = val_miou
    best_val_iter = curr_iter
    checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
               best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
               best_val_acc_iter=best_val_acc_iter, postfix='best_val')
  if val_loss < best_val_loss:
    best_val_loss = val_loss
    best_val_loss_iter = curr_iter
    checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
               best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
               best_val_acc_iter=best_val_acc_iter, postfix='best_loss')
  if val_score > best_val_acc:
    best_val_acc = val_score
    best_val_acc_iter = curr_iter
    checkpoint(model, optimizer, epoch, curr_iter, config, best_val=best_val_miou, best_val_iter=best_val_iter,
               best_val_loss=best_val_loss, best_val_loss_iter=best_val_loss_iter, best_val_acc=best_val_acc,
               best_val_acc_iter=best_val_acc_iter, postfix='best_acc')

  logging.info("Current best mIoU: {:.3f} at iter {}".format(best_val_miou, best_val_iter))
  logging.info("Current best Loss: {:.3f} at iter {}".format(best_val_loss, best_val_loss_iter))
  logging.info("Current best Score: {:.3f} at iter {}".format(best_val_acc, best_val_acc_iter))
