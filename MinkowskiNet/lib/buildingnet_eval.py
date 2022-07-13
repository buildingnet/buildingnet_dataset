import os
import numpy as np
import json
import sys
from scipy import spatial
from tqdm import tqdm
from lib.mesh_utils import read_obj, read_ply, calculate_face_area
from lib.utils import classification_accuracy, get_building_point_iou, get_building_mesh_iou, get_shape_iou,\
  get_part_iou

# BuildingNet directories
BUILDINGNET_BASE_DIR = os.path.join("Dataset", "BuildingNet")
assert (os.path.isdir(BUILDINGNET_BASE_DIR))
BUILDINGNET_PTS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "POINT_CLOUDS")
assert (os.path.isdir(BUILDINGNET_PTS_DIR))
BUILDINGNET_OBJ_DIR = os.path.join(BUILDINGNET_BASE_DIR, "OBJ_MODELS")
assert (os.path.isdir(BUILDINGNET_OBJ_DIR))
BUILDINGNET_PTS_LABELS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_labels")
assert (BUILDINGNET_PTS_LABELS_DIR)
BUILDINGNET_PTS_FACEINDEX_DIR = os.path.join(BUILDINGNET_BASE_DIR, "point_faceindex")
assert (os.path.isdir(BUILDINGNET_PTS_FACEINDEX_DIR))
BUILDINGNET_COMP_TO_LABELS_DIR = os.path.join(BUILDINGNET_BASE_DIR, "component_labels")
assert (os.path.isdir(BUILDINGNET_COMP_TO_LABELS_DIR))
BUILDINGNET_TEST_SPLIT = os.path.join(BUILDINGNET_BASE_DIR, "splits", "test_split.txt")
assert (os.path.isfile(BUILDINGNET_TEST_SPLIT))


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

  face_labels_from_tr_avg_pool = np.argmax(face_feat_from_tr_avg_pool, axis=1)[:, np.newaxis] + 1  # we exclude undetermined (label 0) during training
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


def get_point_cloud_data(model_name, pts_dir, pts_label_dir, pts_faceindex_dir, net_results_dir):
  """
    Get point cloud data needed for evaluation
  :param model_name: str
  :param pts_dir: str
  :param pts_label_dir: str
  :param pts_faceindex_dir: str
  :param net_results_dir: str
  :return:
    points: N x 3, numpy.ndarray(float)
    point_gt_labels: N x 1, numpy.ndarray(int)
    point_pred_labels: N x 1, numpy.ndarray(int)
    point_pred_feat: N x 31, numpy.ndarray(float)
    point_face_index: N x 1, numpy.ndarray(int)
  """

  # Get points
  points, _ = read_ply(os.path.join(pts_dir, model_name + ".ply"))

  # Get ground truth labels
  with open(os.path.join(pts_label_dir, model_name + "_label.json"), 'r') as fin_json:
    labels_json = json.load(fin_json)
  point_gt_labels = np.fromiter(labels_json.values(), dtype=int)[:, np.newaxis]
  assert(points.shape[0] == point_gt_labels.shape[0])

  # Get per point features
  point_feat = np.load(os.path.join(net_results_dir, model_fn + ".npy"))
  assert(point_feat.shape[0] == point_gt_labels.shape[0])
  assert(point_feat.shape[1] == (len(labels)-1))

  # Calculate pred label
  point_pred_labels = np.argmax(point_feat, axis=1)[:, np.newaxis] + 1  # we exclude undetermined (label 0) during training
  assert(point_gt_labels.shape == point_pred_labels.shape)

  # Get points face index
  with open(os.path.join(pts_faceindex_dir, model_name + ".txt"), 'r') as fin_txt:
    point_face_index = fin_txt.readlines()
  point_face_index = np.asarray([int(p.strip()) for p in point_face_index], dtype=int)[:, np.newaxis]
  assert(point_face_index.shape == point_gt_labels.shape)

  return points, point_gt_labels, point_pred_labels, point_feat, point_face_index


