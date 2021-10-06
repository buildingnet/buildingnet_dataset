import os
import torch
import json
import numpy as np

import GNN.utils.util as util

from torch_geometric.data import Data, InMemoryDataset
from itertools import product
#from torch_geometric.utils import add_self_loops


class BuildnetDataSet(InMemoryDataset):
    def __init__(self, root, typeofdata, typeofedge, nodefeature=None, pretrainedtype=None):
        self.typeofdata = typeofdata
        self.typeofedge = typeofedge
        self.nodefeature = nodefeature
        self.pretrainedtype = pretrainedtype
        self.file_list = []
        self.edge_file_paths = []
        self.node_file_paths = []
        self.label_file_paths = []
        super(BuildnetDataSet, self).__init__(root)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self):
        raw_file = open(os.path.join(self.root, self.typeofdata+".txt"),"r")
        self.file_list = []
        for line in raw_file:
            line = line.strip()
            self.file_list.append(line)
            #self.edge_file_paths.append(os.path.join(self.root, self.typeofedge, line+'_'+self.typeofedge+'.json'))
            #self.label_file_paths.append(os.path.join(self.root, "label", line+'_GNNlabel.txt'))
            #self.node_file_paths.append(os.path.join(self.root, "node", line+'_node.json'))

        raw_file.close()
        return self.file_list

    @property
    def processed_file_names(self):
        # what goes in here?
        print("already processed")
        return [self.typeofdata+'_'+self.typeofedge+'_'+self.nodefeature+'_'+self.pretrainedtype+'_data.pt']

    #def __len__(self):
    #    return len(self.raw_paths)

    def download(self):
        pass

    def process(self):
        data_list = []
        path = None
        name = None

        x_list = [] 
        findex = [i for i in range(len(self.file_list))]
        for index in range(len(self.file_list)):
            fname = self.file_list[index]
            print(fname)
            label_json = json.load(open(os.path.join(self.root, "label",fname+'_label.json'),"r"))
            nodefeature = []
            numnodes = 0
            if self.nodefeature == 'minkow':
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_minkow_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                numnodes = len(pointnet_torch)
               
                for i in range(numnodes):
                   nodefeature.append(pointnet_torch[i].float())
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == "node+minkow":
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_minkow_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
                for i in range(numnodes):
                   feature = torch.cat((torch.tensor(node_json[str(i)]), pointnet_torch[i].float()))
                   nodefeature.append(feature)
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == "node+minkownormal":
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_minkownormal_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
      
                for i in range(numnodes):
                   feature = torch.cat((torch.tensor(node_json[str(i)]), pointnet_torch[i].float()))
                   nodefeature.append(feature)
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == "node+dgcnn":
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_dgcnn_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
                for i in range(numnodes):
                   feature = torch.cat((torch.tensor(node_json[str(i)]), pointnet_torch[i].float()))
                   nodefeature.append(feature)
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == 'pointnet':
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_pointnet_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                numnodes = len(pointnet_torch)
               
                for i in range(numnodes):
                   nodefeature.append(pointnet_torch[i].float())
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == "node+pointnet":
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_pointnet_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
      
                for i in range(numnodes):
                   feature = torch.cat((torch.tensor(node_json[str(i)]), pointnet_torch[i].float()))
                   nodefeature.append(feature)
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == "node+pointnetnormal":
                #pointnet_torch = torch.load(os.path.join(self.root, "pretrained_pointnet_acc_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                pointnet_torch = torch.load(os.path.join(self.root, "pretrained_avgpool_pointnetnormal_features",self.pretrainedtype,fname+'.pth.tar'), map_location='cpu')
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
      
                for i in range(numnodes):
                   feature = torch.cat((torch.tensor(node_json[str(i)]), pointnet_torch[i].float()))
                   nodefeature.append(feature)
                nodefeature = torch.stack(nodefeature) 
            elif self.nodefeature == 'node':
                node_json = json.load(open(os.path.join(self.root, "node", fname+'_node.json'),"r"))
                numnodes = len(node_json)
                for i in range(numnodes):
                   nodefeature.append(node_json[str(i)])
                nodefeature = np.array(nodefeature)
                nodefeature = torch.from_numpy(np.array(nodefeature))

            label = []
            for i in range(numnodes):
                label.append(label_json[str(i)])
            y = torch.Tensor(np.array(label))

            if self.typeofedge == 'node':
                numnodes = torch.tensor([float(numnodes)])
                fileindex = torch.tensor([float(findex[index])])
                data_list.append(Data(x=nodefeature, fileindex=fileindex, numnodes=numnodes , y=y)) 

            else:
                nodepair = []
                attribute = []
                nodepair_dict = {}
                if self.typeofedge != 'all':
                    # Undirected edge / Directed edges
                    nodesvisited = set()
                    if self.typeofedge == 'adjacency+similarity':
                        adjacencyedge_json = json.load(open(os.path.join(self.root, 'adjacency', fname+'_adjacency.json')))
                        similarityedge_json = json.load(open(os.path.join(self.root, 'similarity', fname+'_similarity.json')))

                        # 4 adjacency, 1 similarity
                        nodepair_dict = {x:{y:[0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in adjacencyedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:4] = values
                        for node1,node1_neigh in similarityedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][4:] = [values]

                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                    elif self.typeofedge == 'adjacency+support':
                        adjacencyedge_json = json.load(open(os.path.join(self.root, 'adjacency', fname+'_adjacency.json')))
                        supportedge_json = json.load(open(os.path.join(self.root, 'support', fname+'_support.json')))

                        # 4 adjacency, 4 support
                        nodepair_dict = {x:{y:[0,0,0,0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in adjacencyedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:4] = values
                        for node1,node1_neigh in supportedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][4:] = values

                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                    elif self.typeofedge == 'adjacency+containment':
                        containmentedge_json = json.load(open(os.path.join(self.root, 'containment', fname+'_containment.json')))
                        adjacencyedge_json = json.load(open(os.path.join(self.root, 'adjacency', fname+'_adjacency.json')))

                        # 4 adjacency, 2 containment, 
                        nodepair_dict = {x:{y:[0,0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in adjacencyedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:4] = values
                        for node1,node1_neigh in containmentedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][4:] = values

                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                    elif self.typeofedge == 'support+similarity':
                        supportedge_json = json.load(open(os.path.join(self.root, 'support', fname+'_support.json')))
                        similarityedge_json = json.load(open(os.path.join(self.root, 'similarity', fname+'_similarity.json')))

                        # 4 support, 1 similarity
                        nodepair_dict = {x:{y:[0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in supportedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:4] = values
                        for node1,node1_neigh in similarityedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][4:] = [values]

                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                    elif self.typeofedge == 'containment+similarity':
                        containmentedge_json = json.load(open(os.path.join(self.root, 'containment', fname+'_containment.json')))
                        similarityedge_json = json.load(open(os.path.join(self.root, 'similarity', fname+'_similarity.json')))

                        # 2 containment, 1 similarity
                        nodepair_dict = {x:{y:[0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in containmentedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:2] = values
                        for node1,node1_neigh in similarityedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][2:] = [values]

                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))


                    elif self.typeofedge == 'support+containment':
                        containmentedge_json = json.load(open(os.path.join(self.root, 'containment', fname+'_containment.json')))
                        supportedge_json = json.load(open(os.path.join(self.root, 'support', fname+'_support.json')))

                        # 4 support, 1 containment
                        nodepair_dict = {x:{y:[0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                        node_pair_set = set()
                        nodesvisited = set()
                        for node1,node1_neigh in supportedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][0:4] = values
                        for node1,node1_neigh in containmentedge_json.items():
                            for node2, values in node1_neigh.items():
                                nodepair_dict[int(node1)][int(node2)][4:] = values


                        for node1, node1neigh in nodepair_dict.items():
                            for node2, values in node1neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                    elif self.typeofedge == 'similarity':
                        edge_json = json.load(open(os.path.join(self.root, self.typeofedge, fname+'_'+self.typeofedge+'.json'),'r'))
                        for i in range(numnodes):
                            nodepair.append([int(i), int(i)])
                            attribute.append(np.ones(2))
                            nodesvisited.add((str(i),str(i)))
                        for node1,node1_neigh in edge_json.items():
                            
                            for node2, values in node1_neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if values != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate(([edge_json[node1][node2]],[edge_json[node2][node1]])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))
                    elif self.typeofedge == 'containment':
                        edge_json = json.load(open(os.path.join(self.root, self.typeofedge, fname+'_'+self.typeofedge+'.json'),'r'))
                        for i in range(numnodes):
                            nodepair.append([int(i), int(i)])
                            attribute.append(np.ones(4))
                            nodesvisited.add((str(i),str(i)))
                        for node1,node1_neigh in edge_json.items():
                            for node2, values in node1_neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if sum(values) != 0:
                                    nodepair.append([int(node1), int(node2)])
                                    attribute.append(np.concatenate((edge_json[node1][node2],edge_json[node2][node1])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))
                    elif self.typeofedge == 'adjacency':
                        edge_json = json.load(open(os.path.join(self.root, self.typeofedge, fname+'_'+self.typeofedge+'.json'),'r'))
                        for i in range(numnodes):
                            nodepair.append([int(i), int(i)])
                            attribute.append(np.ones(8))
                            nodesvisited.add((str(i),str(i)))
                        for node1,node1_neigh in edge_json.items():
                            for node2, values in node1_neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if (sum(values[3:]) != 0):
                                    nodepair.append([int(node1), int(node2)])
                                    if (node2 in edge_json and node1 in edge_json[node2]):
                                        attribute.append(np.concatenate((edge_json[node1][node2][3:], edge_json[node2][node1][3:])))
                                    else:
                                        attribute.append(np.concatenate((edge_json[node1][node2][3:], edge_json[node1][node2][3:])))
                    elif self.typeofedge == 'support':
                        edge_json = json.load(open(os.path.join(self.root, self.typeofedge, fname+'_'+self.typeofedge+'.json'),'r'))
                        for i in range(numnodes):
                            nodepair.append([int(i), int(i)])
                            attribute.append(np.ones(8))
                            nodesvisited.add((str(i),str(i)))
                        for node1,node1_neigh in edge_json.items():
                            for node2, values in node1_neigh.items():
                                if (node1,node2) in nodesvisited:
                                    continue
                                if (sum(values[3:]) != 0):
                                    nodepair.append([int(node1), int(node2)])
                                    if (node2 in edge_json and node1 in edge_json[node2]):
                                        attribute.append(np.concatenate((edge_json[node1][node2][3:], edge_json[node2][node1][3:])))
                                    else:
                                        attribute.append(np.concatenate((edge_json[node1][node2][3:], edge_json[node1][node2][3:])))
                                    nodesvisited.add((node1,node2))
                                    nodesvisited.add((node2,node1))

                elif self.typeofedge == 'all':
                    # Undirected edge / Directed edges
                    containmentedge_json = json.load(open(os.path.join(self.root, 'containment', fname+'_containment.json')))
                    adjacencyedge_json = json.load(open(os.path.join(self.root, 'adjacency', fname+'_adjacency.json')))
                    similarityedge_json = json.load(open(os.path.join(self.root, 'similarity', fname+'_similarity.json')))
                    supportedge_json = json.load(open(os.path.join(self.root, 'support', fname+'_support.json')))

                    # 4 adjacency, 1 similarity, 2 containment, 4 support
                    nodepair_dict = {x:{y:[0,0,0,0,0,0,0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}
                    # 1 adjacency, 1 similarity, 2 containment, 4 support
                    #nodepair_dict = {x:{y:[0,0,0,0,0,0,0,0] for y in range(numnodes)} for x in range(numnodes)}

                    node_pair_set = set()
                    nodesvisited = set()
                    for i in range(numnodes):
                        nodepair.append([int(i), int(i)])
                        attribute.append(np.ones(22))
                        nodesvisited.add((str(i),str(i)))

                    for node1,node1_neigh in adjacencyedge_json.items():
                        for node2, values in node1_neigh.items():
                            nodepair_dict[int(node1)][int(node2)][0:4] = values[3:]
                    for node1,node1_neigh in similarityedge_json.items():
                        for node2, values in node1_neigh.items():
                            nodepair_dict[int(node1)][int(node2)][4:5] = [values]
                    for node1,node1_neigh in containmentedge_json.items():
                        for node2, values in node1_neigh.items():
                            nodepair_dict[int(node1)][int(node2)][5:7] = values
                    for node1,node1_neigh in supportedge_json.items():
                        for node2, values in node1_neigh.items():
                            nodepair_dict[int(node1)][int(node2)][7:] = values[3:]

                    for node1, node1neigh in nodepair_dict.items():
                        for node2, values in node1neigh.items():
                            if (node1,node2) in nodesvisited:
                                continue
                            if sum(values) != 0 or sum(nodepair_dict[node2][node1]) != 0:
                                nodepair.append([int(node1), int(node2)])
                                attribute.append(np.concatenate((nodepair_dict[node1][node2], nodepair_dict[node2][node1])))
                                nodesvisited.add((node1,node2))
                                nodesvisited.add((node2,node1))


                nodepair = np.array(nodepair)
                #edgeadjacencymatrix = util.getEdgeAdjacencyMatrix(numnodes,nodepair)
                #edgeadjacencymatrix = np.reshape(edgeadjacencymatrix.flatten(),(-1,1))
                #edgeadjacencymatrix = torch.from_numpy(edgeadjacencymatrix)
                #adjacencymatrix = util.getAdjacencyMatrix(nodefeature.shape[0],nodepair)
                #adjacencymatrix = np.reshape(np.array(adjacencymatrix.toarray()).flatten(), (-1,1))
                #adjacencymatrix = torch.from_numpy(adjacencymatrix)
                nodepair = torch.Tensor(nodepair)#, dtype=torch.long)
                attribute = torch.Tensor(np.array(attribute))#, dtype=torch.float)
                numnodes = torch.tensor([float(numnodes)])
                numedges = torch.tensor([float(len(nodepair))])
                fileindex = torch.tensor([float(findex[index])])
                #data_list.append(Data(fileindex=fileindex, x=nodefeature , nodepair=nodepair, attribute=attribute, adjacencymatrix=adjacencymatrix, numnodes=numnodes, y=y)) 
                data_list.append(Data( x=nodefeature , nodepair=nodepair, attribute=attribute, numedges=numedges , numnodes=numnodes, fileindex=fileindex, y=y)) 

        data, slices = self.collate(data_list)
        torch.save((data, slices), self.processed_paths[0])

    #                toremove = []
    #                for node1, node1neigh in nodepair_dict.items():
    #                    for node2, values in node1neigh.items():
    #                        if sum(values) <= 0:
    #                            toremove.append([node1,node2])
    #
    #                for items in toremove:
    #                    del nodepair_dict[items[0]][items[1]]
    #
    #                nodepair_values = {node1: node2 for node1,node2 in nodepair_dict.items() if node2}

