import os
import numpy as np
import json
import sys
import pickle
from scipy import spatial
from collections import Counter
#import torch
import statistics

toplabels = {0:"undetermined",1:"wall", 2:"window", 3:"vehicle",4:"roof", 5:"plant_tree", 6:"door", 7:"tower_steeple", 8:"furniture", 9:"ground_grass", 10:"beam_frame", 11:"stairs", 12:"column", 13:"railing_baluster",\
             14:"floor", 15:"chimney", 16:"ceiling", 17:"fence", 18:"pond_pool", 19:"corridor_path", 20:"balcony_patio", 21:"garage", 22:"dome", 23:"road", 24:"entrance_gate", 25:"parapet_merlon",\
             26:"buttress", 27:"dormer", 28:"lantern_lamp", 29:"arch", 30:"awning", 31:"shutters" }

freqlabels={1:"wall",2:"window",3:"vehicle",4:"roof",5:"plant_tree",6:"door",7:"tower_steeple",8:"furniture",10:"beam_frame",11:"stairs",12:"column",17:"fence",20:"balcony_patio",25:"parapet_merlon"}


def getNearestNeighbour(index, centroids):
    dist = np.sqrt(np.sum((np.array(centroids) - np.array(centroids[index]))**2, axis=1))
    
    minindex = np.argpartition(dist,1)
    return minindex

# ground - label from 0 
# pred - label from 1
def getPointIOU(ground, prediction):

    union = {}
    intersection = {}
    orig = ground[ground != 0]
    pred = prediction[ground != 0]
    correctall = (orig == pred)
    for i in range(1,len(toplabels)):
        intersection[i] = ((orig == i) & (pred == i)).sum()
        union[i] = ((orig ==i ) | (pred == i)).sum()
    return union, intersection

def getAveragePoolingPredictionFromPointsToFace(pointpred_31,points_100K, faceindex_100K, facecentroid):
    prediction = np.zeros(len(facecentroid))

    allfaces = np.arange(len(facecentroid))
    unsampled = np.setdiff1d(allfaces, faceindex_100K)
    sampled = np.intersect1d(allfaces, faceindex_100K)
    unsampled_facecentroid = facecentroid[unsampled]
    sys.setrecursionlimit(10000)
    tree = spatial.cKDTree(points_100K)
    #_,nearest = tree.query(unsampled_facecentroid, k=1, distance_upper_bound=0.2)
    _,nearest = tree.query(unsampled_facecentroid, k=1, distance_upper_bound=0.2)
    prediction[unsampled] = np.argmax(pointpred_31[nearest], axis=1)+1
    p = pointpred_31[nearest][:,np.newaxis]
    avgpool_pred_31 = dict(zip(unsampled,p))
    
    for face in sampled:
        indexes = np.array(np.where(faceindex_100K == face)[0])
        prediction[int(face)] = np.argmax(np.mean(pointpred_31[indexes], axis=0))+1
        avgpool_pred_31[int(face)] = pointpred_31[indexes]

    return prediction, avgpool_pred_31


def getAveragePoolingPredictionFromFaceToComponent(facepred_31, faceToComponent, numcomp):
    prediction = np.zeros(numcomp)
    for comp in range(numcomp):
        indexes = np.array(np.where(faceToComponent == comp)[0])
        features = np.vstack(np.array([facepred_31[k] for k in indexes]))
        prediction[comp] = np.argmax(np.mean(features, axis=0))+1

    return prediction

def getTriangleOrComponentIOU(ground, prediction, area):
    IOUwitharea = {}# {i+1:0 for i in range(len(toplabels)-1)}
    IOU = {}
    area_union = {}
    area_intersection = {}

    eq = np.dot(area, (ground == prediction)&(ground != 0))
    leng = np.dot(area, (ground != 0))
    acc = eq/leng
    
    prediction[ground == 0] = 0
    for i in range(1,len(toplabels)):
        area_union[i] = np.array(area[(ground == i)|(prediction==i)]).sum()
        area_intersection[i] = np.array(area[(ground == i)&(prediction==i)]).sum()
    return area_union, area_intersection, acc

