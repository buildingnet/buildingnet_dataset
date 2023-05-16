import torch.nn as nn

from models.modules.common import NormType, get_norm

import MinkowskiEngine as ME


class BasicBlockBase(nn.Module):
    expansion = 1
    NORM_TYPE = NormType.BATCH_NORM

    def __init__(self,
                 inplanes,
                 planes,
                 stride=1,
                 dilation=1,
                 downsample=None,
                 bn_momentum=0.1,
                 D=3):
        super(BasicBlockBase, self).__init__()

        self.conv1 = ME.MinkowskiConvolution(
            inplanes,
            planes,
            kernel_size=3,
            stride=stride,
            dilation=dilation,
            dimension=D)
        self.norm1 = get_norm(self.NORM_TYPE, planes, D, bn_momentum=bn_momentum)
        self.conv2 = ME.MinkowskiConvolution(
            planes,
            planes,
            kernel_size=3,
            stride=stride,
            dilation=dilation,
            dimension=D)
        self.norm2 = get_norm(self.NORM_TYPE, planes, D, bn_momentum=bn_momentum)
        self.relu = ME.MinkowskiReLU(inplace=False)
        self.downsample = downsample

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.norm1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.norm2(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class BasicBlock(BasicBlockBase):
    NORM_TYPE = NormType.BATCH_NORM


class BasicBlockIN(BasicBlockBase):
    NORM_TYPE = NormType.INSTANCE_NORM


class BasicBlockINBN(BasicBlockBase):
    NORM_TYPE = NormType.INSTANCE_BATCH_NORM


class BottleneckBase(nn.Module):
    expansion = 1
    bottleneck = 4
    NORM_TYPE = NormType.BATCH_NORM

    def __init__(self,
                 inplanes,
                 planes,
                 stride=1,
                 dilation=1,
                 downsample=None,
                 bn_momentum=0.1,
                 D=3):
        super(BottleneckBase, self).__init__()
        self.conv1 = ME.MinkowskiConvolution(
            inplanes,
            planes // self.bottleneck,
            kernel_size=1,
            dimension=D)
        self.norm1 = get_norm(self.NORM_TYPE, planes // self.bottleneck, D, bn_momentum=bn_momentum)

        self.conv2 = ME.MinkowskiConvolution(
            planes // self.bottleneck,
            planes // self.bottleneck,
            kernel_size=3,
            stride=stride,
            dilation=dilation,
            dimension=D)
        self.norm2 = get_norm(self.NORM_TYPE, planes // self.bottleneck, D, bn_momentum=bn_momentum)

        self.conv3 = ME.MinkowskiConvolution(
            planes // self.bottleneck,
            planes * self.expansion,
            kernel_size=1,
            dimension=D)
        self.norm3 = get_norm(self.NORM_TYPE, planes * self.expansion, D, bn_momentum=bn_momentum)

        self.relu = ME.MinkowskiReLU(inplace=False)
        self.downsample = downsample

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.norm1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.norm2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.norm3(out)

        if self.downsample is not None:
            residual = self.downsample(x)

        out += residual
        out = self.relu(out)

        return out


class Bottleneck(BottleneckBase):
    NORM_TYPE = NormType.BATCH_NORM


class BottleneckIN(BottleneckBase):
    NORM_TYPE = NormType.INSTANCE_NORM


class BottleneckINBN(BottleneckBase):
    NORM_TYPE = NormType.INSTANCE_BATCH_NORM
