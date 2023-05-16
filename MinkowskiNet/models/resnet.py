import torch.nn as nn

import MinkowskiEngine as ME

from models.model import Model
from models.modules.common import NormType, get_norm
from models.modules.resnet_block import BasicBlock, Bottleneck


class ResNetBase(Model):
    BLOCK = None
    LAYERS = ()
    INIT_DIM = 64
    PLANES = (64, 128, 256, 512)
    HAS_LAST_BLOCK = False

    def __init__(self, in_channels, out_channels, config, D=3, **kwargs):
        assert self.BLOCK is not None

        super(ResNetBase, self).__init__(in_channels, out_channels, config, D, **kwargs)

        self.network_initialization(in_channels, out_channels, config, D)
        self.weight_initialization()

    def network_initialization(self, in_channels, out_channels, config, D):

        dilations = config.dilations
        bn_momentum = config.bn_momentum
        self.inplanes = self.INIT_DIM
        self.conv1 = ME.MinkowskiConvolution(
            in_channels,
            self.inplanes,
            kernel_size=config.conv1_kernel_size,
            dimension=D)

        self.bn1 = get_norm(
            NormType.BATCH_NORM,
            self.inplanes,
            D=self.D,
            bn_momentum=bn_momentum)
        self.relu = ME.MinkowskiReLU(inplace=True)
        self.pool = ME.MinkowskiSumPooling(
            kernel_size=2,
            stride=2,
            dilation=1,
            dimension=D)

        self.layer1 = self._make_layer(
            self.BLOCK,
            self.PLANES[0],
            self.LAYERS[0],
            stride=2,
            dilation=dilations[0])
        self.layer2 = self._make_layer(
            self.BLOCK,
            self.PLANES[1],
            self.LAYERS[1],
            stride=2,
            dilation=dilations[1])
        self.layer3 = self._make_layer(
            self.BLOCK,
            self.PLANES[2],
            self.LAYERS[2],
            stride=2,
            dilation=dilations[2])
        self.layer4 = self._make_layer(
            self.BLOCK,
            self.PLANES[3],
            self.LAYERS[3],
            stride=2,
            dilation=dilations[3])

        self.final = ME.MinkowskiConvolution(
            self.PLANES[3] * self.BLOCK.expansion,
            out_channels,
            kernel_size=1,
            bias=True,
            dimension=D)

    def weight_initialization(self):
        for m in self.modules():
            if isinstance(m, ME.MinkowskiBatchNorm):
                nn.init.constant_(m.bn.weight, 1)
                nn.init.constant_(m.bn.bias, 0)

    def _make_layer(self,
                    block,
                    planes,
                    blocks,
                    stride=1,
                    dilation=1,
                    norm_type=NormType.BATCH_NORM,
                    bn_momentum=0.1):
        downsample = None
        if stride != 1 or self.inplanes != planes * block.expansion:
            downsample = nn.Sequential(
                ME.MinkowskiConvolution(
                    self.inplanes,
                    planes * block.expansion,
                    kernel_size=1,
                    stride=1,
                    dilation=1,
                    bias=False,
                    dimension=self.D),
                get_norm(norm_type, planes * block.expansion, D=self.D, bn_momentum=bn_momentum))
        layers = []
        layers.append(
            block(
                self.inplanes,
                planes,
                stride=stride,
                dilation=dilation,
                downsample=downsample,
                D=self.D,
                bn_momentum=bn_momentum))
        self.inplanes = planes * block.expansion
        for i in range(1, blocks):
            layers.append(
                block(
                    self.inplanes,
                    planes,
                    stride=1,
                    dilation=dilation,
                    D=self.D,
                    bn_momentum=bn_momentum))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.pool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.final(x)
        return x


class ResNet14(ResNetBase):
    BLOCK = BasicBlock
    LAYERS = (1, 1, 1, 1)


class ResNet18(ResNetBase):
    BLOCK = BasicBlock
    LAYERS = (2, 2, 2, 2)


class ResNet34(ResNetBase):
    BLOCK = BasicBlock
    LAYERS = (3, 4, 6, 3)


class ResNet50(ResNetBase):
    BLOCK = Bottleneck
    LAYERS = (3, 4, 6, 3)


class ResNet101(ResNetBase):
    BLOCK = Bottleneck
    LAYERS = (3, 4, 23, 3)
