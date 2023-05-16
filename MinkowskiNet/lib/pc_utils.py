import os
import numpy as np
from plyfile import PlyData, PlyElement
import pandas as pd


def read_plyfile(filepath):
    """
        Read ply file and return it as numpy array.
    """
    with open(filepath, 'rb') as f:
        plydata = PlyData.read(f)

    return pd.DataFrame(plydata.elements[0].data).values


def save_point_cloud_with_normals(points_3d, filename, binary=True, with_label=False, verbose=True):
    """
        Save an RGB+normals point cloud as a PLY file.
    """

    assert points_3d.ndim == 2
    if with_label:
        assert points_3d.shape[1] == 10
        python_types = (float, float, float, float, float, float, float, float, float, int)
        npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'), ('red', 'f4'),
                     ('green', 'f4'), ('blue', 'f4'), ('label', 'u1')]
    else:
        assert points_3d.shape[1] == 9
        python_types = (float, float, float, float, float, float, float, float, float)
        npy_types = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('nx', 'f4'), ('ny', 'f4'), ('nz', 'f4'), ('red', 'f4'),
                     ('green', 'f4'), ('blue', 'f4')]

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
        with open(filename, 'w') as f:
            f.write('ply\n'
                    'format ascii 1.0\n'
                    f'element vertex {points_3d.shape[0]}\n'
                    'property float x\n'
                    'property float y\n'
                    'property float z\n'
                    'property float nx\n'
                    'property float ny\n'
                    'property float nz\n'
                    'property float red\n'
                    'property float green\n'
                    'property float blue\n'
                    'property uchar label\n' if with_label else ''
                    'end_header\n')
        for row_idx in range(points_3d.shape[0]):
            if with_label:
                X, Y, Z, NX, NY, NZ, R, G, B, L = points_3d[row_idx]
                f.write('%f %f %f %f %f %f %f %f %f %d\n' % (X, Y, Z, NX, NY, NZ, R, G, B, L))
            else:
                X, Y, Z, NX, NY, NZ, R, G, B = points_3d[row_idx]
                f.write('%f %f %f %f %f %f %f %f %f\n' % (X, Y, Z, NX, NY, NZ, R, G, B))

    if verbose is True:
        print('Saved point cloud to: %s' % filename)
