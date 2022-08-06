import os
import sys
import json
import math
import numpy as np
import open3d as o3d
import collada
import operator as op
from collada import *
from quasirandompoint import *
import statistics as stat
import scipy
from scipy.spatial.distance import cdist
import argparse
import math

# This script attempts to find the adjacency relationship between two components by 
# finding the average euclidean distance between the points sampled on the faces and
# edges of the components in relation to the total surface area of them

#Default threshold level
threshold = 0.1

class BBox:
    def __init__(self, xmin,ymin, zmin, xmax, ymax, zmax):
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.zmin = zmin
        self.zmax = zmax
        if self.xmax - self.xmin <= 0:
            self.xmax += 1e-4
            self.xmin -= 1e-4
        if self.ymax - self.ymin <= 0:
            self.ymax += 1e-4
            self.ymin -= 1e-4
        if self.zmax - self.zmin <= 0:
            self.zmax += 1e-4
            self.zmin -= 1e-4
        self.diagonal = math.sqrt(pow((self.xmax - self.xmin),2) + pow((self.ymax - self.ymin),2) + pow((self.zmax - self.zmin),2))
 
    def isAdjacent(self, bbox):
        xdist = (min(self.xmax, bbox.xmax) - max(self.xmin, bbox.xmin))
        ydist = (min(self.ymax, bbox.ymax) - max(self.ymin, bbox.ymin))
        zdist = (min(self.zmax, bbox.zmax) - max(self.zmin, bbox.zmin))
        avgdiagonal = (self.diagonal + bbox.diagonal)*1.0/2

        if (((self.xmin <= bbox.xmin and self.xmax >= bbox.xmax) and (self.ymin <= bbox.ymin and self.ymax >= bbox.ymax) and (self.zmin <= bbox.zmin and self.zmax >= bbox.zmax)) \
           or ((self.xmin >= bbox.xmin and self.xmax <= bbox.xmax) and (self.ymin >= bbox.ymin and self.ymax <= bbox.ymax) and (self.zmin >= bbox.zmin and self.zmax <= bbox.zmax))):
            return True

        if max(abs(min(xdist,0)), abs(min(ydist,0)), abs(min(zdist,0))) <= (threshold * avgdiagonal):
            return True
           
        return False

        #intersection_volume = max(0, xdist) * max(0, ydist) * max(0, zdist)


