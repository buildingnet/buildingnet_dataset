import os
import numpy as np
import json
import sys
from scipy import spatial
from tqdm import tqdm
import torch
import torch.nn.functional as F
from lib.eval_utils import classification_accuracy, calc_building_point_iou, calc_building_mesh_iou, calc_shape_iou, \
    calc_part_iou, LABELS, read_obj, calculate_face_area, read_point_cloud_ply
NUM_POINTS = int(1e5)


def transfer_point_predictions(vertices, faces, components, points, point_feat, point_face_index):
    """
        Transfer point predictions to triangles and components through avg pooling
    :param vertices: N x 3, numpy.ndarray(float)
    :param faces: M x 3, numpy.ndarray(int)
    :param components: M x 1, numpy.ndarray(int)
    :param points: K x 3, numpy.ndarray(float)
    :param point_feat: K x 31, numpy.ndarray(float)
    :param point_face_index: K x 1, numpy.ndarray(int)
    :return:
        face_labels_from_triangle_avg_pool: M x 1, numpy.ndarray(int)
        face_labels_from_comp_avg_pool: M x 1, numpy.ndarray(int)
        face_feat_from_tr_avg_pool: M x 31, numpy.ndarray(float)
        face_feat_from_comp_avg_pool: M x 31, numpy.ndarray(float)
    """

    n_components = len(np.unique(components))
    face_feat_from_tr_avg_pool = np.zeros((faces.shape[0], point_feat.shape[1]))
    face_feat_from_comp_avg_pool = np.zeros((faces.shape[0], point_feat.shape[1]))
    comp_feat_avg_pool = np.zeros((n_components, point_feat.shape[1]))
    face_point_index = {}

    # Find faces that have no corresponding points
    sampled = set(point_face_index.flatten())
    unsampled = list(set(np.arange(len(faces))) - sampled)  # faces with no sample points

    # Compute center for unsampled faces
    v0 = vertices[faces[unsampled, 0]]
    v1 = vertices[faces[unsampled, 1]]
    v2 = vertices[faces[unsampled, 2]]
    face_centers = np.array([[v0[:, 0] + v1[:, 0] + v2[:, 0]],
                             [v0[:, 1] + v1[:, 1] + v2[:, 1]],
                             [v0[:, 2] + v1[:, 2] + v2[:, 2]]]) / 3.0
    face_centers = np.squeeze(face_centers).T

    ## Transfer point predictions to triangles
    # Find nearest point and assign its point feature to each unsampled face
    p_tree = spatial.cKDTree(points)
    _, k_nn_idx = p_tree.query(face_centers)
    for idx, face in enumerate(unsampled):
        face_feat_from_tr_avg_pool[face] = point_feat[k_nn_idx[idx]]
        face_point_index[face] = int(k_nn_idx[idx])

    # Use avg pooling for sampled faces
    for face in sampled:
        mask = np.squeeze(point_face_index == face)
        face_feat_from_tr_avg_pool[face] = np.mean(point_feat[mask], axis=0)
        face_point_index[face] = mask.nonzero()[0].tolist()

    ## Transfer point predictions to components
    for comp_idx in range(comp_feat_avg_pool.shape[0]):
        face_idx = np.squeeze(components == comp_idx).nonzero()[0]
        point_idx = []
        for idx in face_idx:
            try:
                point_idx.extend(face_point_index[int(idx)])
            except:
                point_idx.append(face_point_index[int(idx)])
        comp_feat_avg_pool[comp_idx] = np.mean(point_feat[point_idx], axis=0)
        face_feat_from_comp_avg_pool[face_idx] = comp_feat_avg_pool[comp_idx]

    face_labels_from_tr_avg_pool = np.argmax(face_feat_from_tr_avg_pool, axis=1)[:,
                                   np.newaxis] + 1  # we exclude undetermined (label 0) during training
    face_labels_from_comp_avg_pool = np.argmax(face_feat_from_comp_avg_pool, axis=1)[:, np.newaxis] + 1

    return face_labels_from_tr_avg_pool, face_labels_from_comp_avg_pool, face_feat_from_tr_avg_pool, \
           face_feat_from_comp_avg_pool, comp_feat_avg_pool