def getPartIOU(buildingIOU, destfolder, destname):
    area_intersection = {label:0 for label in range(1, len(toplabels))}
    area_union = {label:0 for label in range(1,len(toplabels))}
    for building, value in buildingIOU.items():
        for label in range(1,len(toplabels)):
            area_intersection[label] += value["area_intersection"][label]
            area_union[label] += value["area_union"][label]

    result = {toplabels[label]: float(area_intersection[label])/(float(1e-40+area_union[label])) for label in range(1,len(toplabels))}
    result['all'] = sum(result.values())/float(len(toplabels)-1)
    result['freq'] = sum([result[toplabels[key]] for key in freqlabels.keys()])/float(len(freqlabels))

    with open(os.path.join(destfolder, destname+'_partIOU.json'),'w') as fwrite:
        json.dump(result, fwrite)
        fwrite.close()

def getShapeIOU(buildingIOU, destfolder, destname):
    shapeIOU = {b:0.0 for b in list(buildingIOU.keys())}
    for building, value in buildingIOU.items():
        numlabel = 0
        for label in range(1,len(toplabels)):
            area_intersection = value["area_intersection"][label]
            area_union = value["area_union"][label]
            if area_union > 0:
                shapeIOU[building] += float(area_intersection)/float(area_union)
                numlabel += 1
        shapeIOU[building] /= numlabel
    shapeIOU['all'] = sum(shapeIOU.values())/float(len(buildingIOU))

    with open(os.path.join(destfolder, destname+'_shapeIOUPerBuilding.json'),'w') as fwrite:
        json.dump(shapeIOU, fwrite)
        fwrite.close()

def getClassificationAccuracy(buildingIOU, destfolder, destname):
    accuracy = 0
    for building, value in buildingIOU.items():
        accuracy += value["area_accuracy"]

    accuracy /= float(len(buildingIOU))
    with open(os.path.join(destfolder, destname+'_classificationAccuracy.txt'),'w') as fwrite:
        fwrite.write(str(accuracy))
        fwrite.close()


def getPointPartAndShapeIOUFromFile(fname, picklefolder):
    p = pickle.load(open(os.path.join(picklefolder, fname+'.pkl'),'rb'))
    union, intersection, accuracy = getBuildingPointIOU(p['orig'], p['pred'])
    result["area_union"] = union
    result["area_intersection"] = intersection
    result["area_accuracy"] = accuracy
    return result

def getPointPartAndShapeIOUFromList(inputfilelist, picklefolder, destfolder, destname):
    fread = open(inputfilelist, 'r')
    buildingIOU = {}
    for line in fread:
        line = line.strip()
        buildingIOU[line] = getPointPartAndShapeIOUFromFile(line, picklefolder)

    getPartIOU(buildingIOU, destfolder, destname)
    getShapeIOU(buildingIOU, destfolder, destname)


def getTrianglePartAndShapeIOUFromFaceFromFile(fname, facepred_31, plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder):
    #pointpred_31 = pickle.load(open(os.path.join(picklefolder, fname+'.pkl'),'rb'))
    #pointpred_31 = np.load(os.path.join(pred31folder, '80_checkpoint.npy'))[2]
    facearea = np.array(list((json.load(open(os.path.join(faceareafolder, fname+'.json'),'r'))).values()))
    facecentroid = np.array(list((json.load(open(os.path.join(facecentroidfolder, fname+'.json'),'r'))).values()))

    prediction = np.argmax(facepred_31, axis=1)+1
    ground = np.array(list((json.load(open(os.path.join(facegroundlabelfolder, fname+'.json'),'r'))).values()))
    area_union, area_intersection, acc = getTriangleOrComponentIOU(ground, prediction, facearea)
    result = {}
    result["triangle_area_union"] = area_union
    result["triangle_area_intersection"] = area_intersection
    result["triangle_area_accuracy"] = acc

    faceToComponentjson = json.load(open(os.path.join(faceToComponentfolder, fname+".json"), "r"))

    faceToComponent = np.zeros(len(facecentroid))
    for start,value in faceToComponentjson.items():
        end = int(list(value.keys())[0])
        comp = int(list(value.values())[0])
        faceToComponent[np.arange(int(start), int(end)+1)] = int(comp)
        
    ground = np.array(list((json.load(open(os.path.join(componentgroundlabelfolder, fname+'_label.json'),'r'))).values()))
    surfacearea = np.array(list((json.load(open(os.path.join(surfaceareafolder, fname+'_pycollada_unitcube_surfacearea.json'),'r'))).values()))

    prediction = getAveragePoolingPredictionFromFaceToComponent(facepred_31, faceToComponent, len(faceToComponentjson))

    #IOU, IOUwitharea, area_union, area_intersection = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    area_union, area_intersectiom,acc = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    result["component_area_union"] = area_union
    result["component_area_intersection"] = area_intersection
    result["component_area_accuracy"] = acc

    return result