class AdjacencyRelationshipByFacePoints:
    def __init__(self, objfile, bboxfile, facenumpoints, edgenumpoints):
        self.numcomponents = 0
        self.vertices = []
        self.faces = []
        self.surfacearea = []
        self.faceindex = {}

        self.maxfacepoints = int(facenumpoints)
        self.maxedgepoints = int(edgenumpoints)
        self.binpoints = []

        self.bbox = {}
        self.bboxadjacent = {}
        self.facepoints = {}
        self.edgepoints = {}
        self.componentpoints = {}
        self.centroid = {}

        self.testvalidpoints = []
        self.adjacent = {}
        self.compsurfacearea = {}
        #self.fname = filename
        self.objfile = objfile # uniform scale ply file
        self.bboxfile = bboxfile
        self.pcd = []

    # Get the max and min of X, Y ,Z
    def loadBoundingBox(self):
        self.bbox = json.load(open(self.bboxfile, 'r'))
        for key,value in self.bbox.items():
            self.bbox[key] = BBox(value[0], value[1], value[2], value[3], value[4], value[5])

    def pruneAdjacencyRelationByBBox(self):
        for key1,value1 in self.bbox.items():
            for key2,value2 in self.bbox.items():
                if key1 != key2:
                    if not key1 in self.bboxadjacent or (key1 in self.bboxadjacent and key2 not in self.bboxadjacent[key1]):
                        if value1.isAdjacent(value2):
                            if not key1 in self.bboxadjacent:
                                self.bboxadjacent[key1] = []
                            if not key2 in self.bboxadjacent:
                                self.bboxadjacent[key2] = []
                            self.bboxadjacent[key1].append(key2)
                            self.bboxadjacent[key2].append(key1)

    def getAllDistanceByBroadcast(self, p1,p2):
        p1 = np.array(p1)
        p2 = np.array(p2)
       # the shape of p2 is only 100
        n = math.ceil(len(p1)/100)
        m = math.ceil(len(p2)/100)

        # since m = 1
        p2_break = p2[:, np.newaxis, :]

        finaldist = []
        for i in range(n):
            dist = []
            s1 = i*100
            e1 = (i+1)*100
            p1_break = p1[s1:e1]
            if e1 > len(p1):
                p1_break = p1[s1:]
            p1_break = p1_break[np.newaxis, :,:]

  ########### DO NOT DELETE IF YOU WANT TO REUSE FOR HIGHER DIMENSION #########
            #for j in range(m):
            #    s2 = j*100
            #    e2 = (j+1)*100
                #p2_break = p2[s2:e2]
                #if e2 > len(p2):
                #    p2_break = p2[s2:]
                #p2_break = p2_break[:, np.newaxis, :]
                #d = np.sqrt(np.sum((p1_break - p2_break)**2, axis=2))
                ### SHAPE OF D  = valuepoint x keypoint ####
                #if not len(dist):
                #    dist = d 
                #else:
                #    dist = np.vstack((dist, d))
            ### SHAPE OF D  = valuepoint x keypoint ####
            
            dist = np.sqrt(np.sum((p1_break - p2_break)**2, axis=2))
            if not len(finaldist):
                finaldist = dist
            else:
                finaldist = np.hstack((finaldist,dist))
        return finaldist

    def getAdjacencyByBallQuery(self):
        count = 0
        #import time
        for key, value in self.adjacent.items():
            keypoint = self.getAllFacePointsForComponent(key)
            keyedgepoint = self.getAllFaceEdgePointsForComponent(key)
            keypoint = np.concatenate((keypoint, keyedgepoint))
            print(len(keypoint))
            if len(keypoint) > 30000:
               half = len(keypoint)/2
               while half > 30000:
                   half = half/2
               randomindex = np.random.randint(0,len(keypoint), int(half))
               newkeys = keypoint[randomindex]
               keypoint = newkeys
            for v in value:
                if key in self.newadj and v in self.newadj[key]:
                    continue
                totalnum = 0
                valuepoints = self.getAllFacePointsForComponent(v)
                valueedgepoints = self.getAllFaceEdgePointsForComponent(v)
                valuepoints = np.concatenate((valuepoints, valueedgepoints))
                if len(valuepoints) > 30000:
                   half = len(valuepoints)/2
                   while half > 30000:
                       half = half/2
                   randomindex = np.random.randint(0,len(valuepoints), int(half))
                   newvalues = valuepoints[randomindex]
                   valuepoints = newvalues
                
                n = math.ceil(len(valuepoints)/100)
                allvalidindex_01 = 0
                allvalidindex_025 = 0
                allvalidindex_05 = 0
                allvalidindex_1 = 0
                for i in range(n):
                    s1 = i*100
                    e1 = (i+1)*100
                    p1 = valuepoints[s1:e1]
                    if e1 > len(valuepoints):
                        p1 = valuepoints[s1:]
             
                    distances = self.getAllDistanceByBroadcast(keypoint, p1)
                    distances = np.array(distances)

                    # number of value points closer to keypoints
                    # doesnt matter if the same keypoint is mapped to several valuepoints
                    #valid_index_0 = np.where(np.any([x <= 0.0 for x in distances],axis=1)==True)
                    diagonal = threshold*((self.bbox[key].diagonal+ self.bbox[v].diagonal)/2)
                    d_threshold = [0.1*diagonal, 0.25*diagonal, 0.5*diagonal, 1*diagonal]
                    valid_index_01 = np.where(np.any([x <= d_threshold[0] for x in distances],axis=1)==True)
                    valid_index_025 = np.where(np.any([x <= d_threshold[1] for x in distances],axis=1)==True)
                    valid_index_05 = np.where(np.any([x <= d_threshold[2] for x in distances],axis=1)==True)
                    valid_index_1 = np.where(np.any([x <= d_threshold[3] for x in distances],axis=1)==True)
                    #valid_index_0 = valid_index_0[0]
                    valid_index_01 = valid_index_01[0]
                    valid_index_025 = valid_index_025[0]
                    valid_index_05 = valid_index_05[0]
                    valid_index_1 = valid_index_1[0]