def get_split_models(split_fn):
    """
        Read split.txt file and return model names
    :param split_fn:
    :return:
        models_fn: list(str)
    """

    models_fn = []
    with open(split_fn, 'r') as fin:
        for line in fin:
            models_fn.append(line.strip())

    return models_fn


def get_point_cloud_data(model_name, pts_dir, pts_faceindex_dir, out_features, pts_label_dir=None):
    """
        Get point cloud data needed for evaluation
    :param model_name: str
    :param pts_dir: str
    :param pts_faceindex_dir: str
    :param out_features: npz file
    :param pts_label_dir: str
    :return:
        points: N x 3, numpy.ndarray(float)
        point_gt_labels: N x 1, numpy.ndarray(int)
        point_pred_labels: N x 1, numpy.ndarray(int)
        point_pred_feat: N x 31, numpy.ndarray(float)
        point_face_index: N x 1, numpy.ndarray(int)
    """

    # Get points
    vertex_properties = read_point_cloud_ply(os.path.join(pts_dir, model_name + ".ply"))
    points = np.hstack((vertex_properties["x"]["data"][:, np.newaxis], vertex_properties["y"]["data"][:, np.newaxis],
                        vertex_properties["z"]["data"][:, np.newaxis])).astype(np.float32)
    assert points.shape[0] == NUM_POINTS

    point_gt_labels = None
    if pts_label_dir is not None:
        # Get ground truth labels
        with open(os.path.join(pts_label_dir, model_name + "_label.json"), 'r') as f_in:
            labels_json = json.load(f_in)
        point_gt_labels = np.fromiter(labels_json.values(), dtype=int)[:, np.newaxis]
        assert point_gt_labels.shape[0] == NUM_POINTS

    # Get per point features
    point_feat = out_features[model_name + ".npy"]
    assert point_feat.shape[0] == NUM_POINTS
    assert point_feat.shape[1] == (len(LABELS) - 1)

    # Calculate pred label
    point_pred_labels = np.argmax(point_feat, axis=1)[:, np.newaxis] + 1  # we exclude undetermined (label 0) during training

    # Get points face index
    with open(os.path.join(pts_faceindex_dir, model_name + ".txt"), 'r') as f_in:
        point_face_index = f_in.readlines()
    point_face_index = np.asarray([int(p.strip()) for p in point_face_index], dtype=int)[:, np.newaxis]
    assert point_face_index.shape[0] == NUM_POINTS

    return points, point_gt_labels, point_pred_labels, point_feat, point_face_index


def get_mesh_data(model_name, obj_dir, face_labels_dir=None):
    """
        Get mesh data needed for evaluation
    :param model_name: str
    :param obj_dir: str
    :param face_labels_dir: str
    :return:
        vertices: N x 3, numpy.ndarray(float)
        faces: M x 3, numpy.ndarray(int)
        face_labels: M x 1, numpy.ndarray(int)
        components: M x 1, numpy.ndarray(float)
        face_area: M x 1, numpy.ndarray(float)
    """

    # Load obj
    vertices, faces, components = read_obj(obj_fn=os.path.join(obj_dir, model_name + ".obj"))
    faces -= 1

    # Calculate face area
    face_area = calculate_face_area(vertices=vertices, faces=faces)
    assert (face_area.shape[0] == faces.shape[0])

    face_labels = None
    if face_labels_dir is not None:
        # Read face labels
        with open(os.path.join(face_labels_dir, model_name + ".json"), 'r') as f_in:
            labels_json = json.load(f_in)
        face_labels = np.fromiter(labels_json.values(), int)
        face_labels = face_labels[:, np.newaxis]

    return vertices, faces, face_labels, components, face_area


