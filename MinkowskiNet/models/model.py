from MinkowskiEngine import MinkowskiNetwork


class Model(MinkowskiNetwork):
    """
    Base network for all sparse convnet
    """

    def __init__(self, in_channels, out_channels, config, D, **kwargs):
        super(Model, self).__init__(D)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.config = config