def get_mesh_data(model_name, obj_dir, comp_to_labels_dir):
  """
    Get mesh data needed for evaluation
  :param model_name: str
  :param obj_dir: str
  :param comp_to_labels_dir: str
  :return:
    vertices: N x 3, numpy.ndarray(float)
    faces: M x 3, numpy.ndarray(int)
    face_labels: M x 1, numpy.ndarray(int)
    components: M x 1, numpy.ndarray(float)
    face_area: M x 1, numpy.ndarray(float)
  """

  # Load obj
  vertices, faces, components = read_obj(obj_fn=os.path.join(obj_dir, model_name + ".obj"))

  # Calculate face area
  faces -= 1
  face_area = calculate_face_area(vertices=vertices, faces=faces)
  assert(face_area.shape[0] == faces.shape[0])

  # Read components to labels
  with open(os.path.join(comp_to_labels_dir, model_name + "_label.json"), 'r') as fin_json:
    labels_json = json.load(fin_json)
  face_labels = np.zeros_like(components)
  for comp, label in labels_json.items():
    face_labels[np.where(components == int(comp))[0]] = label

  return vertices, faces, face_labels, components, face_area


def save_pred_in_json(labels, fn_json):
  """
    Save labels in json format
  :param labels: N x 1, numpy.ndarray(int)
  :param fn_json: str
  :return:
    None
  """

  # Convert numpy to dict
  labels_json = dict(zip(np.arange(labels.shape[0]).astype(str), np.squeeze(labels).tolist()))
  # Export json file
  with open(fn_json, 'w') as fout_json:
    json.dump(labels_json, fout_json)