def phases_evaluation(out_feat_fn):
    assert os.path.isfile(out_feat_fn)
    assert out_feat_fn.endswith(".npz")
    out_features = np.load(out_feat_fn)

    # BuildingNet directories
    BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
    assert os.path.isdir(BUILDINGNET_BASE_DIR)
    BUILDINGNET_PTS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "POINT_CLOUDS")
    assert os.path.isdir(BUILDINGNET_PTS_DIR)
    BUILDINGNET_OBJ_DIR = os.path.join(BUILDINGNET_BASE_DIR, "OBJ_MODELS")
    assert os.path.isdir(BUILDINGNET_OBJ_DIR)
    BUILDINGNET_PTS_LABELS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_labels")
    assert os.path.isdir(BUILDINGNET_PTS_LABELS_DIR)
    BUILDINGNET_PTS_FACEINDEX_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_faceindex")
    assert os.path.isdir(BUILDINGNET_PTS_FACEINDEX_DIR)
    BUILDINGNET_FACE_LABELS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "face_labels")
    assert os.path.isdir(BUILDINGNET_FACE_LABELS_DIR)
    BUILDINGNET_VAL_SPLIT = os.path.join(BUILDINGNET_BASE_DIR, "splits", "val_split.txt")
    assert os.path.isfile(BUILDINGNET_VAL_SPLIT)

    # Get model names
    models_fn = get_split_models(split_fn=BUILDINGNET_VAL_SPLIT)

    point_buildings_iou, mesh_buildings_iou_from_tr, mesh_buildings_iou_from_comp = {}, {}, {}
    point_buildings_acc, mesh_buildings_acc_from_tr, mesh_buildings_acc_from_comp = {}, {}, {}

    print("Calculate evaluation metrics for point and mesh phase")
    for model_fn in tqdm(models_fn):
        # Get point cloud data
        points, point_gt_labels, point_pred_labels, point_feat, point_face_index = \
            get_point_cloud_data(model_fn, BUILDINGNET_PTS_DIR, BUILDINGNET_PTS_FACEINDEX_DIR, out_features,
                                 BUILDINGNET_PTS_LABELS_DIR)
        # Get mesh data
        vertices, faces, face_gt_labels, components, face_area = \
            get_mesh_data(model_fn, BUILDINGNET_OBJ_DIR, BUILDINGNET_FACE_LABELS_DIR)
        # Infer face labels from point predictions
        face_pred_labels_from_tr, face_pred_labels_from_comp, face_feat_from_tr, face_feat_from_comp, comp_feat = \
            transfer_point_predictions(vertices, faces, components, points, point_feat, point_face_index)
        # Calculate point building iou
        point_buildings_iou[model_fn] = calc_building_point_iou(point_gt_labels, point_pred_labels, LABELS)
        # Calculate mesh building iou
        mesh_buildings_iou_from_tr[model_fn] = calc_building_mesh_iou(face_gt_labels, face_pred_labels_from_tr,
                                                                     face_area, LABELS)
        mesh_buildings_iou_from_comp[model_fn] = calc_building_mesh_iou(face_gt_labels, face_pred_labels_from_comp,
                                                                       face_area, LABELS)
        # Calculate classification accuracy
        point_buildings_acc[model_fn] = classification_accuracy(point_gt_labels, point_pred_labels)
        mesh_buildings_acc_from_tr[model_fn] = classification_accuracy(face_gt_labels, face_pred_labels_from_tr,
                                                                       face_area)
        mesh_buildings_acc_from_comp[model_fn] = classification_accuracy(face_gt_labels, face_pred_labels_from_comp,
                                                                         face_area)

    # Calculate avg point part and shape IOU
    point_shape_iou = calc_shape_iou(point_buildings_iou)
    point_part_iou = calc_part_iou(point_buildings_iou, LABELS)
    mesh_shape_iou_from_tr = calc_shape_iou(mesh_buildings_iou_from_tr)
    mesh_part_iou_from_tr = calc_part_iou(mesh_buildings_iou_from_tr, LABELS)
    mesh_shape_iou_from_comp = calc_shape_iou(mesh_buildings_iou_from_comp)
    mesh_part_iou_from_comp = calc_part_iou(mesh_buildings_iou_from_comp, LABELS)
    point_acc = np.sum([acc for acc in point_buildings_acc.values()]) / float(len(point_buildings_acc))
    mesh_acc_from_tr = np.sum([acc for acc in mesh_buildings_acc_from_tr.values()]) / \
                       float(len(mesh_buildings_acc_from_tr))
    mesh_acc_from_comp = np.sum([acc for acc in mesh_buildings_acc_from_comp.values()]) / \
                         float(len(mesh_buildings_acc_from_comp))

    # Log results
    str_len = 5
    cls_str = "Classes |" + "|".join([f" {name[:str_len].rjust(str_len)} "
                                      for name in point_part_iou.keys() if name != "all"])
    div_str = "-" * len(cls_str)
    buf = "BuildingNet-Points Phase:\n"
    buf += "-------------------------\n"
    buf += f" Part IoU={point_part_iou['all'] * 100:.1f} %\n"
    buf += f"Shape IoU={point_shape_iou['all'] * 100:.1f} %\n"
    buf += f"Class acc={point_acc * 100:.1f} %\n"
    buf += cls_str + "\n"
    buf += div_str + "\n"
    iou_str = "IoU     |" + "|".join([f" {iou * 100:05.2f} "
                                      for name, iou in point_part_iou.items() if name != "all"])
    buf += iou_str + "\n\n"
    buf += "BuildingNet-Mesh Phase (from triangles):\n"
    buf += "----------------------------------------\n"
    buf += f" Part IoU={mesh_part_iou_from_tr['all'] * 100:.1f} %\n"
    buf += f"Shape IoU={mesh_shape_iou_from_tr['all'] * 100:.1f} %\n"
    buf += f"Class acc={mesh_acc_from_tr * 100:.1f} %\n"
    buf += cls_str + "\n"
    buf += div_str + "\n"
    iou_str = "IoU     |" + "|".join([f" {iou * 100:05.2f} "
                                      for name, iou in mesh_part_iou_from_tr.items() if name != "all"])
    buf += iou_str + "\n\n"
    buf += "BuildingNet-Mesh Phase (from components):\n"
    buf += "-----------------------------------------\n"
    buf += f" Part IoU={mesh_part_iou_from_comp['all'] * 100:.1f} %\n"
    buf += f"Shape IoU={mesh_shape_iou_from_comp['all'] * 100:.1f} %\n"
    buf += f"Class acc={mesh_acc_from_comp * 100:.1f} %\n"
    buf += cls_str + "\n"
    buf += div_str + "\n"
    iou_str = "IoU     |" + "|".join([f" {iou * 100:05.2f} "
                                      for name, iou in mesh_part_iou_from_comp.items() if name != "all"])
    buf += iou_str

    print(buf)
    log_dir = os.path.dirname(out_feat_fn)
    with open(os.path.join(log_dir, "evaluation_results.txt"), 'w') as f_out:
        f_out.write(buf)


