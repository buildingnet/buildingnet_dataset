import os
import numpy as np
from lib.pc_utils import read_plyfile, save_point_cloud_with_normals
import json

BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
BUILDINGNET_OUT_DIR = os.path.join(BUILDINGNET_BASE_DIR, "minkowski_net")
os.makedirs(BUILDINGNET_OUT_DIR, exist_ok=True)
SPLITS = ["train", "test", "val"]
POINTCLOUD_FILE = ".ply"
MAXIMUM_LABEL_ID = 31
SPLIT_DIR = os.path.join(BUILDINGNET_BASE_DIR, "splits")

for split in SPLITS:
    # Read shapes in split
    split_file = os.path.join(SPLIT_DIR, f"{split}_split.txt")
    shape_list = []
    with open(split_file, 'r') as fin:
        for line in fin:
            shape_list.append(line.strip())

    split_out_path = os.path.join(BUILDINGNET_OUT_DIR, split)
    os.makedirs(split_out_path, exist_ok=True)

    # Rewrite split list
    split_fn = os.path.join(BUILDINGNET_OUT_DIR, f"{split}.txt")
    with open(split_fn, 'w') as f_out:
        for shape in shape_list:
            f_out.write(f'{split}/{shape}.ply\n')

    # Read shape from split
    for ind, shape in enumerate(shape_list):
        print(f"Preprocess {shape} from split {split} ({ind+1}/{len(shape_list)})")

        # Read point cloud
        pointcloud_fn = os.path.join(BUILDINGNET_BASE_DIR, "POINT_CLOUDS", f"{shape}.ply")
        pointcloud = read_plyfile(pointcloud_fn)

        if split != "test":
            # Read labels
            labels_fn = os.path.join(BUILDINGNET_BASE_DIR, "point_labels", f"{shape}_label.json")
            with open(labels_fn, 'r') as fin_json:
                labels_json = json.load(fin_json)
            labels = np.fromiter(labels_json.values(), dtype=float)
            assert labels.shape[0] == pointcloud.shape[0]
            assert np.amin(labels) >= 0
            assert np.amax(labels) <= MAXIMUM_LABEL_ID
            processed = np.hstack((pointcloud, labels[:, np.newaxis]))
        else:
            processed = pointcloud

        # Export pointcloud for minkowskinet
        out_fn = os.path.join(split_out_path, f"{shape}.ply")
        save_point_cloud_with_normals(processed, out_fn, with_label=True if split != "test" else False, verbose=False)
