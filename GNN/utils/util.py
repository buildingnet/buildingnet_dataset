import torch
import torch.nn as nn
import torch.nn.init as init

import numpy as np
import os
import scipy.sparse as sp
from scipy.linalg import block_diag
import shutil

from torch.optim.lr_scheduler import _LRScheduler
import math
import warnings

def save_checkpoint(state,path,epoch,is_best_loss, is_best_acc):
    filepath = os.path.join(path, "checkpoint.pth.tar")
    torch.save(state, filepath)

    if is_best_loss:
        shutil.copy(filepath, os.path.join(path,str(epoch)+'_checkpoint_best_loss.pth.tar'))
        shutil.copy(filepath, os.path.join(path,'checkpoint_best_loss.pth.tar'))
    if is_best_acc:
        shutil.copy(filepath, os.path.join(path,str(epoch)+'_checkpoint_best_acc.pth.tar'))
        shutil.copy(filepath, os.path.join(path,'checkpoint_best_acc.pth.tar'))
    if epoch % 5 == 0:
        shutil.copy(filepath, os.path.join(path,str(epoch)+'_checkpoint.pth.tar'))


def normalize(matrix):
    rowsum = np.array(matrix.sum(axis=1))
    r_inv = np.power(rowsum, -1).flatten()
    r_inv[np.isinf(r_inv)] = 0
    r_mat_inv = sp.diags(r_inv)
    r_mat = r_mat_inv.dot(matrix)
    return r_mat

def getNormalizedAdjacencyMatrix(numnodes, edges):
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:,0], edges[:,1])),shape=(numnodes, numnodes), dtype=np.float32)
    adj = normalize(adj + sp.eye(numnodes))
    return adj

def getAdjacencyMatrix(numnodes, edges):
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:,0], edges[:,1])),shape=(numnodes, numnodes), dtype=np.float32)
    return adj

def getSelfAdjacencyMatrix(numnodes, edges):
    adj = sp.coo_matrix((np.ones(edges.shape[0]), (edges[:,0], edges[:,1])),shape=(numnodes, numnodes), dtype=np.float32)
    adj = adj + sp.eye(numnodes)
    return adj

def getEdgeAdjacencyMatrix(numnodes, nodepair):
    incidenceMatrix = getundirected_edgeincidenceMatrix(numnodes, nodepair)
    edgeadj = np.matmul(incidenceMatrix.transpose(),incidenceMatrix)
    edgeadj[edgeadj > 1] = 1
    np.fill_diagonal(edgeadj, 0)
    return edgeadj 

def getundirected_edgeincidenceMatrix(numnodes, nodepair):
    incidencem = np.zeros((numnodes, 2*len(nodepair)))
    edgecount = 0
    for i in range(len(nodepair)):
        e = nodepair[i]
        incidencem[int(e[0])][edgecount] = 1
        incidencem[int(e[1])][edgecount] = 1
        incidencem[int(e[0])][edgecount+1] = 1
        incidencem[int(e[1])][edgecount+1] = 1
        edgecount += 2
    return incidencem

def getedgeincidencematrix(numnodes, edges):
    incidencem = np.zeros((numnodes, len(edges)))
    #print(numnodes)
    #print(np.array(edges).shape)
    for i in range(len(edges)):
        e = edges[i]
        #print(e)
        incidencem[int(e[0])][i] = 1
        incidencem[int(e[1])][i] = -1
    return incidencem

def getWeightedLaplacian(incidenceM, weightM):
    A = np.matmul(incidenceM, weightM, dtype=np.float32)
    L = np.matmul(A, np.transpose(incidenceM), dtype=np.float32)
    L = normalize(L)
    return L

def weight_init(m):
    '''
    Usage:
        model = Model()
        model.apply(weight_init)
    '''

    if isinstance(m, nn.Conv1d):
        init.normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.Conv2d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.Conv3d):
        init.xavier_normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)
    elif isinstance(m, nn.ConvTranspose1d):
        init.normal_(m.weight.data)
        if m.bias is not None:
            init.normal_(m.bias.data)


def accuracy(preds, labels):
    indexremoved_labels = labels[labels != -1]
    indexremoved_preds = preds[labels != -1]
    accuracy = (indexremoved_preds == indexremoved_labels.long()).sum()

    return accuracy, indexremoved_labels.numel()

def createSparseBlockAdjacencymatrix(numnodes,validentries, adj_matrix):
    adj_matrices = []
    curr_index = 0
    for i in range(len(numnodes)):
        n = int(numnodes[i])
        if validentries[i]:
            adj = adj_matrix[curr_index:curr_index+(n*n)]
            adj = adj.view(n,n)
            curr_index += n*n
            adj_matrices.append(adj.cpu().numpy())     
        else:
            adj = torch.zeros([n,n])
            adj_matrices.append(adj.cpu().numpy())     

    block_adj_matrix = block_diag(*adj_matrices)
    return adj_matrices,block_adj_matrix


