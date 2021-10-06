import torch
import torch.nn as nn
import torch.nn.parallel
import torch.utils.data
from torch.autograd import Variable
import copy
import numpy as np
#import encoding
from torch.nn import Sequential, Dropout, Linear, ReLU, BatchNorm1d, Parameter
import torch.nn.functional as F
import math

device = torch.device("cpu")
deviceids = []
if torch.cuda.is_available():
    for i in range(torch.cuda.device_count()):
        deviceids.append(i)
    torch.cuda.set_device(0)
    device = torch.device("cuda")
else:
    device = torch.device("cpu")


class MLP_GN(nn.Module):
    def __init__(self, channels, num_layers, isDecoder=False, bias = False):
        #super(MLP, self).__init(channels, num_layers, droput_prob=0.5, bias=False)
        super(MLP_GN, self).__init__()
        self.num_layers = num_layers
        self.channels = channels
        groupNorm = []
        if not isDecoder:
            for i in range(1,self.num_layers):
                if self.channels[i] >= 64:
                    groupNorm.append(self.channels[i]//64)
                else:
                    groupNorm.append(1)
        else:
            for i in range(1,self.num_layers-1):
                if self.channels[i] >= 64:
                    groupNorm.append(self.channels[i]//64)
                else:
                    groupNorm.append(1)
            groupNorm.append(1)
        self.mlpmodules = torch.nn.ModuleList([nn.Sequential(nn.Linear(self.channels[i], self.channels[i+1]), nn.LeakyReLU(negative_slope=0.2), nn.GroupNorm(groupNorm[i],self.channels[i+1])) for i in range(self.num_layers-1)])

        self.initialize_weights()

    def initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight.data)
            elif isinstance(m, nn.GroupNorm):
                nn.init.ones_(m.weight.data)

    def forward(self, input_features):
        x = input_features
        for i in range(len(self.mlpmodules)):
            mlpmod = self.mlpmodules[i]
            x = mlpmod(x)
        return x

class MLP(nn.Module):
    def __init__(self, channels, num_layers, dropout_prob=0.5, bias = False):
        #super(MLP, self).__init(channels, num_layers, droput_prob=0.5, bias=False)
        super(MLP, self).__init__()
        self.num_layers = num_layers
        self.channels = channels
        self.mlpmodules = torch.nn.ModuleList([nn.Sequential(nn.Linear(self.channels[i], self.channels[i+1]), nn.LeakyReLU(negative_slope=0.2), nn.BatchNorm1d(self.channels[i+1])) for i in range(self.num_layers-1)])
        self.mlpNoBNmodules = torch.nn.ModuleList([nn.Sequential(nn.Linear(self.channels[i], self.channels[i+1]), nn.LeakyReLU(negative_slope=0.2)) for i in range(self.num_layers-1)])
       

        self.initialize_weights()

    def initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight.data)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.ones_(m.weight.data)

    def forward(self, input_features):
        x = input_features
        #print(" model feature = {}".format(x.size()))
        if len(x) == 1:
            for i in range(len(self.mlpNoBNmodules)):
                mlpmod = self.mlpNoBNmodules[i]
                x = mlpmod(x)
        else:
            for i in range(len(self.mlpmodules)):
                mlpmod = self.mlpmodules[i]
                x = mlpmod(x)
        return x

class GNN_Edge(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_hidden, normalization='BN', isDecoder=False, bias=True):
        super(GNN_Edge, self).__init__()

        self.channels = [in_channels]
        for i in range(num_hidden):
            self.channels.append(hidden_channels)
        self.channels.append(out_channels)
        if normalization == 'BN':
            model = MLP(self.channels, len(self.channels))
        elif normalization == 'GN':
            model = MLP_GN(self.channels, len(self.channels), isDecoder)
        self.mlp = nn.DataParallel(model, device_ids=deviceids)
        self.mlp.to(device)

    def forward(self, inputf):
       input_features, node_neigh_index, prob_retained = inputf[0], inputf[1], inputf[2]
       #print(input_features[0:5])
       f = self.mlp(input_features)
       #print(f)
       #k = [sum(x) for x in f]
       #print(k)
       #node_update = {}
       value = [torch.tensor(node_neigh_index[i]).to(device).long() for i in range(len(node_neigh_index))]
       node_update = torch.cat([((torch.index_select(f,0,value[i])).mean(dim=0)).unsqueeze(0) for i in range(len(node_neigh_index))])


#       node_update = []
#       for key in range(len(node_neigh_index)):
#           value = node_neigh_index[key]
#           t = torch.tensor(value).to(device).long()
#           index = torch.index_select(f,0,t)
#           node_update.append((index.mean(dim=0))*prob_retained)
#
#       node_update = torch.stack(node_update)
#
#       node_update = {}
#       for key,value in node_neigh_index.items():
#           t = torch.tensor(value).to(device).long()
#           index = torch.index_select(f,0,t)
#           node_update[key] = (index.mean(dim=0))*prob_retained

       return node_update, f 

class GNN_Node(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels, num_hidden, normalization='BN', isDecoder=False,bias=True):
        super(GNN_Node, self).__init__()

        self.channels = [in_channels]
        for i in range(num_hidden):
            self.channels.append(hidden_channels)
        self.channels.append(out_channels)
        if normalization == 'BN':
            model = MLP(self.channels, len(self.channels))
        elif normalization == 'GN':
            model = MLP_GN(self.channels, len(self.channels), isDecoder)
        #model = encoding.nn.SyncBatchNorm(model)
        self.mlp = nn.DataParallel(model, device_ids=deviceids)
        self.mlp.to(device)

    def forward(self, input_features):
       output = self.mlp(input_features)
       return output