def export_predictions(out_feat_fn, split):
    assert os.path.isfile(out_feat_fn)
    assert out_feat_fn.endswith(".npz")
    out_features = np.load(out_feat_fn)

    # BuildingNet directories
    BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
    assert os.path.isdir(BUILDINGNET_BASE_DIR)
    BUILDINGNET_PTS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "POINT_CLOUDS")
    assert os.path.isdir(BUILDINGNET_PTS_DIR)
    BUILDINGNET_OBJ_DIR = os.path.join(BUILDINGNET_BASE_DIR, "OBJ_MODELS")
    assert os.path.isdir(BUILDINGNET_OBJ_DIR)
    BUILDINGNET_PTS_FACEINDEX_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_faceindex")
    assert os.path.isdir(BUILDINGNET_PTS_FACEINDEX_DIR)
    BUILDINGNET_SPLIT = os.path.join(BUILDINGNET_BASE_DIR, "splits", f"{split}_split.txt")
    assert os.path.isfile(BUILDINGNET_SPLIT)

    # Get model names
    models_fn = get_split_models(split_fn=BUILDINGNET_SPLIT)

    print(f"Export predictions for point and mesh phase for {split} split")
    point_predicted_labels, face_predicted_labels_from_tr, face_predicted_labels_from_comp = {}, {}, {}
    for model_fn in tqdm(models_fn):
        # Get point cloud data
        points, _, point_pred_labels, point_feat, point_face_index = \
            get_point_cloud_data(model_fn, BUILDINGNET_PTS_DIR, BUILDINGNET_PTS_FACEINDEX_DIR, out_features)
        # Get mesh data
        vertices, faces, _, components, face_area = get_mesh_data(model_fn, BUILDINGNET_OBJ_DIR)
        # Infer face labels from point predictions
        face_pred_labels_from_tr, face_pred_labels_from_comp, _, _, _ = \
            transfer_point_predictions(vertices, faces, components, points, point_feat, point_face_index)
        model_name = os.path.basename(model_fn).split(".")[0]
        point_predicted_labels[f"{model_name}"] = point_pred_labels.astype(np.uint8)
        face_predicted_labels_from_tr[f"{model_name}"] = face_pred_labels_from_tr.astype(np.uint8)
        face_predicted_labels_from_comp[f"{model_name}"] = face_pred_labels_from_comp.astype(np.uint8)

    # Save predictions
    log_dir = os.path.dirname(out_feat_fn)
    model_name = os.path.basename(out_feat_fn).split("_")[0]
    out_fn = os.path.join(log_dir, f"{model_name}_{split}_pred_point_labels.npz")
    np.savez(out_fn, **point_predicted_labels)
    out_fn = os.path.join(log_dir, f"{model_name}_{split}_pred_face_labels_from_tr.npz")
    np.savez(out_fn, **face_predicted_labels_from_tr)
    out_fn = os.path.join(log_dir, f"{model_name}_{split}_pred_face_labels_from_comp.npz")
    np.savez(out_fn, **face_predicted_labels_from_comp)


