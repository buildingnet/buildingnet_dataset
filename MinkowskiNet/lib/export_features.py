import logging
import os
import sys
import numpy as np
from scipy import spatial
import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
sys.setrecursionlimit(100000)  # Increase recursion limit for k-d tree.

from lib.utils import get_torch_device, count_parameters, Timer
from lib.dataset import initialize_data_loader
from models import load_model
from lib.pc_utils import read_plyfile
from lib.buildingnet_eval import transfer_point_predictions, get_mesh_data

from MinkowskiEngine import SparseTensor

# BuildingNet directories
BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
assert (os.path.isdir(BUILDINGNET_BASE_DIR))
BUILDINGNET_OBJ_DIR = os.path.join(BUILDINGNET_BASE_DIR, "OBJ_MODELS")
assert (os.path.isdir(BUILDINGNET_OBJ_DIR))
BUILDINGNET_PTS_FACEINDEX_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_faceindex")
assert (os.path.isdir(BUILDINGNET_PTS_FACEINDEX_DIR))
BUILDINGNET_COMP_TO_LABELS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "component_labels")
assert (os.path.isdir(BUILDINGNET_COMP_TO_LABELS_DIR))


def get_feats(DatasetClass, config):
	""" Export per point output features """

	# Get data loaders
	dataset_dict = load_dataset(DatasetClass, config)

	# Set input and output features
	if dataset_dict["train_split"].dataset.NUM_IN_CHANNEL is not None:
		num_in_channel = dataset_dict["train_split"].dataset.NUM_IN_CHANNEL
	else:
		num_in_channel = 3  # RGB color
	num_labels = dataset_dict["train_split"].dataset.NUM_LABELS

	logging.info('===> Building model')
	NetClass = load_model(config.model)
	model = NetClass(num_in_channel, num_labels, config)
	target_device = get_torch_device(config.is_cuda)
	model = model.to(target_device)
	logging.info('===> Number of trainable parameters: {}: {}'.format(NetClass.__name__, count_parameters(model)))
	logging.info(model)

	# Load weights if specified by the parameter.
	if config.weights.lower() != 'none':
		logging.info('===> Loading weights: ' + config.weights)
		state = torch.load(config.weights)
		model.load_state_dict(state['state_dict'])
	else:
		print("ERROR: No model weights provided")
		exit(-1)

	for split, data_loader in dataset_dict.items():
		feed_forward(model, data_loader, split, config)


def feed_forward(model, data_loader, split, config):
	# Init
	device = get_torch_device(config.is_cuda)
	dataset = data_loader.dataset
	global_timer = Timer()
	logging.info('===> Start feed forward - {}' .format(split))

	global_timer.tic()
	data_iter = data_loader.__iter__()
	max_iter = len(data_loader)

	# Fix batch normalization running mean and std
	model.eval()

	# Clear cache (when run in val mode, cleanup training cache)
	torch.cuda.empty_cache()

	# Create save dir
	save_pred_dir = os.path.join(config.log_dir, split)
	save_pred_point_feat_dir = os.path.join(save_pred_dir, "point_features")
	save_pred_comp_feat_dir = os.path.join(save_pred_dir, "comp_features")
	os.makedirs(save_pred_dir, exist_ok=True)
	os.makedirs(save_pred_point_feat_dir, exist_ok=True)
	os.makedirs(save_pred_comp_feat_dir, exist_ok=True)

	with torch.no_grad():
		for iteration in tqdm(range(max_iter)):
			# Get data
			coords, input, target, transformation = data_iter.next()

			# Construct SparseTensor
			sinput = SparseTensor(input, coords).to(device)

			# Feed forward
			soutput = model(sinput)
			output = soutput.F

			# Inverse distance weighting using 4-nn
			coords = coords[:, 1:].numpy()
			# Undo voxelizer transformation.
			curr_transformation = transformation[0][:16].numpy().reshape(4, 4)
			xyz = np.hstack((coords, np.ones((coords.shape[0], 1))))
			orig_coords = (np.linalg.inv(curr_transformation) @ xyz.T).T
			orig_coords = orig_coords[:, :3]
			out_feat = output.detach().cpu().numpy()
			pred = np.hstack((orig_coords, out_feat))
			pred_tree = spatial.cKDTree(pred[:, :3], leafsize=500)
			fullply_f = dataset.data_root / dataset.data_paths[iteration]
			query_pointcloud = read_plyfile(fullply_f)
			query_xyz = query_pointcloud[:, :3]
			k, pow = 4, 2
			dist, k_nn = pred_tree.query(query_xyz, k=k)
			dist_pow = dist ** pow
			if not np.amin(dist_pow) > 0.0:
				dist_pow = np.maximum(dist_pow, 2.0 * np.finfo(np.float32).eps)
			norm = np.sum(1 / dist_pow, axis=1, keepdims=True)
			norm = np.tile(norm, [1, k])
			weight = (1 / dist_pow) / norm
			assert (np.isclose(np.sum(weight, axis=1, keepdims=True), np.ones_like(norm)).all())
			feats = np.multiply(weight[..., np.newaxis], pred[k_nn, 3:])
			per_point_feat = np.sum(feats, axis=1)
			# Export features per point
			model_name = os.path.basename(dataset.data_paths[iteration])[:-4]
			filename = '%s.pth.tar' % (model_name)
			torch.save(torch.from_numpy(per_point_feat.astype(np.float32)), os.path.join(save_pred_point_feat_dir, filename))
			# Export features per component
			# Get points face index
			with open(os.path.join(BUILDINGNET_PTS_FACEINDEX_DIR, model_name + ".txt"), 'r') as fin_txt:
				point_face_index = fin_txt.readlines()
			point_face_index = np.asarray([int(p.strip()) for p in point_face_index], dtype=int)[:, np.newaxis]
			# Get mesh data
			vertices, faces, _, components, face_area = \
				get_mesh_data(model_name, BUILDINGNET_OBJ_DIR, BUILDINGNET_COMP_TO_LABELS_DIR)
			# Get component features
			_, _, _, _, per_comp_feat = \
				transfer_point_predictions(vertices, faces, components, query_xyz, per_point_feat, point_face_index)
			per_comp_feat = F.normalize(torch.from_numpy(per_comp_feat.astype(np.float32)), dim=0)
			torch.save(per_comp_feat, os.path.join(save_pred_comp_feat_dir, filename))

			if iteration % config.empty_cache_freq == 0:
				# Clear cache
				torch.cuda.empty_cache()

	global_time = global_timer.toc(False)
	logging.info("Finished feed forward. Elapsed time: {:.4f}".format(global_time))


def load_dataset(DatasetClass, config):
	""" Load all data splits """
	train_data_loader = initialize_data_loader(
		DatasetClass,
		config,
		phase=config.train_phase,
		num_workers=config.num_workers,
		shift=False,
		rot_aug=False,
		shuffle=False,
		repeat=False,
		batch_size=1,
		limit_numpoints=False)

	val_data_loader = initialize_data_loader(
		DatasetClass,
		config,
		num_workers=config.num_val_workers,
		phase=config.val_phase,
		shift=False,
		rot_aug=False,
		shuffle=False,
		repeat=False,
		batch_size=1,
		limit_numpoints=False)

	test_data_loader = initialize_data_loader(
		DatasetClass,
		config,
		num_workers=config.num_workers,
		phase=config.test_phase,
		shift=False,
		rot_aug=False,
		shuffle=False,
		repeat=False,
		batch_size=1,
		limit_numpoints=False)

	return dict({"train_split": train_data_loader,
							 "val_split": val_data_loader,
							 "test_split": test_data_loader})
