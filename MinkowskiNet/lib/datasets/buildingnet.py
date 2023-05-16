import logging
import os

from lib.dataset import VoxelizationDataset, DatasetPhase, str2datasetphase_type
from lib.utils import read_txt


VALID_CLASS_IDS = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                   28, 29, 30, 31)

NORMALIZED_FREQ = {
    1: 1,
    2: 6.650778396445241,
    3: 44.04740969500708,
    4: 1.7091751066080447,
    5: 13.299036810581534,
    6: 29.097540536010683,
    7: 10.890898807168925,
    8: 70.14972725317553,
    9: 2.774511869415295,
    10: 31.571039725930966,
    11: 46.068691203451394,
    12: 33.95408102643154,
    13: 69.90114167211453,
    14: 7.78802821826952,
    15: 55.69334358970821,
    16: 16.06576537625881,
    17: 16.30538134797283,
    18: 24.322134790753235,
    19: 34.051363167585144,
    20: 33.36482544773351,
    21: 93.9891839027599,
    22: 26.65545563658036,
    23: 16.816255535789427,
    24: 560.4733571701322,
    25: 98.22451239247083,
    26: 57.0236280541644,
    27: 176.5323011824906,
    28: 1106.6558826553344,
    29: 166.53401478073863,
    30: 377.41779845251176,
    31: 521.5646724382996
}


class BuildingNetVoxelizationDataset(VoxelizationDataset):
    # Voxelization arguments
    VOXEL_SIZE = 0.05

    # Augmentation arguments
    SHIFT_PARAMS = (0.01, 0.05)  # ((sigma, clip)
    N_ROTATIONS = 12

    ROTATION_AXIS = 'y'
    NUM_LABELS = 32  # Will be converted to 31 as defined in IGNORE_LABELS.
    IGNORE_LABELS = tuple(set(range(NUM_LABELS)) - set(VALID_CLASS_IDS))
    NORM_FREQ = NORMALIZED_FREQ

    # If trainval.txt does not exist, copy train.txt and add contents from val.txt
    DATA_PATH_FILE = {
        DatasetPhase.Train: 'train.txt',
        DatasetPhase.Val: 'val.txt',
        DatasetPhase.Test: 'test.txt'
    }

    def __init__(self,
                 config,
                 prevoxel_transform=None,
                 rot_aug=False,
                 phase=DatasetPhase.Train):
        self.phase = phase
        if isinstance(phase, str):
            phase = str2datasetphase_type(phase)
        data_root = config.buildingnet_path
        data_paths = read_txt(os.path.join(data_root, self.DATA_PATH_FILE[phase]))
        logging.info('Loading {}: {}'.format(self.__class__.__name__, self.DATA_PATH_FILE[phase]))
        self.input_feat = config.input_feat.lower()
        if self.input_feat == 'rgb' or self.input_feat == 'normals':
            self.NUM_IN_CHANNEL = 3
        elif self.input_feat == 'normals_rgb':
            self.NUM_IN_CHANNEL = 6
        else:
            print("Unknown input features {feat:s}".format(feat=self.input_feat))
            exit(-1)

        super().__init__(
            data_paths,
            data_root=data_root,
            prevoxel_transform=prevoxel_transform,
            ignore_label=config.ignore_label,
            return_transformation=config.return_transformation,
            rot_aug=rot_aug,
            config=config)


class BuildingNetVoxelization0_02Dataset(BuildingNetVoxelizationDataset):
    VOXEL_SIZE = 0.02


class BuildingNetVoxelization0_01Dataset(BuildingNetVoxelizationDataset):
    VOXEL_SIZE = 0.01


class BuildingNetVoxelization0_005Dataset(BuildingNetVoxelizationDataset):
    VOXEL_SIZE = 0.005
