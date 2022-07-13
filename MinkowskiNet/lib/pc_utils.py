import os
import numpy as np
from numpy.linalg import matrix_rank, inv
from plyfile import PlyData, PlyElement
import pandas as pd


def read_plyfile(filepath):
  """Read ply file and return it as numpy array. Returns None if emtpy."""
  with open(filepath, 'rb') as f:
    plydata = PlyData.read(f)
  if plydata.elements:
    return pd.DataFrame(plydata.elements[0].data).values


def save_point_cloud(points_3d, filename, binary=True, with_label=False, verbose=True):
  """Save an RGB point cloud as a PLY file.

  Args:
    points_3d: Nx6 matrix where points_3d[:, :3] are the XYZ coordinates and points_3d[:, 4:] are
        the RGB values. If Nx3 matrix, save all points with [128, 128, 128] (gray) color.
  """
  assert points_3d.ndim == 2
  if with_label:
    assert points_3d.shape[1] == 7
    python_types = (float, float, float, int, int, int, int)
    npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'),
                 ('blue', 'u1'), ('label', 'u1')]
  else:
    if points_3d.shape[1] == 3:
      gray_concat = np.tile(np.array([128], dtype=np.uint8), (points_3d.shape[0], 3))
      points_3d = np.hstack((points_3d, gray_concat))
    assert points_3d.shape[1] == 6
    python_types = (float, float, float, int, int, int)
    npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'),
                 ('blue', 'u1')]
  if binary is True:
    # Format into NumPy structured array
    vertices = []
    for row_idx in range(points_3d.shape[0]):
      cur_point = points_3d[row_idx]
      vertices.append(tuple(dtype(point) for dtype, point in zip(python_types, cur_point)))
    vertices_array = np.array(vertices, dtype=npy_types)
    el = PlyElement.describe(vertices_array, 'vertex')

    # Write
    PlyData([el]).write(filename)
  else:
    # PlyData([el], text=True).write(filename)
    with open(filename, 'w') as f:
      f.write('ply\n'
              'format ascii 1.0\n'
              'element vertex %d\n'
              'property float x\n'
              'property float y\n'
              'property float z\n'
              'property uchar red\n'
              'property uchar green\n'
              'property uchar blue\n'
              'property uchar alpha\n'
              'end_header\n' % points_3d.shape[0])
      for row_idx in range(points_3d.shape[0]):
        X, Y, Z, R, G, B = points_3d[row_idx]
        f.write('%f %f %f %d %d %d 0\n' % (X, Y, Z, R, G, B))
  if verbose is True:
    print('Saved point cloud to: %s' % filename)


def save_point_cloud_with_normals(points_3d, filename, binary=True, with_label=False, verbose=True):
  """Save an RGB+normals point cloud as a PLY file.

  Args:
    points_3d: Nx9 matrix where points_3d[:, :3] are the XYZ coordinates, points_3d[:, 4:6] are the nx,ny,ny normals
    and points_3d[:, 7:] are the RGB values.
  """
  assert points_3d.ndim == 2
  if with_label:
    assert points_3d.shape[1] == 11
    python_types = (float, float, float, float, float, float, float, float, float, float, int)
    npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'), ('red', 'f4'),
                 ('green', 'f4'), ('blue', 'f4'), ('alpha', 'f4'), ('label', 'u1')]
  else:
    assert points_3d.shape[1] == 10
    python_types = (float, float, float, float, float, float, float, float, float, float)
    npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'), ('red', 'f4'),
                 ('green', 'f4'), ('blue', 'f4'), ('alpha', 'f4')]
  if binary is True:
    # Format into NumPy structured array
    vertices = []
    for row_idx in range(points_3d.shape[0]):
      cur_point = points_3d[row_idx]
      vertices.append(tuple(dtype(point) for dtype, point in zip(python_types, cur_point)))
    vertices_array = np.array(vertices, dtype=npy_types)
    el = PlyElement.describe(vertices_array, 'vertex')

    # Write
    PlyData([el]).write(filename)
  else:
    # PlyData([el], text=True).write(filename)
    with open(filename, 'w') as f:
      f.write('ply\n'
              'format ascii 1.0\n'
              'element vertex %d\n'
              'property float x\n'
              'property float y\n'
              'property float z\n'
              'property float nx\n'
              'property float ny\n'
              'property float nz\n'
              'property float red\n'
              'property float green\n'
              'property float blue\n'
	      'property float alpha\n'
              'property uchar label\n' if with_label else ''
              'end_header\n' % points_3d.shape[0])
      for row_idx in range(points_3d.shape[0]):
        if with_label:
          X, Y, Z, NX, NY, NZ, R, G, B, A, L = points_3d[row_idx]
          f.write('%f %f %f %f %f %f %f %f %f %d\n' % (X, Y, Z, NX, NY, NZ, R, G, B, A, L))
        else:
          X, Y, Z, NX, NY, NZ, R, G, B, A = points_3d[row_idx]
          f.write('%f %f %f %f %f %f %f %f %f\n' % (X, Y, Z, NX, NY, NZ, R, G, B, A))
  if verbose is True:
    print('Saved point cloud to: %s' % filename)


class PlyWriter(object):

  POINTCLOUD_DTYPE = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('red', 'u1'), ('green', 'u1'),
                      ('blue', 'u1')]

  @classmethod
  def read_txt(cls, txtfile):
    # Read txt file and parse its content.
    with open(txtfile) as f:
      pointcloud = [l.split() for l in f]
    # Load point cloud to named numpy array.
    pointcloud = np.array(pointcloud).astype(np.float32)
    assert pointcloud.shape[1] == 6
    xyz = pointcloud[:, :3].astype(np.float32)
    rgb = pointcloud[:, 3:].astype(np.uint8)
    return xyz, rgb

  @staticmethod
  def write_ply(array, filepath):
    ply_el = PlyElement.describe(array, 'vertex')
    target_path, _ = os.path.split(filepath)
    if target_path != '' and not os.path.exists(target_path):
      os.makedirs(target_path)
    PlyData([ply_el]).write(filepath)

  @classmethod
  def write_vertex_only_ply(cls, vertices, filepath):
    # assume that points are N x 3 np array for vertex locations
    color = 255 * np.ones((len(vertices), 3))
    pc_points = np.array([tuple(p) for p in np.concatenate((vertices, color), axis=1)],
                         dtype=cls.POINTCLOUD_DTYPE)
    cls.write_ply(pc_points, filepath)

  @classmethod
  def write_ply_vert_color(cls, vertices, colors, filepath):
    # assume that points are N x 3 np array for vertex locations
    pc_points = np.array([tuple(p) for p in np.concatenate((vertices, colors), axis=1)],
                         dtype=cls.POINTCLOUD_DTYPE)
    cls.write_ply(pc_points, filepath)

  @classmethod
  def concat_label(cls, target, xyz, label):
    subpointcloud = np.concatenate([xyz, label], axis=1)
    subpointcloud = np.array([tuple(l) for l in subpointcloud], dtype=cls.POINTCLOUD_DTYPE)
    return np.concatenate([target, subpointcloud], axis=0)