#                    p = distances[:,valid_index]
#                    for kk in p:
#                        for dd in kk:
#                            if dd <= 0:
#                                print(dd)

                    #if len(valid_index):
                        #print(distances)
                    #    if not len(self.testvalidpoints):
                    #        self.testvalidpoints = np.array(keypoint[valid_index])
                    #    else:
                    #        self.testvalidpoints = np.concatenate((self.testvalidpoints,keypoint[valid_index]))
                    #if len(valid_index_0):
                    #    allvalidindex_0.append(valid_index_0)
                    if len(valid_index_01):
                        allvalidindex_01 += len(valid_index_01)
                    if len(valid_index_025):
                        allvalidindex_025 += len(valid_index_025)
                    if len(valid_index_05):
                        allvalidindex_05 += len(valid_index_05)
                    if len(valid_index_1):
                        allvalidindex_1 += len(valid_index_1)
                    #if(len(valuepoints) == 17674):
                    #    print("four")


                #percentcoverage = 100.0*len(allvalidindex)/len(keypoint)
                #print(str(key)+"::"+str(v)+"::"+str(percentcoverage))

                if sum([allvalidindex_01, allvalidindex_025, allvalidindex_05, allvalidindex_1]) > 0:
                    if not key in self.newadj:
                        self.newadj[key] = {}
                    self.newadj[key][v] = {}
                    #percentcoverage_0 = 100.0*len(allvalidindex_0)/len(valuepoints)
                    percentcoverage_01 = (allvalidindex_01)/float(len(valuepoints))
                    percentcoverage_025 = (allvalidindex_025)/float(len(valuepoints))
                    percentcoverage_05 = (allvalidindex_05)/float(len(valuepoints))
                    percentcoverage_1 = (allvalidindex_1)/float(len(valuepoints))
                    #if(len(valuepoints) == 17674):
                    #        print("five")
                    #self.newadj[key][v][0] = percentcoverage_0

                    self.newadj[key][v][0.1] =  percentcoverage_01
                    self.newadj[key][v][0.25] =  percentcoverage_025
                    self.newadj[key][v][0.5] =  percentcoverage_05
                    self.newadj[key][v][1.0] =  percentcoverage_1

    def getAdjacencyByEuclideanDistance(self):
        count = 0 
        for comp1, adj1 in self.bboxadjacent.items():
            comp1points = self.componentpoints[int(comp1)]
            comp1points = comp1points.astype('float32')
            for comp2 in adj1:
                if comp1 in self.adjacent: 
                   continue
                totalnum = 0
                comp2points = self.componentpoints[int(comp2)]
                comp2points = comp2points.astype('float32')
                diagonal = threshold*((self.bbox[comp1].diagonal+ self.bbox[comp2].diagonal)/2)
                d_threshold = [0.01*diagonal, 0.025*diagonal, 0.05*diagonal, 0.1*diagonal, 0.25*diagonal, 0.5*diagonal, 1*diagonal]

                valid_comp1_index = {i:0 for i in range(len(d_threshold))}
                valid_comp2_index = {i:0 for i in range(len(d_threshold))}

                splits = math.ceil(len(comp1points)/10000)
                for index in range(1,splits+1):
                    distances = cdist(comp1points[(index-1)*10000:index*10000], comp2points)
                    for i in range(len(d_threshold)):
                        valid_comp1_index[i] += len((np.where(np.any([x <= d_threshold[i] for x in distances],axis=1)==True))[0])

                splits = math.ceil(len(comp2points)/10000)
                for index in range(1,splits+1):
                    distances = cdist(comp2points[(index-1)*10000:index*10000], comp1points)
                    for i in range(len(d_threshold)):
                        valid_comp2_index[i] += len((np.where(np.any([x <= d_threshold[i] for x in distances],axis=1)==True))[0])


                if sum(valid_comp1_index.values()):
                    if comp1 == "0" and comp2 == "4":
                        print(valid_comp1_index)
                    if not comp1 in self.adjacent:
                        self.adjacent[comp1] = {}
                    if not comp2 in self.adjacent[comp1]:
                        self.adjacent[comp1][comp2] = []
                    for i in range(len(d_threshold)):
                        (self.adjacent[comp1][comp2]).append(valid_comp1_index[i]*1.0/len(comp1points))

                if sum(valid_comp2_index.values()):
                    if not comp2 in self.adjacent:
                        self.adjacent[comp2] = {}
                    if not comp1 in self.adjacent[comp1]:
                        self.adjacent[comp2][comp1] = []
                    for i in range(len(d_threshold)):
                        (self.adjacent[comp2][comp1]).append(valid_comp2_index[i]*1.0/len(comp2points))

    def getAllFacePointsForComponent(self, compid):
        faceindex = self.faceindex[compid]
        allfacepoints = np.empty((0,3),float)
        for f in range(faceindex[0], faceindex[1]+1):
            allfacepoints = np.vstack((allfacepoints,np.array(self.facepoints[f])))
        return allfacepoints

    def getAllFaceEdgePointsForComponent(self, compid):
        faceindex = self.faceindex[compid]
        allfaceedgepoints = np.empty((0,3),float)
        visitededges = []
        edgepoints = []
        
        for f in range(faceindex[0], faceindex[1]+1):
            face = self.faces[f]
            v0 = face[0] # self.vertices[face[0]]
            v1 = face[1] #self.vertices[face[1]]
            v2 = face[2] #self.vertices[face[2]]
            if not v0 in edgepoints:
                edgepoints.append(v0)
            if not v1 in edgepoints:
                edgepoints.append(v1)
            if not v2 in edgepoints:
                edgepoints.append(v2)
            if not (v0,v1) in visitededges:
                allfaceedgepoints = np.vstack((allfaceedgepoints,np.array(self.edgepoints[(v0,v1)])))
                visitededges.append((v0,v1))
                visitededges.append((v1,v0))
            if not (v0,v2) in visitededges:
                allfaceedgepoints = np.vstack((allfaceedgepoints,np.array(self.edgepoints[(v0,v2)])))
                visitededges.append((v0,v2))
                visitededges.append((v2,v0))
            if not (v2,v1) in visitededges:
                allfaceedgepoints = np.vstack((allfaceedgepoints,np.array(self.edgepoints[(v1,v2)])))
                visitededges.append((v1,v2))
                visitededges.append((v2,v1))

        vertexpoints = []
        for v in edgepoints:
            vertexpoints.append(self.vertices[v])
        allfaceedgepoints = np.vstack((allfaceedgepoints, np.array(vertexpoints)))
        return allfaceedgepoints

    def gatherAllPointsForAComponent(self):
        for key in self.faceindex.keys():
            keypoint = self.getAllFacePointsForComponent(key)
            keyedgepoint = self.getAllFaceEdgePointsForComponent(key)
            self.componentpoints[key] = np.vstack((keypoint, keyedgepoint))
            self.centroid[key] = (np.mean(self.componentpoints[key],axis=0)).tolist()

            
    def getSurfaceArea(self, v1, v2, v3):
        a = v2 - v1
        b = v3 - v1
        cross = np.cross(a,b)
        L = np.linalg.norm(cross)
        return L/2.0
        
    def getPointsOnfaces(self):
        nonzerosurfacearea = []
        nonzeroedge = {}
        edgelength = []
        minedge = math.inf
        maxedge = -math.inf
        self.surfacearea = []
        for face in self.faces:
            vertices = []
            vertices.append(self.vertices[face[0]])
            vertices.append(self.vertices[face[1]])
            vertices.append(self.vertices[face[2]])
            v0_v1 = (face[0], face[1]) in nonzeroedge 
            v1_v0 = (face[1], face[0]) in nonzeroedge
            v0_v2 = (face[0], face[2]) in nonzeroedge
            v2_v0 = (face[2], face[0]) in nonzeroedge
            v1_v2 = (face[1], face[2]) in nonzeroedge 
            v2_v1 = (face[2], face[1]) in nonzeroedge  
            
            if not (v0_v1 or v1_v0):
                edge1 = np.linalg.norm(vertices[0] - vertices[1])
                nonzeroedge[(face[0],face[1])] = edge1
                nonzeroedge[(face[1],face[0])] = edge1

            if not (v0_v2 or v2_v0):
                edge2 = np.linalg.norm(vertices[0] - vertices[2])
                nonzeroedge[(face[0],face[2])] = edge2
                nonzeroedge[(face[2],face[0])] = edge2

            if not (v1_v2 or v2_v1):
                edge3 = np.linalg.norm(vertices[1] - vertices[2])
                nonzeroedge[(face[1],face[2])] = edge3
                nonzeroedge[(face[2],face[1])] = edge3
            
            s = self.getSurfaceArea(vertices[0], vertices[1], vertices[2])
            self.surfacearea.append(s)
            if s > 0:
                nonzerosurfacearea.append(s)


        medianedge = stat.median(list(nonzeroedge.values()))
        minedge = np.amin(list(nonzeroedge.values()))
        maxedge = np.amax(list(nonzeroedge.values()))
        edgebindiff = ((maxedge - minedge)/self.maxedgepoints)

        mediansurfacearea = stat.median(list(nonzerosurfacearea))
        minsurfacearea = np.amin(list(nonzerosurfacearea))
        maxsurfacearea = np.amax(list(nonzerosurfacearea))

        self.binpoints = []
        for s in self.surfacearea:
            if s > 0:
                diff = s - mediansurfacearea
                if diff <= 0:
                    self.binpoints.append(math.ceil(s*self.maxfacepoints/mediansurfacearea))
                else:
                     self.binpoints.append(100+math.ceil(s*self.maxfacepoints/maxsurfacearea))
            else:
                self.binpoints.append(0)

        self.edgepoints = {}
        for i in range(len(self.faces)):
            face = self.faces[i]
            vertices = []
            vertices.append(self.vertices[face[0]])
            vertices.append(self.vertices[face[1]])
            vertices.append(self.vertices[face[2]])
            v0_v1 = (face[0], face[1]) in self.edgepoints
            v1_v0 = (face[1], face[0]) in self.edgepoints
            v0_v2 = (face[0], face[2]) in self.edgepoints
            v2_v0 = (face[2], face[0]) in self.edgepoints
            v1_v2 = (face[1], face[2]) in self.edgepoints
            v2_v1 = (face[2], face[1]) in self.edgepoints
             

            if not (v0_v1 or v1_v0):
                dist = nonzeroedge[(face[0], face[1])]
                points = self.getPointsForOneEdge(vertices[0], vertices[1],dist, medianedge, maxedge)
                self.edgepoints[(face[0], face[1])] = points
                self.edgepoints[(face[1], face[0])] = points

            if not (v0_v2 or v2_v0):
                dist = nonzeroedge[(face[0], face[2])]
                points = self.getPointsForOneEdge(vertices[0], vertices[2],dist, medianedge, maxedge)
                self.edgepoints[(face[0], face[2])] = points
                self.edgepoints[(face[2], face[0])] = points

            if not (v1_v2 or v2_v1):
                dist = nonzeroedge[(face[1], face[2])]
                points = self.getPointsForOneEdge(vertices[1], vertices[2],dist, medianedge, maxedge)
                self.edgepoints[(face[1], face[2])] = points
                self.edgepoints[(face[2], face[1])] = points
            
            points = getQuasiRandomPoint(vertices[0], vertices[1], vertices[2], self.binpoints[i]+1, 0.5)
            self.facepoints[i] = points

    def getPointsForOneEdge(self,v1,v2,dist, medianedge,maxedge):
        diff = dist - medianedge
        if diff <= 0:
            numpoints = math.ceil(dist*self.maxedgepoints/medianedge)
        else:
            numpoints = 10+math.ceil(dist*self.maxedgepoints/maxedge)
        
        beta = 1.0/(numpoints+2)
        points = getEdgePoints(v2,v1,beta,numpoints+2)
        return points

    def getMetaData(self):
        fread = open(self.objfile, 'r')
        count = -1
        fstart = fend = None
        index = -1

        for line in fread:
            line = line.strip()

            if line.startswith("o "):
                fend = count

                if (not fstart is None) and (not fend is None):
                    self.faceindex[index] = [fstart, fend]
                    fstart = None
                    fend = None
                data = line.split()
                if len(data) == 2:
                    index = int(data[1])

            elif line.startswith("v "):
                data = line.split()[1:]
                data = list(map(float, data))
                data = np.array(data)
                #print(data)
                self.vertices.append(data)

            elif line.startswith("f "):
                count +=1
                if fstart is None:
                    fstart = count
                data = line.split()[1:]
                self.faces.append([int(data[0].split('/')[0])-1, int(data[1].split('/')[0])-1, int(data[2].split('/')[0])-1])

        self.faceindex[index] = [fstart,count]

        self.vertices = np.array(self.vertices)
        minv = np.amin(self.vertices, axis=0)
        maxv = np.amax(self.vertices, axis=0)
        m = np.amax(maxv - minv)
        centroid = (minv + maxv)/2


        for i in range(len(self.vertices)):
            self.vertices[i][0] -= centroid[0]
            self.vertices[i][1] -= centroid[1]
            self.vertices[i][2] -= centroid[2]

            self.vertices[i][0] /= m
            self.vertices[i][1] /= m
            self.vertices[i][2] /= m 
       
    def testpoints(self, inputpoints, isdict=False):
        allpoints = []
        #for k, points in self.facepoints.items():
        if isdict:
            for k, points in inputpoints.items():
                for p in points:
                    allpoints.append(p)
        else:
            for p in inputpoints:
                allpoints.append(p)

        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(allpoints)
        o3d.visualization.draw_geometries([self.pcd])
        #o3d.io.write_point_cloud('test.pcd',pcd)

