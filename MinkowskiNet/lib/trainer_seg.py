import logging
import os.path as osp
import os
import numpy as np
import torch
from torch import nn
from torch.utils.tensorboard import SummaryWriter

from lib.utils import checkpoint, Timer, AverageMeter, get_torch_device
from lib.eval_utils import classification_accuracy, calc_building_point_iou, calc_building_mesh_iou, calc_shape_iou, \
	calc_part_iou, LABELS
from lib.solvers import initialize_optimizer, initialize_scheduler
from lib.dataset import DatasetPhase

import MinkowskiEngine as ME


class Trainer():

	def __init__(self, model, data_loader, val_data_loader, config, mink_settings):

		# Configuration
		self.device = get_torch_device(config.is_cuda)
		self.model = model
		self.model_name = self.model.__class__.__name__
		self.data_loader = data_loader
		self.val_data_loader = val_data_loader
		self.config = config
		self.mink_settings = mink_settings

		self.writer = SummaryWriter(log_dir=self.config.log_dir)
		self.data_timer, self.iter_timer = Timer(), Timer()
		self.data_time_avg, self.iter_time_avg = AverageMeter(), AverageMeter()
		self.train_loss, self.train_part_iou, self.train_shape_iou, self.train_acc = AverageMeter(), AverageMeter(), \
																					 AverageMeter(), AverageMeter()

		self.optimizer = initialize_optimizer(self.model.parameters(), self.config)
		# Number of batches
		self.data_len = len(self.data_loader)
		self.config.max_iter = self.data_len * self.config.max_epoch
		self.config.stat_freq = self.data_len // 5
		self.min_lr_factor, self.lr_factor, self.mlt_stp_gamma, self.milestones_pct = 1e-4, 0.5, 0.1, [0.8, 0.9]
		self.min_lr = self.config.lr * self.min_lr_factor
		self.lr_milestones = [int(self.config.max_iter * pct) for pct in self.milestones_pct]

		self.scheduler = initialize_scheduler(self.optimizer, self.config, factor=self.lr_factor,
											  milestones=self.lr_milestones, mlt_stp_gamma=self.mlt_stp_gamma,
											  min_lr=self.min_lr)

		if self.config.weighted_cross_entropy:
			# Re-weight the loss function by assigning relatively higher costs to examples from minor classes
			weights = []
			for id in range(1, self.data_loader.dataset.NUM_LABELS + 1):
				weights.append(self.data_loader.dataset.NORM_FREQ[id])
			weights = np.asarray(weights)
			weights = 1 + np.log10(weights)
			min_weight = np.amin(weights)
			max_weight = np.amax(weights)
			weights = (weights - min_weight) / (max_weight - min_weight) + 1
			weights = torch.from_numpy(weights).float()
			weights = weights.cuda()
			self.criterion = nn.CrossEntropyLoss(ignore_index=self.config.ignore_label, weight=weights)
		else:
			self.criterion = nn.CrossEntropyLoss(ignore_index=self.config.ignore_label)

		self.best_val_part_iou, self.best_val_part_iou_iter = 0, 0
		self.best_val_shape_iou, self.best_val_shape_iou_iter = 0, 0
		self.best_val_loss, self.best_val_loss_iter = np.Inf, 0
		self.best_val_acc, self.best_val_acc_iter = 0, 0
		self.curr_iter, self.epoch, self.is_training = 1, 1, True

	def train(self):
		# Train the network
		self.model.train()
		logging.info('===> Start training')

		if self.config.resume:
			# Resume training
			self._resume()

		if self.config.save_param_histogram:
			# Log initial params histograms
			self._log_params()

		self.data_iter = self.data_loader.__iter__()
		torch.autograd.set_detect_anomaly(True)

		while self.is_training:

			### START OF EPOCH
			for iteration in range(self.data_len):
				# Train for one iteration
				self._train_iter()

				if self.curr_iter % self.config.stat_freq == 0 or self.curr_iter == 1:
					# Log stats
					self._log_stats()

				# End of iteration
				self.curr_iter += 1
			### END OF EPOCH

			if self.epoch >= self.config.max_epoch:
				# Terminate training
				self.is_training = False
				break

			# Save current status, save before val to prevent occational mem overflow
			self._save_curr_checkpoint()

			# Validation
			val_loss, val_acc, val_part_iou, val_shape_iou = self._validate()
			self._save_best_checkpoints(val_loss, val_acc, val_part_iou, val_shape_iou)
			self._log_val_stats()

			# Recover back
			self.model.train()

			if self.config.scheduler == "ReduceLROnPlateau":
				try:
					self.scheduler.step(val_loss)
				except UnboundLocalError:
					pass

			if self.config.save_param_histogram:
				# Log params histograms
				if self.epoch % self.config.param_histogram_freq == 0:
					self._log_params()
			self.train_loss.reset()
			self.train_part_iou.reset()
			self.train_shape_iou.reset()
			self.train_acc.reset()
			self.epoch += 1

		# Explicit memory cleanup
		if hasattr(self.data_iter, 'cleanup'):
			self.data_iter.cleanup()

		# Save the final model
		val_loss, val_acc, val_part_iou, val_shape_iou = self._validate()
		self._save_curr_checkpoint()
		self._save_best_checkpoints(val_loss, val_acc, val_part_iou, val_shape_iou)
		self._log_val_stats()
		self._log_params()
		self.writer.flush()

	def _train_iter(self):
		self.optimizer.zero_grad()

		self.iter_timer.tic()

		# Get training data
		self.data_timer.tic()
		in_field, target = self._fetch_data()
		sinput = in_field.sparse()
		data_time = self.data_timer.toc(False)

		# Feed forward
		soutput = self.model(sinput)
		out_field = soutput.interpolate(in_field)
		target = target.long().to(self.device)

		loss = self.criterion(out_field.F, target.long())

		# Compute gradients
		batch_loss = loss.item()
		loss.backward()

		# Update number of steps
		self.optimizer.step()
		if self.config.scheduler != "ReduceLROnPlateau":
			self.scheduler.step()
		torch.cuda.empty_cache()

		self.data_time_avg.update(data_time)
		self.iter_time_avg.update(self.iter_timer.toc(False))

		# Calculate buildings iou and acc
		buildings_iou, buildings_acc = {}, {}
		batch_size = torch.max(out_field.C[:, 0]).cpu().numpy().astype(int) + 1
		gt_labels = target.cpu().numpy().astype(int)
		# Rearrange labels since undetermined is excluded
		gt_labels += 1
		gt_labels[gt_labels == (self.config.ignore_label + 1)] = 0
		gt_labels = gt_labels.reshape(batch_size, -1)[..., np.newaxis]
		pred_labels = torch.max(out_field.F, 1)[1] + 1 # undetermined is excluded
		pred_labels = pred_labels.cpu().numpy().astype(int).reshape(batch_size, -1)[..., np.newaxis]
		for batch_ind in range(batch_size):
			gt_shape = gt_labels[batch_ind]
			pred_shape = pred_labels[batch_ind]
			buildings_iou[batch_ind] = calc_building_point_iou(gt_shape, pred_shape, LABELS)
			buildings_acc[batch_ind] = classification_accuracy(gt_shape, pred_shape)
		part_iou = calc_part_iou(buildings_iou, LABELS)
		shape_iou = calc_shape_iou(buildings_iou)
		class_acc = np.sum([acc for acc in buildings_acc.values()]) / float(len(buildings_acc))

		self.train_loss.update(batch_loss, 1)
		self.train_part_iou.update(part_iou["all"] * 100, 1)
		self.train_shape_iou.update(shape_iou["all"] * 100, 1)
		self.train_acc.update(class_acc * 100, 1)

	def _validate(self):
		loss, acc, part_iou, shape_iou= Trainer.test(self.model, self.val_data_loader, self.config, self.mink_settings)
		self.writer.add_scalar('validation/loss', loss, self.curr_iter)
		self.writer.add_scalar('validation/PartIoU', part_iou, self.curr_iter)
		self.writer.add_scalar('validation/ShapeIoU', shape_iou, self.curr_iter)
		self.writer.add_scalar('validation/acc', acc, self.curr_iter)

		return loss, acc, part_iou, shape_iou

	def _fetch_data(self):
		coords, input, target = self.data_iter.next()
		in_field = ME.TensorField(
			features=input,
			coordinates=coords,
			quantization_mode=self.mink_settings["q_mode"],
			minkowski_algorithm=self.mink_settings["mink_algo"],
			device=self.device)

		return in_field, target

	def _log_stats(self):
		lr = ', '.join([f"{self.optimizer.param_groups[0]['lr']:.3e}"])
		debug_str = f"===> Epoch[{self.epoch}]({self.curr_iter}/{self.data_len}): " \
					f"Loss {self.train_loss.avg:.4f}\tLR: {lr}\t"
		debug_str += f"Part IoU {self.train_part_iou.avg:.2f}\tShape IoU {self.train_shape_iou.avg:.2f}\t" \
					 f"Acc {self.train_acc.avg:.2f}\tData time: {self.data_time_avg.avg:.4f}\t" \
					 f"Total iter time: {self.iter_time_avg.avg:.4f}"
		logging.info(debug_str)
		# Reset timers
		self.data_time_avg.reset()
		self.iter_time_avg.reset()
		# Write logs
		self.writer.add_scalar('training/loss', self.train_loss.avg, self.curr_iter)
		self.writer.add_scalar('training/PartIoU', self.train_part_iou.avg, self.curr_iter)
		self.writer.add_scalar('training/ShapeIoU', self.train_shape_iou.avg, self.curr_iter)
		self.writer.add_scalar('training/acc', self.train_acc.avg, self.curr_iter)
		self.writer.add_scalar('training/learning_rate', self.optimizer.param_groups[0]['lr'], self.curr_iter)

	def _log_val_stats(self):
		logging.info("Current best Part IoU: {:.2f} at iter {}"
		             .format(self.best_val_part_iou, self.best_val_part_iou_iter))
		logging.info("Current best Shape IoU: {:.2f} at iter {}"
		             .format(self.best_val_shape_iou, self.best_val_shape_iou_iter))
		logging.info("Current best Loss: {:.3f} at iter {}"
		             .format(self.best_val_loss, self.best_val_loss_iter))
		logging.info("Current best Acc: {:.2f} at iter {}"
		             .format(self.best_val_acc, self.best_val_acc_iter))

	def _log_params(self):
		for name, weight in self.model.named_parameters():
			self.writer.add_histogram(self.model_name+'/'+name, weight, self.epoch)
			if weight.grad is not None:
				self.writer.add_histogram(self.model_name + '/' + name + '.grad', weight.grad, self.epoch)

	def _save_curr_checkpoint(self, postfix=None):
		checkpoint(self.model, self.optimizer, self.epoch+1, self.curr_iter, self.config,
		           best_val_part_iou=self.best_val_part_iou, best_val_part_iou_iter=self.best_val_part_iou_iter,
		           best_val_shape_iou=self.best_val_shape_iou, best_val_shape_iou_iter=self.best_val_shape_iou_iter,
		           best_val_loss=self.best_val_loss,  best_val_loss_iter=self.best_val_loss_iter,
		           best_val_acc=self.best_val_acc, best_val_acc_iter=self.best_val_acc_iter, postfix=postfix)

	def _save_best_checkpoints(self, val_loss, val_acc, val_part_iou, val_shape_iou):
		if val_part_iou > self.best_val_part_iou:
			self.best_val_part_iou = val_part_iou
			self.best_val_part_iou_iter = self.curr_iter
			self._save_curr_checkpoint(postfix='best_part_iou')
		if val_shape_iou > self.best_val_shape_iou:
			self.best_val_shape_iou = val_shape_iou
			self.best_val_shape_iou_iter = self.curr_iter
			self._save_curr_checkpoint(postfix='best_shape_iou')
		if val_loss < self.best_val_loss:
			self.best_val_loss = val_loss
			self.best_val_loss_iter = self.curr_iter
			self._save_curr_checkpoint(postfix='best_loss')
		if val_acc > self.best_val_acc:
			self.best_val_acc = val_acc
			self.best_val_acc_iter = self.curr_iter
			self._save_curr_checkpoint(postfix='best_acc')

	def _resume(self):
		checkpoint_fn = self.config.resume + '/weights.pth'
		if osp.isfile(checkpoint_fn):
			logging.info("=> loading checkpoint '{}'".format(checkpoint_fn))
			state = torch.load(checkpoint_fn)
			self.curr_iter = state['iteration'] + 1
			self.epoch = state['epoch']
			self.model.load_state_dict(state['state_dict'])
			if self.config.resume_optimizer:
				self.scheduler = initialize_scheduler(self.optimizer, self.config, last_step=self.curr_iter,
													  factor=self.lr_factor, milestones=self.lr_milestones,
													  mlt_stp_gamma=self.mlt_stp_gamma, min_lr=self.min_lr)
				self.optimizer.load_state_dict(state['optimizer'])
			if 'best_val_part_iou' in state:
				self.best_val_part_iou = state['best_val_part_iou']
				self.best_val_part_iou_iter = state['best_val_part_iou_iter']
			if 'best_val_shape_iou' in state:
				self.best_val_shape_iou = state['best_val_shape_iou']
				self.best_val_shape_iou_iter = state['best_val_shape_iou_iter']
			if 'best_val_loss' in state:
				self.best_val_loss = state['best_val_loss']
				self.best_val_loss_iter = state['best_val_loss_iter']
			if 'best_val_acc' in state:
				self.best_val_acc = state['best_val_acc']
				self.best_val_acc_iter = state['best_val_acc_iter']
			logging.info("=> loaded checkpoint '{}' (epoch {})".format(checkpoint_fn, state['epoch']))
		else:
			raise ValueError("=> no checkpoint found at '{}'".format(checkpoint_fn))

	@staticmethod
	def print_info(iteration, max_iteration, data_time, iter_time, loss, acc, part_iou, shape_iou, all_part_iou):
		debug_str = f"{iteration+1}/{max_iteration}: "
		debug_str += f"Data time: {data_time:.4f}, Iter time: {iter_time:.4f}"
		debug_str += f"\tLoss {loss.avg:.3f}\tAcc {acc.avg:.2f}\t" \
		             f"Part IoU {part_iou.avg:.2f}\tShape IoU {shape_iou.avg:.2f}"
		logging.info(debug_str)
		str_len = 5
		cls_str = "Classes |" + "|".join([f" {name[:str_len].rjust(str_len)} " for name in all_part_iou.keys() if name != "all"])
		logging.info(cls_str)
		div_str = "-" * len(cls_str)
		logging.info(div_str)
		iou_str = "IoU     |" + "|".join([f" {iou * 100:05.2f} " for name, iou in all_part_iou.items() if name != "all"]) \
				  + "\n"
		logging.info(iou_str)

	@staticmethod
	def test(model, data_loader, config, mink_settings):
		device = get_torch_device(config.is_cuda)
		global_timer, data_timer, iter_timer = Timer(), Timer(), Timer()
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
		loss, acc, shape_iou, part_iou = AverageMeter(), AverageMeter(), AverageMeter(), AverageMeter()
		buildings_iou, buildings_acc = {}, {}

		logging.info('===> Start testing')

		global_timer.tic()
		data_iter = data_loader.__iter__()
		max_iter = len(data_loader)
		max_iter_unique = max_iter

		# Fix batch normalization running mean and std
		model.eval()

		# Clear cache (when run in val mode, cleanup training cache)
		torch.cuda.empty_cache()

		with torch.no_grad():
			for iteration in range(max_iter):
				iter_timer.tic()
				data_timer.tic()
				coords, input, target = data_iter.next()

				in_field = ME.TensorField(
					features=input,
					coordinates=coords,
					quantization_mode=mink_settings["q_mode"],
					minkowski_algorithm=mink_settings["mink_algo"],
					device=device)
				sinput = in_field.sparse()
				data_time = data_timer.toc(False)

				# Feed forward
				soutput = model(sinput)
				out_field = soutput.interpolate(in_field)
				output = out_field.F

				iter_time = iter_timer.toc(False)

				target = target.to(device)
				cross_ent = criterion(output, target.long())
				loss.update(float(cross_ent), 1)
				# Rearrange labels since undetermined is excluded
				gt_labels = target.cpu().numpy().astype(int)
				gt_labels += 1
				gt_labels[gt_labels == (config.ignore_label + 1)] = 0
				gt_labels = gt_labels[:, np.newaxis]
				pred_labels = torch.max(output, 1)[1] + 1  # undetermined is excluded
				pred_labels = pred_labels.cpu().numpy().astype(int)[:, np.newaxis]
				buildings_iou[iteration] = calc_building_point_iou(gt_labels, pred_labels, LABELS)
				buildings_acc[iteration] = classification_accuracy(gt_labels, pred_labels)

				if iteration % config.test_stat_freq == 0 and iteration > 0:
					all_part_iou = calc_part_iou(buildings_iou, LABELS)
					all_shape_iou = calc_shape_iou(buildings_iou)
					avg_acc = np.sum([acc for acc in buildings_acc.values()]) / float(len(buildings_acc))
					part_iou.update(all_part_iou["all"] * 100, len(buildings_iou))
					shape_iou.update(all_shape_iou["all"] * 100, len(buildings_iou))
					acc.update(avg_acc * 100, len(buildings_acc))
					Trainer.print_info(iteration, max_iter_unique, data_time, iter_time, loss, acc, part_iou, shape_iou,
									   all_part_iou)

				if iteration % config.empty_cache_freq == 0:
					# Clear cache
					torch.cuda.empty_cache()

		global_time = global_timer.toc(False)

		all_part_iou = calc_part_iou(buildings_iou, LABELS)
		all_shape_iou = calc_shape_iou(buildings_iou)
		avg_acc = np.sum([acc for acc in buildings_acc.values()]) / float(len(buildings_acc))
		part_iou.reset()
		shape_iou.reset()
		acc.reset()
		part_iou.update(all_part_iou["all"] * 100, len(buildings_iou))
		shape_iou.update(all_shape_iou["all"] * 100, len(buildings_iou))
		acc.update(avg_acc * 100, len(buildings_acc))
		Trainer.print_info(iteration, max_iter_unique, data_time, iter_time, loss, acc, part_iou, shape_iou,
						   all_part_iou)

		logging.info("Finished test. Elapsed time: {:.4f}".format(global_time))

		return loss.avg, acc.avg, part_iou.avg, shape_iou.avg

	@staticmethod
	def export_feat(model, data_loader, config, mink_settings):
		device = get_torch_device(config.is_cuda)
		global_timer = Timer()

		logging.info('===> Start exporting features')

		global_timer.tic()
		data_iter = data_loader.__iter__()
		max_iter = len(data_loader)

		# Fix batch normalization running mean and std
		model.eval()

		# Clear cache (when run in val mode, cleanup training cache)
		torch.cuda.empty_cache()

		out_features = {}
		with torch.no_grad():
			for iteration in range(max_iter):
				coords, input, target = data_iter.next()

				in_field = ME.TensorField(
					features=input,
					coordinates=coords,
					quantization_mode=mink_settings["q_mode"],
					minkowski_algorithm=mink_settings["mink_algo"],
					device=device)
				sinput = in_field.sparse()

				# Feed forward
				soutput = model(sinput)
				out_field = soutput.interpolate(in_field)
				output = out_field.F

				# Get per-point features
				per_point_feat = output.cpu().numpy().astype(np.float32)
				model_name = data_loader.dataset.data_paths[iteration].split('/')[-1].split('.ply')[0]
				out_features[f'{model_name}'] = per_point_feat

		# Save predictions
		if data_loader.dataset.phase == DatasetPhase.Train:
			split = 'train'
		elif data_loader.dataset.phase == DatasetPhase.Val:
			split = 'val'
		elif data_loader.dataset.phase == DatasetPhase.Test:
			split = 'test'
		else:
			raise ValueError(f'Unknown dataset split {data_loader.dataset.phase}')
		out_fn = os.path.join(config.log_dir, f"{model.__class__.__name__}_{split}_per_point_feat.npz")
		np.savez(out_fn, **out_features)

		global_time = global_timer.toc(False)
		logging.info("Finished exporting features. Elapsed time: {:.4f}".format(global_time))

		return out_fn