def getEdgeIndexAndAttr( numnodes, numedges, edge_index, edge_attr):
    edge_index_arr = []
    edge_attr_arr = []
    curr_index = 0
    edge_index = edge_index.permute(1,0)
    sumn = 0
    index = 0
    for n in numedges:
        n = int(n)
        curredge = edge_index[curr_index: curr_index+n]
        curredge = curredge - sumn
        edge_index_arr.append(curredge)
        currattr = edge_attr[curr_index: curr_index+n]
        edge_attr_arr.append(currattr)
        curr_index = curr_index + n
        sumn += int(numnodes[index])
        index += 1

    return edge_index_arr, edge_attr_arr

def createAdjacencyList(self, numnodes, adj_matrix):
    index = 0
    curr_index = 0
    buildingadjlist = []
    for n in numnodes:
        n = int(n)
        adj = adj_matrix[curr_index: curr_index+(n*n)]
        adj = np.array(adj.cpu().numpy())
        adj = np.reshape(adj, (n,n))
        curr_index += n*n
        adjlist = {}
        for i in range(n):
            adjlist[i] = []
            for j in range(n):
                if adj[i][j] == 1:
                    adjlist[i].append(j)
        buildingadjlist.append(adjlist)
    return buildingadjlist

def getNodefeatureList(self, numnodes, features):
        curr_index = 0
        nodefeatures = []
        for n in numnodes:
            n = int(n)
            #print(features[curr_index: curr_index+n])
            nodefeatures.append(features[curr_index: curr_index+n])
            curr_index += n
        return nodefeatures

class mlp_channels:
    def __init__(self, in_channel=10, hidden_channel=32, out_channel=32, num_hidden=32, dropout=0.5):
        self.in_channel = in_channel
        self.hidden_channel = hidden_channel
        self.out_channel = out_channel
        self.num_hidden = num_hidden
        if isinstance(dropout, float) or isinstance(dropout, int):
            self.dropout = dropout
        else:
            assert(len(dropout) == self.num_hidden+1)
            self.dropout = dropout


class channel_init:
    def __init__(self, mlp_ch=None, conv_ch=None):
        self.mlp_ch = mlp_ch
        self.conv_ch = conv_ch

class GNNmodelMeta:
    def __init__(self, mlp_channels, normalization='BN'):
        self.normalization = normalization
        self.mlp_channels = mlp_channels
        self.num_updates = len(mlp_channels)
    
class CosineAnnealingCustomWarmRestarts(_LRScheduler):

    def __init__(self, optimizer, T_0, T_mult=1, eta_min=0, last_epoch=-1):
            if T_0 <= 0 or not isinstance(T_0, int):
                raise ValueError("Expected positive integer T_0, but got {}".format(T_0))
            if T_mult < 1 or not isinstance(T_mult, int):
                raise ValueError("Expected integer T_mult >= 1, but got {}".format(T_mult))
            self.T_0 = T_0
            self.T_i = T_0
            self.T_mult = T_mult
            self.eta_min = eta_min

            super(CosineAnnealingCustomWarmRestarts, self).__init__(optimizer, last_epoch)

            self.T_cur = self.last_epoch

    def get_lr(self):
        if not self._get_lr_called_within_step:
            warnings.warn("To get the last learning rate computed by the scheduler, "
                          "please use `get_last_lr()`.", UserWarning)

        return [self.eta_min + (base_lr - self.eta_min) * (1 + math.cos(math.pi * self.T_cur / self.T_i)) / 2
                for base_lr in self.base_lrs]

    def step(self, epoch=None):
        if epoch is None and self.last_epoch < 0:
            epoch = 0

        if epoch is None:
            epoch = self.last_epoch + 1
            self.T_cur = self.T_cur + 1
            if self.T_cur >= self.T_i:
                self.T_cur = self.T_cur - self.T_i
                self.T_i = self.T_i * self.T_mult
        else:
            if epoch < 0:
                raise ValueError("Expected non-negative epoch, but got {}".format(epoch))
            if epoch >= self.T_0:
                if self.T_mult == 1:
                    self.T_cur = epoch % self.T_0
                else:
                    #n = int(math.log((epoch / self.T_0 * (self.T_mult - 1) + 1), self.T_mult))
                    #temp = self.T_0 * (self.T_mult ** n - 1) / (self.T_mult - 1)
                    self.T_cur = epoch
                    self.T_i = self.T_i* self.T_mult # self.T_0 * self.T_mult ** (n)
            else:
                self.T_i = self.T_0
                self.T_cur = epoch
        self.last_epoch = math.floor(epoch)

        class _enable_get_lr_call:

            def __init__(self, o):
                self.o = o

            def __enter__(self):
                self.o._get_lr_called_within_step = True
                return self

            def __exit__(self, type, value, traceback):
                self.o._get_lr_called_within_step = False
                return self

        with _enable_get_lr_call(self):
            for param_group, lr in zip(self.optimizer.param_groups, self.get_lr()):
                param_group['lr'] = lr

        self._last_lr = [group['lr'] for group in self.optimizer.param_groups]



