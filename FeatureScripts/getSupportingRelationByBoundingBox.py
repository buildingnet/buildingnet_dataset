import os
import sys
import json
import math
import numpy as np
#import open3d as o3d
#from open3d import *
import collada
import operator as op
from collada import *
from quasirandompoint import *
#import matplotlib.pyplot as plt
import PIL
from PIL import Image

from scipy import spatial
import argparse

threshold = 0.1

class BBox:
    # return iscontaining, iscontained
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
        self.volume = abs(self.xmax - self.xmin) * abs(self.ymax - self.ymin) * abs(self.zmax -self.zmin)
        self.xy = (self.xmax - self.xmin)*(self.ymax - self.ymin)
        self.yz = (self.ymax - self.ymin)*(self.zmax - self.zmin)
        self.xz = (self.xmax - self.xmin)*(self.zmax - self.zmin)

    # if self is containing bbox, then containment of self < containment of bbox
    # iscontained_self, iscontained_bbox, IOU
    def isSupporting(self, bbox):
        issupported = False
        issupporting = False

        if ((self.xmin <= bbox.xmin and self.xmax >= bbox.xmax) and (self.ymin <= bbox.ymin and self.ymax >= bbox.ymax) and (self.zmin <= bbox.zmin and self.zmax >= bbox.zmax)):
            return False,None,None,None
        
        if ((self.xmin >= bbox.xmin and self.xmax <= bbox.xmax) and (self.ymin >= bbox.ymin and self.ymax <= bbox.ymax) and (self.zmin >= bbox.zmin and self.zmax <= bbox.zmax)):
            return False,None,None,None

        distance = abs(max(self.ymin, bbox.ymin) - min(self.ymax , bbox.ymax))
        intersection_area = max(0, (min(self.xmax, bbox.xmax) - max(self.xmin, bbox.xmin))) * max(0, (min(self.zmax, bbox.zmax) - max(self.zmin, bbox.zmin)))
        minarea = min(self.xz , bbox.xz)

#        if self.xz <= 1e-10 and bbox.xz <= 1e-10:
#            intersection_area = 1e-4
#            avgarea = 1e-4
#        elif self.xz <= 1e-10 or bbox.xz <= 1e-10:
#            if self.xz <= 1e-10:
#                intersection_area = threshold*bbox.xz
#            else:
#                intersection_area = threshold*self.xz
        avgy = ((self.ymax - self.ymin) + (bbox.ymax - bbox.ymin))/2
        
        if (distance <= (threshold*avgy) and (intersection_area >= 0.1 * minarea)):
            return True,(threshold*avgy), distance, intersection_area
        return False,None,None,None 


class SupportingRelationship:
    def __init__(self, objfile, bboxfile):
        self.numcomponents = 0
        self.vertices = []
        self.faces = []
        self.faceindex = {}

        self.binpoints = []

        self.bbox = {}
        self.support = {}
        self.objfile = objfile # uniform scale ply file
        self.bboxfile = bboxfile

    def loadBoundingBox(self):
        bbox = json.load(open(self.bboxfile,'r'))
        for key, value in bbox.items():
            self.bbox[key] = BBox(value[0],value[1],value[2],value[3],value[4],value[5])

    def getSupportingRelation(self):
        for comp1,comp1bbox in self.bbox.items():
            for comp2,comp2bbox in self.bbox.items():
                if comp1 != comp2:
                    if (not comp1 in self.support) or ((comp1 in self.support) and (comp2 not in self.support[comp1])):
                        isSupporting, thresholdheight, diffheight, intersection_area = comp1bbox.isSupporting(self.bbox[comp2])
                        if isSupporting:
                            thresholdarr = [0.01*thresholdheight, 0.025*thresholdheight, 0.05*thresholdheight,0.1*thresholdheight, 0.25*thresholdheight, 0.5*thresholdheight, 1*thresholdheight]
                            percentage = [0.01,0.025,0.05,0.1, 0.25, 0.5, 1]
                            if not comp1 in self.support:
                                self.support[comp1] = {}
                            if not comp2 in self.support[comp1]:
                                self.support[comp1][comp2] = []
                            if not comp2 in self.support:
                                self.support[comp2] = {}
                            if not comp1 in self.support[comp2]:
                                self.support[comp2][comp1] = []


                            for thresh in thresholdarr:
                              
                                if diffheight <= thresh:
                                    self.support[comp1][comp2].append(intersection_area/self.bbox[comp1].xz)
                                    self.support[comp2][comp1].append(intersection_area/self.bbox[comp2].xz)
                                else:
                                    self.support[comp1][comp2].append(0.0)
                                    self.support[comp2][comp1].append(0.0)

def writeJsonSupport(fname, support, outputfolder):

    with open(os.path.join(outputfolder, fname+"_support.json"),"w") as f:
        json.dump(support, f)
        f.close()
    

def computeSupportingRelationshipOfAFile(fname, objfolder, bboxfolder, outputfolder):
    #print(fname)
    objfile = os.path.join(objfolder, fname+".obj")
    bboxfile = os.path.join(bboxfolder, fname+"_bbox.json")
    supportObj = SupportingRelationship(objfile, bboxfile)
    supportObj.loadBoundingBox()
    supportObj.getSupportingRelation()
    writeJsonSupport(fname, supportObj.support, outputfolder)


def computeSupportingRelationshipOfAllFiles(inputfilelist, objfolder, bboxfolder, outputfolder):
    fopen = open(inputfilelist,'r')
    for line in fopen:
        line = line.strip()
        print(line)
        computeSupportingRelationshipOfAFile(line, objfolder, bboxfolder, outputfolder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--isfileorlist',type=str, help="To process a list of files or a single fil")
    parser.add_argument('--inputfileorlist',type=str, help="The file with filenames per line")
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
    if args.bboxfolder is None:
        print("Pass the location of bboxfiles")
        exit()
    if args.outputfolder is None:
        print("Pass the location of detinationfolder to save files")
        exit()
    
    
    if args.isfileorlist == "list":
        computeSupportingRelationshipOfAllFiles(args.inputfileorlist, args.objfolder, args.bboxfolder, args.outputfolder)
    if args.isfileorlist == "file":
        computeSupportingRelationshipOfAFile(args.inputfileorlist, args.objfolder, args.bboxfolder, args.outputfolder)

