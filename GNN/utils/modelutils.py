import numpy as np
import torch
from scipy.linalg import block_diag

def reassignNodePairIndex(numnodes, numedges, nodepair):

    n, e1, e2 = 0, int(numedges[0]),0
    for i in range(len(numnodes)-1):
        n += int(numnodes[i])
        e2 = e1 + int(numedges[i+1])
        nodepair[e1:e2] += n
        e1 = e2

#    n1 = 0
#    for i in range(len(numedges)):
#        n2 = n1+int(numedges[i])
#        print("{} :: min {} :: max {} ".format(i, min(nodepair[n1:n2][:,0]), max(nodepair[n1:n2][:,0])))
#        n1 = n2

    return nodepair
        

def getNodeNeighbourRelation( edge_nodepair, edge_attribute):
    n = int(len(edge_attribute[0])/2)
    e1 = edge_attribute[:,0:n]
    e2 = edge_attribute[:,n:]
    split_edge_attribute = torch.stack([e for pair in zip(e1,e2) for e in pair])

    index = 0
    feature = []
    xi, xj = zip(*edge_nodepair)
    xi = np.array(list(map(int,xi)))
    xj = np.array(list(map(int,xj)))
    allx = np.union1d(xi,xj)
    node_neighbour_index = {x:np.concatenate((np.where(xi == x)[0]*2, np.where(xj == x)[0]*2+1)) for x in allx}
    split_nodepair = [c for pair in zip(np.column_stack((xi,xj)), np.column_stack((xj,xi))) for c in pair]


#    node_neighbour_index = {}
#    split_nodepair = []
#
#    split_edge_attribute = []
#    for i in range(len(edge_attribute)):
#        n = int(len(edge_attribute[i])/2)
#        split_edge_attribute.append(edge_attribute[i][0:n])
#        split_edge_attribute.append(edge_attribute[i][n:])
#
#    if not len(split_edge_attribute):
#        return None,None,None,None
#    split_edge_attribute = torch.stack(split_edge_attribute)
#    for i in range(len(split_edge_attribute)):
#        if not torch.all(split_edge_attribute[i].eq(split_edge_attribute1[i])):
#            print(i)
   

#    split_nodepair = []
#    for i in range(edge_nodepair.size()[0]):
#        xi = int(edge_nodepair[i][0])
#        xj = int(edge_nodepair[i][1])
#        if not xi in node_neighbour_index:
#            node_neighbour_index[xi] = []
#        if not xj in node_neighbour_index:
#            node_neighbour_index[xj] = []
#        node_neighbour_index[xi].append(index)
#        node_neighbour_index[xj].append(index+1)
#        split_nodepair.append([xi,xj])
#        split_nodepair.append([xj,xi])
#        index += 2
#
#    print(node_neigh_index[0],flush=True)
#    print(node_neigh_index[10],flush=True)
#    print(node_neigh_index[100],flush=True)
#    print(split_nodepair[0:10], flush=True)

    return  node_neighbour_index, split_nodepair, split_edge_attribute # feature
    #return node_hasedge_features, node_neighbour_index, split_nodepair, split_edge_attribute # feature


def getEdgeInputFeatures(nodefeatures, nodepair, edge_attr):
    features = []
    xi, xj = zip(*nodepair)
    xi = list(map(int, xi))
    xj = list(map(int, xj))
    features = torch.cat((nodefeatures[xi], nodefeatures[xj], edge_attr),dim=1)
    #features = torch.from_numpy(features)
#    print(features[0], flush=True)
#    features = []
#
#    for i in range(len(nodepair)):
#        nodep = nodepair[i]
#        edgeval = edge_attr[i]
#        xi = int(nodep[0])
#        xj = int(nodep[1])
#        ni = nodefeatures[xi]#.to(dtype=torch.float32)
#        nj = nodefeatures[xj]#.to(dtype=torch.float32)
#        f = torch.cat([ni,nj,edge_attr[i]])
#        features.append(f)
#    features = torch.stack(features)
#    print(features[0], flush=True)
    return features


def getInputFeatureSize(modeltype, edgetype, nodetype, pretrainedtype):
    edgefeature = {'adjacency': 4, 'similarity': 1, 'containment': 2, 'support': 4, 'adjacency+similarity':5, 'adjacency+support':8,\
                   'adjacency+containment':6, 'support+containment':6, 'support+similarity':5, 'containment+similarity':3, 'all':11, 'adjacency_one':1, 'adjacency_two':2, 'adjacency_three':3}
    #pretrainedfeature = {'fc3_max': 33, 'fc3_avg': 33, 'fc1_max': 128, 'fc1_avg': 128}
    pretrainedfeature = {'fc3_avg': 31, 'fc2_avg': 64, 'fc1_avg': 64}
    nodefeature = {'node': 10, 'node+minkow': pretrainedfeature[pretrainedtype]+10, 'minkow':pretrainedfeature[pretrainedtype], 'node+minkownormal':pretrainedfeature[pretrainedtype]+10, 'node+dgcnn':pretrainedfeature[pretrainedtype]+10, 'node+pointnet': pretrainedfeature[pretrainedtype]+10, 'node+pointnetnormal':pretrainedfeature[pretrainedtype]+10,'pointnet':pretrainedfeature[pretrainedtype]}

    inputfeature_enc = 0
    inputfeature_dec = 0
    numnodefeatures = nodefeature[nodetype]
    numedgefeatures = 0
    if modeltype == 'Edge':
        #inputfeature_enc = edgefeature[edgetype] +  nodefeature[nodetype]*2
        inputfeature_enc = nodefeature[nodetype]*3
        numedgefeatures = edgefeature[edgetype]
    elif modeltype == 'Node':
        inputfeature_enc = nodefeature[nodetype]
        numedgefeatures = nodefeature[nodetype]
    inputfeature_dec = nodefeature[nodetype]

    return numedgefeatures, numnodefeatures,inputfeature_enc, inputfeature_dec