def writeJsonAdjacency(fname, adjlist, outputfolder):
    with open(os.path.join(outputfolder, fname+"_adjacency.json"),"w") as fwrite:
        json.dump(adjlist, fwrite)


def adjacencyOfAFile(fname, facepoints, edgepoints,objfolder, bboxfolder, outputfolder):
    print(fname)
    objfile = os.path.join(objfolder, fname+".obj")
    bboxfile = os.path.join(bboxfolder, fname+"_bbox.json")
    
    # Uncomment these lines if you do not need to re-compute the files

    #if os.path.exits(os.path.join(outputfolder, fname+"_adjacency.json")):
    #    print(fname, " already present")
    #    return

    #if not os.path.exists(bboxfile):
    #    print("bbox not yet computed")
    #    return

    adj = AdjacencyRelationshipByFacePoints(objfile, bboxfile,facepoints, edgepoints)
    adj.getMetaData()  # for an OBJ file meta data = vertices, faces, faceindex

    # By the internal surface area and edge length the number of 
    # points on the face is calculated and points are generated
    # by quasirandompoint generator for each face
    adj.getPointsOnfaces()

    # Load the world oriented Bounding Box for each component from
    # precomputed json file
    # Ideally OBB is preferred
    adj.loadBoundingBox()
    
    #Uncomment this line to visualize the points generated per face
    #adj.testpoints(adj.facepoints, True)

    # Gather all the face points computed by getPointsOnFaces
    # for a component / all components
    adj.gatherAllPointsForAComponent()

    # To reduce the number of adjacency relationship calculation( n-n
    # computation), prune the number of adjacent components for a component
    # using the Bounding box adjacency relationship
    adj.pruneAdjacencyRelationByBBox()

    # Once the number of adajcent components has been established
    # calculate
    # diagonal = threshold * (diagonal_A + diagonal_b)/2
    # dt = [0.01*diagonal, 0.025*diagonal, 0.05*diagonal, 0.1*diagonal, 0.25*diagonal, 0.5*diagonal, 1*diagonal]
    #  n_CA =  number of component_A_points euclidean distance to component_B_points <= dt[i], i = 0..6
    #  n_CB =  number of component_B_points euclidean distance to compoentn_A_points <= dt[i], i = 0..6
    # Two way adajcency relationship is generated as 
    #   adjacency of component_A to component B = n_CA / total number of component_A_points
    #   adjacency of component_B to component A = n_CB / total number of component_B_points
    # Note :: d_threshold is a list of 
    adj.getAdjacencyByEuclideanDistance()
    writeJsonAdjacency(fname, adj.adjacent, outputfolder)