def export_features(out_feat_fn, split):
    assert os.path.isfile(out_feat_fn)
    assert out_feat_fn.endswith(".npz")
    out_features = np.load(out_feat_fn)

    # BuildingNet directories
    BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
    assert os.path.isdir(BUILDINGNET_BASE_DIR)
    BUILDINGNET_PTS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "POINT_CLOUDS")
    assert os.path.isdir(BUILDINGNET_PTS_DIR)
    BUILDINGNET_OBJ_DIR = os.path.join(BUILDINGNET_BASE_DIR, "OBJ_MODELS")
    assert os.path.isdir(BUILDINGNET_OBJ_DIR)
    BUILDINGNET_PTS_FACEINDEX_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_faceindex")
    assert os.path.isdir(BUILDINGNET_PTS_FACEINDEX_DIR)
    BUILDINGNET_SPLIT = os.path.join(BUILDINGNET_BASE_DIR, "splits", f"{split}_split.txt")
    assert os.path.isfile(BUILDINGNET_SPLIT)
    split_feat_dir = os.path.join(os.path.dirname(out_feat_fn), f"{split}_comp_feat")
    os.makedirs(split_feat_dir, exist_ok=True)

    # Get model names
    models_fn = get_split_models(split_fn=BUILDINGNET_SPLIT)

    print(f"Export per-component features for {split} split")

    for model_fn in tqdm(models_fn):
        # Get point cloud data
        points, _, _, point_feat, point_face_index = \
            get_point_cloud_data(model_fn, BUILDINGNET_PTS_DIR, BUILDINGNET_PTS_FACEINDEX_DIR, out_features)
        # Get mesh data
        vertices, faces, _, components, face_area = get_mesh_data(model_fn, BUILDINGNET_OBJ_DIR)
        # Get component features
        _, _, _, _, per_comp_feat = \
            transfer_point_predictions(vertices, faces, components, points, point_feat, point_face_index)
        per_comp_feat = F.normalize(torch.from_numpy(per_comp_feat.astype(np.float32)), dim=0)
        # Save features
        model_name = os.path.basename(model_fn).split(".")[0]
        torch.save(per_comp_feat, os.path.join(split_feat_dir, f"{model_name}.pth"))


