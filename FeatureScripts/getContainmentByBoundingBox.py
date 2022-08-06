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

# iscontained = component_A's BBox is within component_B's BBox
# iscontaining = component_B's BBox is encompassing component_A's BBox
# the containment relationship is calculated as IOU
# IOU = intersection_volume of the BB of two components / (totalvolume - intersection volume)

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
            self.xmax += 1e-6
            self.xmin -= 1e-6
        if self.ymax - self.ymin <= 0:
            self.ymax += 1e-6
            self.ymin -= 1e-6
        if self.zmax - self.zmin <= 0:
            self.zmax += 1e-6
            self.zmin -= 1e-6
        self.volume = abs(self.xmax - self.xmin) * abs(self.ymax - self.ymin) * abs(self.zmax -self.zmin)

    # if self is containing bbox, then containment of self < containment of bbox
    # iscontained_self, iscontained_bbox, IOU
    def isContained(self, bbox):
        iscontained = False
        iscontaining = False

        if ((self.xmin <= bbox.xmin and self.xmax >= bbox.xmax) and (self.ymin <= bbox.ymin and self.ymax >= bbox.ymax) and (self.zmin <= bbox.zmin and self.zmax >= bbox.zmax)):
            iscontaining = True
        
        if ((self.xmin >= bbox.xmin and self.xmax <= bbox.xmax) and (self.ymin >= bbox.ymin and self.ymax <= bbox.ymax) and (self.zmin >= bbox.zmin and self.zmax <= bbox.zmax)):
            iscontained = True

        if iscontaining and iscontained:
            if self.volume <= 0.0 or bbox.volume <=0.0:
                IOU = 0
            else:
                IOU = 1.0
            return 1,1,1.0
            

        if iscontaining:
            if self.volume <= 0.0 or bbox.volume <=0.0:
                IOU = 0
            else:
                IOU = bbox.volume*1.0 / self.volume
            return IOU, 1 ,IOU

        if iscontained:
            if self.volume <= 0.0 or bbox.volume <=0.0:
                IOU = 0
            else:
                IOU = self.volume *1.0/bbox.volume
            return 1, IOU,IOU

        intersection_volume = max(0, (min(self.xmax, bbox.xmax) - max(self.xmin, bbox.xmin))) * max(0, (min(self.ymax, bbox.ymax) - max(self.ymin, bbox.ymin))) * max(0, (min(self.zmax, bbox.zmax) - max(self.zmin, bbox.zmin)))
        if (intersection_volume <= threshold*(min(self.volume,bbox.volume))):
            return 0,0,0

        IOU = intersection_volume*1.0/ (self.volume + bbox.volume - intersection_volume)
        return intersection_volume/self.volume, intersection_volume/bbox.volume,IOU


class ContainmentRelationship:
    def __init__(self, objfile, bboxfile):
        self.bbox = {}
        self.containment = {}
        self.objfile = objfile # uniform scale ply file
        self.bboxfile = bboxfile

    def loadBoundingBox(self):
        bbox = json.load(open(self.bboxfile, 'r'))
        for key,value in bbox.items():
            self.bbox[key] = BBox(value[0], value[1], value[2], value[3], value[4], value[5])


    def getContainmentRelation(self):
        for comp1,comp1bbox in self.bbox.items():
            for comp2,comp2bbox in self.bbox.items():
                if comp1 != comp2:
                    if not comp1 in self.containment or (comp1 in self.containment and comp2 not in self.containment[comp1]):
                        comp1_value, comp2_value, IOU = comp1bbox.isContained(self.bbox[comp2])

                        if sum([comp1_value, comp2_value, IOU]) > 0:
                            if not comp1 in self.containment:
                                self.containment[comp1] = {}
                            if not comp2 in self.containment:
                                self.containment[comp2] = {}

                            self.containment[comp1][comp2] = [comp1_value, IOU]
                            self.containment[comp2][comp1] = [comp2_value, IOU]
       

def writeJsonContainment(fname, containment, outputfolder):

    with open(os.path.join(outputfolder, fname+"_containment.json"),"w") as f:
        json.dump(containment, f)
        f.close()
    
def computeContainmentOfAFile(fname, objfolder,bboxfolder,  outputfolder):
    #print(fname)
    objfile = os.path.join(objfolder, fname+".obj")
    bboxfile = os.path.join(bboxfolder, fname+"_bbox.json")
    containmentObj = ContainmentRelationship(objfile, bboxfile)
    containmentObj.loadBoundingBox()
    containmentObj.getContainmentRelation()
    writeJsonContainment(fname, containmentObj.containment, outputfolder)


def computeContainmentOfAllFiles(inputfilelist, objfolder, bboxfolder, outputfolder):
    fopen = open(inputfilelist,'r')
    for line in fopen:
        line = line.strip()
        print(line)
        computeContainmentOfAFile(line, objfolder, bboxfolder, outputfolder)

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
        computeContainmentOfAllFiles(args.inputfileorlist, args.objfolder, args.bboxfolder, args.outputfolder)
    if args.isfileorlist == "file":
        computeContainmentOfAFile(args.inputfileorlist, args.objfolder, args.bboxfolder,args.outputfolder)