# Get adjacency relationship for all the files in the list
def adjacencyOfAllFiles(inputfilelist, maxnumfacepoints, maxnumedgepoints, objfolder, bboxfolder, outputfolder):
    fopen = open(inputfilelist,'r')
    for line in fopen:
        line = line.strip()
        print(line)
        adjacencyOfAFile(line, maxnumfacepoints, maxnumedgepoints, objfolder, bboxfolder,  outputfolder)


# Relationship estimation for a list of files or a single file
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--isfileorlist',type=str, help="To process a list of files or a single fil")
    parser.add_argument('--inputfileorlist',type=str, help="The file with filenames per line")
    parser.add_argument('--maxfacepoints',type=int, default=50, help="maximum number of points on a the largest face")
    parser.add_argument('--maxedgepoints',type=int, default=10, help="maximum number of points on the longest edge")
    parser.add_argument('--objfolder',type=str,  help="Obj files directory location")
    parser.add_argument('--bboxfolder',type=str,  help="BBox files directory location")
    parser.add_argument('--outputfolder', type=str, default=".",help="destination folder to store the json file of adjacency relationships of components per building")

    args = parser.parse_args()

    if args.isfileorlist is None:
        print("Pass argument - file or list")
        exit()
    if args.inputfileorlist is None:
        print("Pass the name of the file or the list of filenames")
        exit()
    if args.objfolder is None:
        print("Pass the location of objfiles")
        exit()
    if args.outputfolder is None:
        print("Pass the location of detinationfolder to save files")
        exit()
    if args.bboxfolder is None:
        print("Pass the location of bboxfolder")
        exit()
    
    if args.isfileorlist == "list":
        adjacencyOfAllFiles(args.inputfileorlist, args.maxfacepoints, args.maxedgepoints, args.objfolder, args.bboxfolder, args.outputfolder)
    if args.isfileorlist == "file":
        adjacencyOfAFile(args.inputfileorlist, args.maxfacepoints, args.maxedgepoints, args.objfolder, args.bboxfolder, args.outputfolder)