#def getTrianglePartAndShapeIOUFromFile(fname, picklefolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder, componentCentroidfolder):
def getTrianglePartAndShapeIOUFromFile(fname, pointpred_31, plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder):
    #pointpred_31 = pickle.load(open(os.path.join(picklefolder, fname+'.pkl'),'rb'))
    #pointpred_31 = np.load(os.path.join(pred31folder, '80_checkpoint.npy'))[2]
    facearea = np.array(list((json.load(open(os.path.join(faceareafolder, fname+'.json'),'r'))).values()))
    faceindexfile = open(os.path.join(faceindexfolder, fname+'.txt'),'r')
    facecentroid = np.array(list((json.load(open(os.path.join(facecentroidfolder, fname+'.json'),'r'))).values()))
    points_100K = []

    plyfile = open(os.path.join(plyfolder, fname+'.ply'), 'r')
    count = 0
    for line in plyfile:
        line = line.strip()
        if count < 12:
            count += 1
            continue
        data = line.split()
        points_100K.append([float(data[0]), float(data[1]), float(data[2])]) 

    points_100K = np.array(points_100K)

    faceindex = []
    for line in faceindexfile:
        faceindex.append(line.strip())
    faceindex = np.array(faceindex)

    prediction, avgpool_trianglepred_31 = getAveragePoolingPredictionFromPointsToFace(pointpred_31, points_100K, faceindex, facecentroid)
    ground = np.array(list((json.load(open(os.path.join(facegroundlabelfolder, fname+'.json'),'r'))).values()))
    area_union, area_intersection, area_acc = getTriangleOrComponentIOU(ground, prediction, facearea)
    result = {}
    result["triangle_area_union"] = area_union
    result["triangle_area_intersection"] = area_intersection
    result["triangle_area_accuracy"] = area_acc

    faceToComponentjson = json.load(open(os.path.join(faceToComponentfolder, fname+".json"), "r"))

    faceToComponent = np.zeros(len(facecentroid))
    for start,value in faceToComponentjson.items():
        end = int(list(value.keys())[0])
        comp = int(list(value.values())[0])
        faceToComponent[np.arange(int(start), int(end)+1)] = int(comp)
        
    ground = np.array(list((json.load(open(os.path.join(componentgroundlabelfolder, fname+'_label.json'),'r'))).values()))
    surfacearea = np.array(list((json.load(open(os.path.join(surfaceareafolder, fname+'_pycollada_unitcube_surfacearea.json'),'r'))).values()))

    prediction = getAveragePoolingPredictionFromFaceToComponent(avgpool_trianglepred_31, faceToComponent, len(faceToComponentjson))

    #IOU, IOUwitharea, area_union, area_intersection = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    area_union, area_intersection, area_acc = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    result["component_area_union"] = area_union
    result["component_area_intersection"] = area_intersection
    result["component_area_accuracy"] = area_acc

    return result


def getTrianglePartAndShapeIOUFromFaceFromList(inputfilelist, pred31folder, plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder, destfolder, checkpoint):
    fread = open(inputfilelist, 'r')
    buildingTriangleIOU = {}
    buildingComponentIOU = {}
    for line in fread:
        line = line.strip()
        print("{}".format(line), flush=True)
        facepred_31 = (np.load(os.path.join(pred31folder, line+'.npy')))
        #result = getTrianglePartAndShapeIOUFromFile(line, picklefolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder, componentCentroidfolder)
        result = getTrianglePartAndShapeIOUFromFaceFromFile(line, facepred_31, plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder)
        buildingTriangleIOU[line] = {"area_union": result["triangle_area_union"], "area_intersection": result["triangle_area_intersection"], "area_accuracy": results["triangle_area_accuracy"]}
        buildingComponentIOU[line] = {"area_union": result["component_area_union"], "area_intersection": result["component_area_intersection"], "area_accuracy": results["component_area_accuracy"]}

    getPartIOU(buildingTriangleIOU, destfolder, "triangle_"+checkpoint)
    getShapeIOU(buildingTriangleIOU, destfolder, "triangle_"+checkpoint)
    getClassificationAccuracy(buildingIOU, destfolder, "triangle_"+checkpoint)

    getPartIOU(buildingComponentIOU, destfolder, "component_"+checkpoint)
    getShapeIOU(buildingComponentIOU, destfolder, "component_"+checkpoint)
    getClassificationAccuracy(buildingIOU, destfolder, "component_"+checkpoint)

