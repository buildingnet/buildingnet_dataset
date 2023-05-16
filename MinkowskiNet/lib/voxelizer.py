import numpy as np
import MinkowskiEngine as ME
from scipy.linalg import expm, norm


# Rotation matrix along axis with angle theta
def M(axis, theta):
    return expm(np.cross(np.eye(3), axis / norm(axis) * theta))


class Voxelizer:

    def __init__(self,
                 voxel_size=1,
                 ignore_label=255):
        """
        Args:
          voxel_size: side length of a voxel
          ignore_label: label assigned for ignore (not a training label).
        """
        self.voxel_size = voxel_size
        self.ignore_label = ignore_label

    def get_transformation_matrix(self):
        voxelization_matrix = np.eye(4)

        # Transform pointcloud coordinate to voxel coordinate.
        # Scale and translate to the voxel space.
        scale = 1 / self.voxel_size
        np.fill_diagonal(voxelization_matrix[:3, :3], scale)
        # Get final transformation matrix.
        return voxelization_matrix

    def voxelize(self, coords, feats, labels):
        assert coords.shape[1] == 3 and coords.shape[0] == feats.shape[0] and coords.shape[0]

        # Get scale
        M_v = self.get_transformation_matrix()
        # Apply transformations
        rigid_transformation = M_v

        homo_coords = np.hstack((coords, np.ones((coords.shape[0], 1), dtype=coords.dtype)))
        # coords_aug = np.floor(homo_coords @ rigid_transformation.T[:, :3]) -> change this if you are not using TensorField
        coords_aug = homo_coords @ rigid_transformation.T[:, :3]

        return coords_aug, feats, labels, rigid_transformation.flatten()