if __name__ == "__main__":

  # Network results directory
  NET_RESULTS_DIR = sys.argv[1]
  assert (os.path.isdir(NET_RESULTS_DIR))

  # Labels
  labels = {0: "undetermined", 1: "wall", 2: "window", 3: "vehicle", 4: "roof", 5: "plant", 6: "door", 7: "tower",
            8: "furniture", 9: "ground", 10: "beam", 11: "stairs", 12: "column", 13: "banister",
            14: "floor", 15: "chimney", 16: "ceiling", 17: "fence", 18: "pool", 19: "corridor", 20: "balcony",
            21: "garage", 22: "dome", 23: "road", 24: "gate", 25: "parapet", 26: "buttress", 27: "dormer",
            28: "lighting", 29: "arch", 30: "awning", 31: "shutters"}

  # Get model names
  models_fn = get_split_models(split_fn=BUILDINGNET_TEST_SPLIT)

  point_buildings_iou, mesh_buildings_iou_from_tr, mesh_buildings_iou_from_comp = {}, {}, {}
  point_buildings_acc, mesh_buildings_acc_from_tr, mesh_buildings_acc_from_comp = {}, {}, {}

  print("Calculate part and shape IOU for point and mesh tracks")
  for model_fn in tqdm(models_fn):
    # Get point cloud data
    points, point_gt_labels, point_pred_labels, point_feat, point_face_index = \
      get_point_cloud_data(model_fn, BUILDINGNET_PTS_DIR, BUILDINGNET_PTS_LABELS_DIR, BUILDINGNET_PTS_FACEINDEX_DIR,
                           NET_RESULTS_DIR)
    # Get mesh data
    vertices, faces, face_gt_labels, components, face_area = \
      get_mesh_data(model_fn, BUILDINGNET_OBJ_DIR, BUILDINGNET_COMP_TO_LABELS_DIR)
    # Infer face labels from point predictions
    face_pred_labels_from_tr, face_pred_labels_from_comp, face_feat_from_tr, face_feat_from_comp, comp_feat = \
      transfer_point_predictions(vertices, faces, components, points, point_feat, point_face_index)
    # Calculate point building iou
    point_buildings_iou[model_fn] = get_building_point_iou(point_gt_labels, point_pred_labels, labels)
    # Calculate mesh building iou
    mesh_buildings_iou_from_tr[model_fn] = get_building_mesh_iou(face_gt_labels, face_pred_labels_from_tr, face_area,
                                                                 labels)
    mesh_buildings_iou_from_comp[model_fn] = get_building_mesh_iou(face_gt_labels, face_pred_labels_from_comp,
                                                                   face_area, labels)
    # Calculate classification accuracy
    point_buildings_acc[model_fn] = classification_accuracy(point_gt_labels, point_pred_labels)
    mesh_buildings_acc_from_tr[model_fn] = classification_accuracy(face_gt_labels, face_pred_labels_from_tr, face_area)
    mesh_buildings_acc_from_comp[model_fn] = classification_accuracy(face_gt_labels, face_pred_labels_from_comp, face_area)

  # Calculate avg point part and shape IOU
  point_shape_iou = get_shape_iou(point_buildings_iou)
  point_part_iou = get_part_iou(point_buildings_iou, labels)
  mesh_shape_iou_from_tr = get_shape_iou(mesh_buildings_iou_from_tr)
  mesh_part_iou_from_tr = get_part_iou(mesh_buildings_iou_from_tr, labels)
  mesh_shape_iou_from_comp = get_shape_iou(mesh_buildings_iou_from_comp)
  mesh_part_iou_from_comp = get_part_iou(mesh_buildings_iou_from_comp, labels)
  point_acc = np.sum([acc for acc in point_buildings_acc.values()]) / float(len(point_buildings_acc))
  mesh_acc_from_tr = np.sum([acc for acc in mesh_buildings_acc_from_tr.values()]) / float(len(mesh_buildings_acc_from_tr))
  mesh_acc_from_comp = np.sum([acc for acc in mesh_buildings_acc_from_comp.values()]) / float(len(mesh_buildings_acc_from_comp))

  # Log results
  buf = "Point Classification Accuracy: " + str(np.round(point_acc * 100, 2)) + '\n' \
        "Point Shape IoU: " + str(np.round(point_shape_iou['all'] * 100, 2)) + '\n' \
        "Point Part IoU: " + str(np.round(point_part_iou['all'] * 100, 2)) + '\n' \
        "Per label point part IoU: " + ", ".join([label + ": " +
           str(np.round(point_part_iou[label] * 100, 2)) for label in labels.values() if label != "undetermined"]) + '\n' \
        "Average Pooling" + '\n' \
        "---------------" + '\n' \
        "Mesh Classification Accuracy From Triangles: " + str(np.round(mesh_acc_from_tr * 100, 2)) + '\n' \
        "Mesh Shape IoU From Triangles: " + str(np.round(mesh_shape_iou_from_tr['all'] * 100, 2)) + '\n' \
        "Mesh Part IoU From Triangles: " + str(np.round(mesh_part_iou_from_tr['all'] * 100, 2)) + '\n' \
        "Mesh Classification Accuracy From Comp: " + str(np.round(mesh_acc_from_comp * 100, 2)) + '\n' \
        "Mesh Shape IoU From Comp: " + str(np.round(mesh_shape_iou_from_comp['all'] * 100, 2)) + '\n' \
        "Mesh Part IoU From Comp: " + str(np.round(mesh_part_iou_from_comp['all'] * 100, 2)) + '\n' \
        "Per label mesh part IoU from triangles: " + ", ".join([label + ": " +
           str(np.round(mesh_part_iou_from_tr[label][0] * 100, 2)) for label in labels.values() if label != "undetermined"]) + '\n' \
        "Per label mesh part IoU from comp: " + ", ".join([label + ": " +
           str(np.round(mesh_part_iou_from_comp[label][0] * 100, 2)) for label in labels.values() if label != "undetermined"]) + '\n' \

  print(buf)
  with open(os.path.join(NET_RESULTS_DIR, "results_log.txt"), 'w') as fout_txt:
    fout_txt.write(buf)