def getTrianglePartAndShapeIOUFromList(inputfilelist, pred31folder, plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder, destfolder, checkpoint):
    fread = open(inputfilelist, 'r')
    buildingTriangleIOU = {}
    buildingComponentIOU = {}
    for line in fread:
        line = line.strip()
        print("{} {}".format(count, line), flush=True)
        #result = getTrianglePartAndShapeIOUFromFile(line, picklefolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder, componentCentroidfolder)
        pointpred_31 = (np.load(os.path.join(pred31folder, line+'.npy')))
        result = getTrianglePartAndShapeIOUFromFile(line, pointpred_31[count], plyfolder, facegroundlabelfolder, componentgroundlabelfolder, faceindexfolder, faceareafolder, surfaceareafolder, facecentroidfolder, faceToComponentfolder)
        buildingTriangleIOU[line] = {"area_union": result["triangle_area_union"], "area_intersection": result["triangle_area_intersection"], "area_accuracy": results["triangle_area_accuracy"]}
        buildingComponentIOU[line] = {"area_union": result["component_area_union"], "area_intersection": result["component_area_intersection"], "area_accuracy": results["component_area_accuracy"]}
   
    getPartIOU(buildingTriangleIOU, destfolder, "triangle_"+checkpoint)
    getShapeIOU(buildingTriangleIOU, destfolder, "triangle_"+checkpoint)
    getClassificationAccuracy(buildingTriangleIOU, destfolder, "triangle_"+checkpoint)

    getPartIOU(buildingComponentIOU, destfolder, "component_"+checkpoint)
    getShapeIOU(buildingComponentIOU, destfolder, "component_"+checkpoint)
    getClassificationAccuracy(buildingComponentIOU, destfolder, "component_"+checkpoint)


def getComponentPartAndShapeIOUFromFile(fname, componentgroundlabelfolder, surfaceareafolder, predfolder):
    #prediction = pickle.load(open(os.path.join(picklefolder, fname+'.pkl'),'rb'))
    prediction = (np.load(os.path.join(predfolder, fname+".npy")))+1
    surfacearea = np.array(list((json.load(open(os.path.join(surfaceareafolder, fname+'_pycollada_unitcube_surfacearea.json'),'r'))).values()))
    #ground = torch.tensor(list((json.load(open(os.path.join(componentgroundlabelfolder, fname+'.json'),'r'))).values()), dtype=torch.int32)
    ground = np.array(list((json.load(open(os.path.join(componentgroundlabelfolder, fname+'_label.json'),'r'))).values()))
    #IOU, IOUwitharea, area_union, area_intersection = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    area_union, area_intersection, area_accuracy = getTriangleOrComponentIOU(ground, prediction, surfacearea)
    result = {}
    result["area_union"] = area_union
    result["area_intersection"] = area_intersection
    result["area_accuracy"] = area_accuracy
    return result

    
def getComponentPartAndShapeIOUFromList(inputfilelist, componentgroundlabelfolder, surfaceareafolder, predfolder, destfolder, destname):
    fread = open(inputfilelist, 'r')
    buildingIOU = {}
    for line in fread:
        line = line.strip()
        print(line)
        buildingIOU[line] = getComponentPartAndShapeIOUFromFile(line, componentgroundlabelfolder, surfaceareafolder, predfolder)
        #buildingIOU[line] = getPointPartAndShapeIOUFromFile(line, picklefolder)

    if destfolder is None:
        destfolder = predfolder
    getPartIOU(buildingIOU, destfolder, destname)
    getShapeIOU(buildingIOU, destfolder, destname)
    getClassificationAccuracy(buildingIOU, destfolder, destname)

if __name__ == "__main__":
    param = sys.argv[1]
    if param == 'point':
        getPointPartAndShapeIOUFromList(*sys.argv[2:]) 
    elif param =='triangle':
        getTrianglePartAndShapeIOUFromList(*sys.argv[2:]) 
    elif param =='shapetriangle':
        getTrianglePartAndShapeIOUFromFaceFromList(*sys.argv[2:]) 
    elif param =='component':
        getComponentPartAndShapeIOUFromList(*sys.argv[2:]) 

