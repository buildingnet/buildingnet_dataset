import os
import numpy as np


LABELS = {0: "undetermined", 1: "wall", 2: "window", 3: "vehicle", 4: "roof", 5: "plant", 6: "door", 7: "tower",
          8: "furniture", 9: "ground", 10: "beam", 11: "stairs", 12: "column", 13: "banister", 14: "floor",
          15: "chimney", 16: "ceiling", 17: "fence", 18: "pool", 19: "corridor", 20: "balcony", 21: "garage",
          22: "dome", 23: "road", 24: "gate", 25: "parapet", 26: "buttress", 27: "dormer", 28: "lighting", 29: "arch",
          30: "awning", 31: "shutters"}


def classification_accuracy(ground, prediction, face_area=None):
    """
        Classification accuracy
    :param ground: N x 1, numpy.ndarray(int)
    :param prediction: N x 1, numpy.ndarray(int)
    :param face_area: N x 1, numpy.ndarray(float)
    :return:
        accuracy: float
    """

    prediction = np.copy(prediction)
    ground = np.copy(ground)
    non_zero_idx = np.squeeze(ground != 0).nonzero()[0]
    ground = ground[non_zero_idx]
    prediction = prediction[non_zero_idx]
    if face_area is not None:
        face_area = np.copy(face_area)
        face_area = face_area[non_zero_idx]
        accuracy = np.dot(face_area.T, ground == prediction)[0] / np.sum(face_area)
        accuracy = accuracy[0]
    else:
        accuracy = np.sum(ground == prediction) / float(len(ground))

    return float(accuracy)


def calc_building_point_iou(ground_truth, prediction, labels):
    """
          Calculate point IOU for buildings
    :param ground_truth: N x 1, numpy.ndarray(int)
    :param prediction: N x 1, numpy.ndarray(int)
    :param labels: tuple: (<label_name> (float))
    :return:
        metrics: dict: {
                          "label_iou": dict{label: iou (float)},
                          "intersection": dict{label: intersection (float)},
                          "union": dict{label: union (float)
                       }
    """

    label_iou, intersection, union = {}, {}, {}
    # Ignore undetermined class
    prediction = np.copy(prediction)
    prediction[ground_truth == 0] = 0

    for i in range(1, len(labels)):
        # Calculate intersection and union for ground truth and predicted labels
        intersection_i = np.sum((ground_truth == i) & (prediction== i))
        union_i = np.sum((ground_truth == i) | (prediction == i))

        # If label i is present either on the gt or the pred set
        if union_i > 0:
            intersection[i] = float(intersection_i)
            union[i] = float(union_i)
            label_iou[i] = intersection[i] / union[i]

    metrics = {"label_iou": label_iou, "intersection": intersection, "union": union}

    return metrics


def calc_building_mesh_iou(ground_truth, prediction, face_area, labels):
    """
        Calculate mesh IOU for buildings
    :param ground_truth: N x 1, numpy.ndarray(int)
    :param prediction: N x 1, numpy.ndarray(int)
    :param face_area: N x 1, numpy.ndarray(float)
    :param labels: tuple: (<label_name> (float))
    :return:
        metrics: dict: {
                          "label_iou": dict{label: iou (float)},
                          "intersection": dict{label: intersection (float)},
                          "union": dict{label: union (float)
                       }
    """

    label_iou, intersection, union = {}, {}, {}
    # Ignore undetermined class
    prediction = np.copy(prediction)
    prediction[ground_truth == 0] = 0

    for i in range(1, len(labels)):
        # Calculate binary intersection and union for ground truth and predicted labels
        intersection_i = ((ground_truth == i) & (prediction == i))
        union_i = ((ground_truth == i) | (prediction == i))

        if np.sum(union_i) > 0:
            intersection[i] = float(np.dot(face_area.T, intersection_i))
            union[i] = float(np.dot(face_area.T, union_i))
            if union[i] > 0.0:
                label_iou[i] = intersection[i] / union[i]
            else:
                label_iou[i] = 0.0

    metrics = {"label_iou": label_iou, "intersection": intersection, "union": union}

    return metrics


def calc_shape_iou(buildings_iou):
    """
        Average label IOU and calculate overall shape IOU
    :param buildings_iou: dict: {
                                    <model_name> : {
                                                      "label_iou": dict{label: iou (float)},
                                                      "intersection": dict{label: intersection (float)},
                                                      "union": dict{label: union (float)
                                                   }
                                }
    :return:
      shape_iou: dict: {
                          "all": avg shape iou,
                          <model_name>: per building shape iou
                       }
    """

    shape_iou = {}

    for building, metrics in buildings_iou.items():
        # Average label iou per shape
        L_s = len(metrics["label_iou"])
        shape_iou[building] = np.sum([v for v in metrics["label_iou"].values()]) / float(L_s)

    # Dataset avg shape iou
    shape_iou['all'] = np.sum([v for v in shape_iou.values()]) / float(len(buildings_iou))

    return shape_iou


