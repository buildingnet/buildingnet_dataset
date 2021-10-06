import torch
import torch.nn as nn
import torch.nn.parallel
import torch.utils.data
import time
from torch.autograd import Variable
import copy
import numpy as np

from GNN.utils.modelutils import *
from torch.nn import Sequential, Dropout, Linear, ReLU, BatchNorm1d, Parameter
import torch.nn.functional as F

from GNN.Buildnet.layers import MLP, GNN_Edge, GNN_Node
#from GNN.Buildnet.layers import MLP, GNN_Node, GNN_Edge, GNN_EdgeLaplacian

#device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

device =torch.device("cpu")
deviceids = []
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        deviceids.append(i)
    torch.cuda.set_device(0)
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

class BuildnetEnc_Node(nn.Module):
    def __init__(self, modelmeta):
        super(BuildnetEnc_Node, self).__init__()
        self.channels = modelmeta.mlp_channels
        self.normalization = modelmeta.normalization
        self.num_updates = len(self.channels)
        self.GNNModule = []
        self.GNNModule = torch.nn.ModuleList([GNN_Node(self.channels[i].in_channel, self.channels[i].hidden_channel, self.channels[i].out_channel, self.channels[i].num_hidden, self.normalization ) for i in range(self.num_updates)])

    def forward(self, input_features):        
            x = input_features
            for i in range(self.num_updates):
                module = self.GNNModule[i]
                x = module(x)
            return x

class BuildnetDec_Node(nn.Module):
    def __init__(self, modelmeta):
        super(BuildnetDec_Node, self).__init__()
        self.channels = modelmeta.mlp_channels
        self.normalization = modelmeta.normalization
        self.num_updates = len(self.channels)
        self.GNNModule = []
        self.GNNModule = torch.nn.ModuleList([GNN_Node(self.channels[i].in_channel, self.channels[i].hidden_channel, self.channels[i].out_channel, self.channels[i].num_hidden, self.normalization, True) for i in range(self.num_updates)])

    def forward(self, input_features):        
        x = input_features
        for i in range(self.num_updates):
            module = self.GNNModule[i]
            x = module(x)
        return x

class BuildnetEnc_Edge(nn.Module):
    def __init__(self, modelmeta_edge, modelmeta):
        super(BuildnetEnc_Edge, self).__init__()
        self.edge_channels = modelmeta_edge.mlp_channels
        self.edge_normalization = modelmeta_edge.normalization
        self.edge_num_updates = len(self.edge_channels)
        self.GNNModule_edge = torch.nn.ModuleList([GNN_Node(self.edge_channels[i].in_channel, self.edge_channels[i].hidden_channel, self.edge_channels[i].out_channel, self.edge_channels[i].num_hidden, self.edge_normalization, False) for i in range(self.edge_num_updates)])

        self.channels = modelmeta.mlp_channels
        self.normalization = modelmeta.normalization
        self.num_updates = len(self.channels)
        self.GNNModule = torch.nn.ModuleList([GNN_Edge(self.channels[i].in_channel, self.channels[i].hidden_channel, self.channels[i].out_channel, self.channels[i].num_hidden, self.normalization) for i in range(self.num_updates)])

#    def __init__(self, modelmeta):
#        super(BuildnetEnc_Edge, self).__init__()
#
#        self.channels = modelmeta.mlp_channels
#        self.normalization = modelmeta.normalization
#        self.num_updates = len(self.channels)
#        self.GNNModule = torch.nn.ModuleList([GNN_Edge(self.channels[i].in_channel, self.channels[i].hidden_channel, self.channels[i].out_channel, self.channels[i].num_hidden, self.normalization) for i in range(self.num_updates)])

    def forward(self, node_features, nodepair, edge_attribute,  node_neighbour_index, prob_retained=1):        
        for i in range(self.edge_num_updates):
            module = self.GNNModule_edge[i]
            edge_attribute = module(edge_attribute)

        for i in range(self.num_updates):
            nodepair_features = getEdgeInputFeatures(node_features, nodepair, edge_attribute)
            module = self.GNNModule[i]
            node_features, edge_attribute = module([nodepair_features, node_neighbour_index, prob_retained])
        return node_features

class BuildnetDec_Edge(nn.Module):
    def __init__(self, modelmeta):
        super(BuildnetDec_Edge, self).__init__()
        self.channels = modelmeta.mlp_channels
        self.normalization = modelmeta.normalization
        self.num_updates = len(self.channels)
        self.GNNModule = torch.nn.ModuleList([GNN_Node(self.channels[i].in_channel, self.channels[i].hidden_channel, self.channels[i].out_channel, self.channels[i].num_hidden, self.normalization, True) for i in range(self.num_updates)])

    def forward(self, node_features):# input_features):        
        for i in range(self.num_updates):
            module = self.GNNModule[i]
            node_features = module(node_features)
        return node_features
