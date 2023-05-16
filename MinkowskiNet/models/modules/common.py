from enum import Enum
import torch.nn as nn

import MinkowskiEngine as ME


class NormType(Enum):
    BATCH_NORM = 0
    INSTANCE_NORM = 1
    INSTANCE_BATCH_NORM = 2


def get_norm(norm_type, n_channels, D, bn_momentum=0.1, eps=1e-5):
    if norm_type == NormType.BATCH_NORM:
        return ME.MinkowskiBatchNorm(n_channels, momentum=bn_momentum)
    elif norm_type == NormType.INSTANCE_NORM:
        return ME.MinkowskiInstanceNorm(n_channels)
    elif norm_type == NormType.INSTANCE_BATCH_NORM:
        return nn.Sequential(
          ME.MinkowskiInstanceNorm(n_channels),
          ME.MinkowskiBatchNorm(n_channels, momentum=bn_momentum))
    else:
        raise ValueError(f'Norm type: {norm_type} not supported')
