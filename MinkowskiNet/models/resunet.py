from models.resnet import ResNetBase, get_norm, NormType
from models.modules.resnet_block import BasicBlock, BasicBlockINBN, Bottleneck

import torch.nn as nn

import MinkowskiEngine as ME
import MinkowskiEngine.MinkowskiOps as me


class MinkUNetBase(ResNetBase):
    BLOCK = None
    PLANES = (64, 128, 256, 512, 256, 128, 128)
    DILATIONS = (1, 1, 1, 1, 1, 1)
    LAYERS = (2, 2, 2, 2, 2, 2)
    INIT_DIM = 64
    NORM_TYPE = NormType.BATCH_NORM

    # To use the model, must call initialize_coords before forward pass.
    # Once data is processed, call clear to reset the model before calling initialize_coords
    def __init__(self, in_channels, out_channels, config, D=3, **kwargs):
        super(MinkUNetBase, self).__init__(in_channels, out_channels, config, D)

    def network_initialization(self, in_channels, out_channels, config, D):
        # Setup net_metadata
        dilations = self.DILATIONS
        bn_momentum = config.bn_momentum

        # Output of the first conv concated to conv6
        self.inplanes = self.INIT_DIM
        self.conv1p1s1 = ME.MinkowskiConvolution(
            in_channels,
            self.inplanes,
            kernel_size=config.conv1_kernel_size,
            dimension=D)

        self.bn1 = get_norm(self.NORM_TYPE, self.PLANES[0], D, bn_momentum=bn_momentum)
        self.block1 = self._make_layer(
            self.BLOCK,
            self.PLANES[0],
            self.LAYERS[0],
            dilation=dilations[0],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)

        self.conv2p1s2 = ME.MinkowskiConvolution(
            self.inplanes,
            self.inplanes,
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bn2 = get_norm(self.NORM_TYPE, self.inplanes, D, bn_momentum=bn_momentum)
        self.block2 = self._make_layer(
            self.BLOCK,
            self.PLANES[1],
            self.LAYERS[1],
            dilation=dilations[1],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)

        self.conv3p2s2 = ME.MinkowskiConvolution(
            self.inplanes,
            self.inplanes,
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bn3 = get_norm(self.NORM_TYPE, self.inplanes, D, bn_momentum=bn_momentum)
        self.block3 = self._make_layer(
            self.BLOCK,
            self.PLANES[2],
            self.LAYERS[2],
            dilation=dilations[2],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)

        self.conv4p4s2 = ME.MinkowskiConvolution(
            self.inplanes,
            self.inplanes,
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bn4 = get_norm(self.NORM_TYPE, self.inplanes, D, bn_momentum=bn_momentum)
        self.block4 = self._make_layer(
            self.BLOCK,
            self.PLANES[3],
            self.LAYERS[3],
            dilation=dilations[3],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)
        self.convtr4p8s2 = ME.MinkowskiConvolutionTranspose(
            self.inplanes,
            self.PLANES[4],
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bntr4 = get_norm(self.NORM_TYPE, self.PLANES[4], D, bn_momentum=bn_momentum)

        self.inplanes = self.PLANES[4] + self.PLANES[2] * self.BLOCK.expansion
        self.block5 = self._make_layer(
            self.BLOCK,
            self.PLANES[4],
            self.LAYERS[4],
            dilation=dilations[4],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)
        self.convtr5p4s2 = ME.MinkowskiConvolutionTranspose(
            self.inplanes,
            self.PLANES[5],
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bntr5 = get_norm(self.NORM_TYPE, self.PLANES[5], D, bn_momentum=bn_momentum)

        self.inplanes = self.PLANES[5] + self.PLANES[1] * self.BLOCK.expansion
        self.block6 = self._make_layer(
            self.BLOCK,
            self.PLANES[5],
            self.LAYERS[5],
            dilation=dilations[5],
            norm_type=self.NORM_TYPE,
            bn_momentum=bn_momentum)
        self.convtr6p2s2 = ME.MinkowskiConvolutionTranspose(
            self.inplanes,
            self.PLANES[6],
            kernel_size=2,
            stride=2,
            dimension=D)
        self.bntr6 = get_norm(self.NORM_TYPE, self.PLANES[6], D, bn_momentum=bn_momentum)
        self.relu = ME.MinkowskiReLU(inplace=True)

        self.final = nn.Sequential(
            ME.MinkowskiConvolution(
                self.PLANES[6] + self.PLANES[0] * self.BLOCK.expansion,
                512,
                kernel_size=1,
                bias=True,
                dimension=D),
            ME.MinkowskiBatchNorm(512), ME.MinkowskiReLU(),
            ME.MinkowskiConvolution(
                512,
                out_channels,
                kernel_size=1,
                bias=True,
                dimension=D))

    def forward(self, x):
        out = self.conv1p1s1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out_b1p1 = self.block1(out)

        out = self.conv2p1s2(out_b1p1)
        out = self.bn2(out)
        out = self.relu(out)

        out_b2p2 = self.block2(out)

        out = self.conv3p2s2(out_b2p2)
        out = self.bn3(out)
        out = self.relu(out)

        out_b3p4 = self.block3(out)

        out = self.conv4p4s2(out_b3p4)
        out = self.bn4(out)
        out = self.relu(out)

        # pixel_dist=8
        out = self.block4(out)

        out = self.convtr4p8s2(out)
        out = self.bntr4(out)
        out = self.relu(out)

        out = me.cat(out, out_b3p4)
        out = self.block5(out)

        out = self.convtr5p4s2(out)
        out = self.bntr5(out)
        out = self.relu(out)

        out = me.cat(out, out_b2p2)
        out = self.block6(out)

        out = self.convtr6p2s2(out)
        out = self.bntr6(out)
        out = self.relu(out)

        out = me.cat(out, out_b1p1)
        return self.final(out)


class ResUNet14(MinkUNetBase):
    BLOCK = BasicBlock
    LAYERS = (1, 1, 1, 1, 1, 1)


class ResUNet18(MinkUNetBase):
    BLOCK = BasicBlock
    LAYERS = (2, 2, 2, 2, 2, 2)


class ResUNet18INBN(ResUNet18):
    NORM_TYPE = NormType.INSTANCE_BATCH_NORM
    BLOCK = BasicBlockINBN


class ResUNet34(MinkUNetBase):
    BLOCK = BasicBlock
    LAYERS = (3, 4, 6, 3, 2, 2)


class ResUNet50(MinkUNetBase):
    BLOCK = Bottleneck
    LAYERS = (3, 4, 6, 3, 2, 2)


class ResUNet101(MinkUNetBase):
    BLOCK = Bottleneck
    LAYERS = (3, 4, 23, 3, 2, 2)


class ResUNet14D(ResUNet14):
    PLANES = (64, 128, 256, 512, 512, 512, 512)


class ResUNet18D(ResUNet18):
    PLANES = (64, 128, 256, 512, 512, 512, 512)


class ResUNet34D(ResUNet34):
    PLANES = (64, 128, 256, 512, 512, 512, 512)


class ResUNet34E(ResUNet34):
    INIT_DIM = 32
    PLANES = (32, 64, 128, 256, 128, 64, 64)


class ResUNet34F(ResUNet34):
    INIT_DIM = 32
    PLANES = (32, 64, 128, 256, 128, 64, 32)