def calc_part_iou(buildings_iou, labels):
    """
        Average intersection/union and calculate overall part IOU and most frequent part IOU
    :param buildings_iou: dict: {
                                    <model_name> : {
                                                      "label_iou": dict{label: iou (float)},
                                                      "intersection": dict{label: intersection (float)},
                                                      "union": dict{label: union (float)
                                                   }
                                }
    :param labels: tuple: (<label_name> (float))
    :return:
      part_iou:  dict: {
                          "all": avg part iou,
                          <label_name>: per label part iou
                       }
    """

    intersection = {i: 0.0 for i in range(1, len(labels))}
    union = {i: 0.0 for i in range(1, len(labels))}

    for building, metrics in buildings_iou.items():
        for label in metrics["intersection"].keys():
            # Accumulate intersection and union for each label across all shapes
            intersection[label] += metrics["intersection"][label]
            union[label] += metrics["union"][label]

    # Calculate part IOU for each label
    part_iou = {labels[key]: intersection[key] / union[key] if union[key] > 0. else 0. for key in range(1, len(labels))}
    # Avg part IOU
    part_iou["all"] = np.sum([v for v in part_iou.values()]) / float(len(labels) - 1)

    return part_iou


def read_obj(obj_fn):
    """
        Read obj
    :param obj_fn: str
    :return:
        vertices: N x 3, numpy.ndarray(float)
        faces: M x 3, numpy.ndarray(int)
        components: M x 1, numpy.ndarray(int)
    """

    assert (os.path.isfile(obj_fn))

    # Return variables
    vertices, faces, components = [], [], []

    with open(obj_fn, 'r') as f_obj:
        component = -1
        skip = False
        vertex_offset = 0
        # Read obj geometry
        for line in f_obj:
            line = line.strip().split(' ')
            if line[0] == 'o':
                # object row
                if len(line) == 2:
                    component = int(line[1])
                    skip = False
                else:
                    skip = True
            if skip:
                # Skip degenerate group
                if line[0] == 'v':
                    vertex_offset += 1
                continue
            if line[0] == 'v':
                # Vertex row
                assert (len(line) == 4)
                vertex = [float(line[1]), float(line[2]), float(line[3])]
                vertices.append(vertex)
            if line[0] == 'f':
                # Face row
                assert (len(line) == 4)
                face = [float(line[1].split('/')[0]), float(line[2].split('/')[0]), float(line[3].split('/')[0])]
                face[0] -= vertex_offset
                face[1] -= vertex_offset
                face[2] -= vertex_offset
                faces.append(face)
                components.append(component)

    vertices = np.vstack(vertices)
    faces = np.vstack(faces)
    components = np.vstack(components)

    assert faces.shape[0] == components.shape[0]

    return vertices, faces.astype(np.int32), components.astype(np.int32)


def calculate_face_area(vertices, faces):
    """
        Calculate face area of a triangular mesh
    :param vertices: N x 3, numpy.ndarray(float)
    :param faces: M x 3, numpy.ndarray(int)
    :return:
        face_area: M x 1, numpy.ndarray(float)
    """

    # Get vertices of faces
    A = vertices[faces[:, 0]]
    B = vertices[faces[:, 1]]
    C = vertices[faces[:, 2]]

    # Create face edges
    e1 = B - A
    e2 = C - A

    # Calculate cross product and find length
    cross_prod = np.cross(e1, e2)
    cross_prod_len = np.sqrt(np.sum(cross_prod**2, axis=1))

    # Get face area
    face_area = cross_prod_len / 2.0

    return face_area[:, np.newaxis].astype(np.float32)


def read_point_cloud_ply(ply_fn):
    """
        Read point cloud ply file
    :param ply_fn: str
    :return:
        vertex_properties: dict()
    """

    vertex_properties, n_vertices = {}, 0
    header_end, read_vertex_properties = False, False

    with open(ply_fn, 'r') as fin_ply:
        # Read header
        line = fin_ply.readline().strip()
        assert(line == "ply")
        for line in fin_ply:
            line = line.strip().split(' ')
            if line[0] == 	"end_header":
                # Header end
                header_end = True
                break
            # Read element
            if (line[0] == "element") and (line[1] == "vertex"):
                n_vertices = int(line[2])
                read_vertex_properties = True
            if (line[0] == "element") and (line[1] == "face"):
                n_faces = int(line[2])
                assert n_faces == 0, f"{ply_fn}: faces are not zero {n_faces=}"
                read_vertex_properties = False
            # Read property; only vertex properties are supported
            if (line[0] == "property"):
                if read_vertex_properties:
                    if line[1] == "float":
                        data_type = float
                    elif line[1] == "int":
                        data_type = int
                    else:
                        raise ValueError(f"{ply_fn}: unsupported data type {line[1]}")
                    property_name = line[-1]
                    vertex_properties[property_name] = {"data_type": data_type,
                                                        "data": np.zeros((n_vertices,), dtype=data_type)}
        assert(header_end)

        # Read vertex properties
        assert n_vertices, f"{ply_fn}: model is empty {n_vertices=}"
        vertex_properties_list = list(vertex_properties.keys())
        n_vertex_properties_list = len(vertex_properties_list)
        for v_idx in range(n_vertices):
            line = fin_ply.readline().strip().split(' ')
            assert(len(line) == n_vertex_properties_list)
            for l_idx, v_property in enumerate(vertex_properties_list):
                data_type = vertex_properties[v_property]["data_type"]
                vertex_properties[v_property]["data"][v_idx] = data_type(line[l_idx])

    return vertex_properties
