from pathlib import Path
import numpy as np
from lib.pc_utils import read_plyfile, save_point_cloud_with_normals
import json

BUILDINGNET_BASE_PATH = Path('Dataset/BuildingNet')
BUILDINGNET_OUT_PATH = BUILDINGNET_BASE_PATH / 'minkowski_net'
SPLITS = ["train", "test", "val"]
POINTCLOUD_FILE = '.ply'
MAXIMUM_LABEL_ID = 31

split_path = BUILDINGNET_BASE_PATH / 'splits'
for split in SPLITS:
	# Read shapes in split
	split_file = split_path / (split + '_split.txt')
	shape_list = []
	with open(split_file, 'r') as fin:
		for line in fin:
			shape_list.append(line.strip())

	split_out_path = BUILDINGNET_OUT_PATH / split
	split_out_path.mkdir(parents=True, exist_ok=True)

	# Rewrite split list
	with open(BUILDINGNET_OUT_PATH / (split + '.txt'), 'w') as fout_split:
		for shape in shape_list:
			fout_split.write(split + '/' + shape + '.ply\n')

	# Read shape from split
	for ind, shape in enumerate(shape_list):
		print("Preprocess {shape:s} from split {split:s} ({ind:d}/{total:d})"
			  .format(shape=shape, split=split, ind=ind+1, total=len(shape_list)))
		pointcloud_path = BUILDINGNET_BASE_PATH / 'POINT_CLOUDS' / (shape + '.ply')

		# Read point cloud
		pointcloud = read_plyfile(pointcloud_path)

		# Read labels
		labels_path = BUILDINGNET_BASE_PATH / 'point_labels' / (shape + '_label.json')
		with open(labels_path, 'r') as fin_json:
			labels_json = json.load(fin_json)
		labels = np.fromiter(labels_json.values(), dtype=float)
		assert labels.shape[0] == pointcloud.shape[0]
		assert np.amin(labels) >= 0
		assert np.amax(labels) <= MAXIMUM_LABEL_ID

		# Export pointcloud for minkowski
		out_filepath = split_out_path / (shape + '.ply')
		processed = np.hstack((pointcloud, labels[:, np.newaxis]))
		save_point_cloud_with_normals(processed, out_filepath, with_label=True, verbose=False)
