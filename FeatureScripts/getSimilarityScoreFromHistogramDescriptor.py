import numpy as np
import json
import copy
import os
import sys


# The similarity score is calculated as a histogram
# of distance from centroid of a compoents to all its vertices
# and the difference in the score is given as
# similarity weight between components

NUM_BINS = 64

def clamp(n, smallest, largest): 
  return max(smallest, min(n, largest))


def findDistanceFromCentroid(objectvalues):
  vertices = objectvalues["vertex"]
  faces = objectvalues["faces"]
  centroid = objectvalues["centroid"]

  if(len(faces) <= 0) or (len(vertices) <= 0):
    return []

  distancemetric  = []
  maxdistance = 0.0
  for v in vertices:
      dist = np.linalg.norm(np.array(centroid) - np.array(v))
      distancemetric.append(dist)
  distancemetric.sort()

  maxdistance = max(distancemetric)
  if maxdistance <= 1e-20:
    return []

  bin_size = maxdistance*1.0 / NUM_BINS;

  features = [0] * (NUM_BINS+1)

  for d in distancemetric:
    c_bin =  clamp(d*1.0/bin_size, 0, NUM_BINS -1)
    bin_max = (c_bin+1)*bin_size*1.0;
    k = d*1.0/bin_max
    features[int(c_bin)] += k
  features[NUM_BINS] = maxdistance
  return features


def getSimilarScore(compfeature1, compfeature2, numverts):
  diff = 0

  for i in range(len(compfeature1)):
      diff += np.abs(compfeature1[i] - compfeature2[i])

  return diff/numverts


def collectSimilarScoreComponentsOfAFile(fname, metadatafolder, outputfolder):
    # this metadata file contains the number of components
    # component vertices, faces and centroid
    # This could be computed for any mesh file with seperated groups/objects
    # a sample metadata file is provided for reference
    metadatafile = os.path.join(metadatafolder, fname+"_pycollada_metadata.json")
    if not os.path.exists(metadatafile):
       return

    similarscorefile = os.path.join(outputfolder, fname+"_similarscore.json")
    metadata = json.load(open(metadatafile, 'r'))

    similar = {}
    componentfeatures = {}
    for objindex, values in metadata.items():
        objindex = int(objindex)
        similar[objindex] = {}
        componentfeatures[int(objindex)] = findDistanceFromCentroid(values)
    
    for objindex, values in metadata.items():
        objindex = int(objindex)
        for i in range(len(metadata)):
            valuesofi = metadata[str(i)]
            if objindex != i and not i in similar[objindex]:
                score = getSimilarScore(componentfeatures[objindex], componentfeatures[i], (len(values['vertex'])+len(valuesofi['vertex']))/2)
                similar[objindex][i] = score
                similar[i][objindex] = score
                            
    with open(similarscorefile, 'w') as similarf:
         json.dump(similar, similarf)
         similarf.close()

def collectSimilarScoreComponentsForAllFiles(inputfilelist, metadatafolder, outputfolder):
    fileinput = open(inputfilelist, 'r')
    for fname in fileinput:
        fname = fname.strip()
        collectSimilarScoreComponentsOfAFile(fname, metadatafolder, outputfolder)
    fileinput.close()
       

if __name__ == "__main__":
    param = sys.argv[1]
    if param == 'file':
        collectSimilarScoreComponentsOfAFile(*sys.argv[2:])
    elif param == 'list':
        collectSimilarScoreComponentsForAllFiles(*sys.argv[2:])
