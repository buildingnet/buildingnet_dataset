import os
import math
import numpy as np
import ctypes

def generateQuasiRandomPoint(i, jitter):
    if i <= 0 :
        print("point must be positive")

    if jitter < 0:
        print("jitter constant must be positive")


    plastic_constant = g = 1.324717957244746
    sqrtpi = 1.7724538509055159#  math.sqrt(math.pi)

    a0 = 1.0 / g
    a1 = 1.0 / (g*g)


    d0 = 0.76
    i0 = 0.7

    c = np.uint32(i)
    c = np.uint32(c ^(c >> 15))
    c = np.uint32(c*0x85ebca77)
    c = np.uint32(c^(c >> 13))
    c = np.uint32(c * 0xc2b2ae3d)

    n0 = (1.0 / 4294967295.0) *(c*1.0*741103597)
    n1 = (1.0 / 4294967295.0) *(c*1.0*1597334677)

    f = i*1.0
    jitter = (jitter * sqrtpi *d0) / (4.0 * math.sqrt(f - i0))

    x = ((0.5 + a0 * f + jitter * n0)%( 1.0))
    y = ((0.5 + a1 * f + jitter * n1)% (1.0))

    return x, y

def getQuasiRandomPoint(v1,v2,v3, numpoints, jitter):

    points = []
    for i in range(1,numpoints+1):
        u, w = generateQuasiRandomPoint(i, 0.5) 
        #print(str(u)+"::"+str(w))
        if u+w > 1.0:
            u = 1 - u
            w = 1 - w

        p = (1 - u - w) * v1 + u * v2 + w * v3
        points.append(np.array(p))
    points = np.array(points)
    return points

def getEdgePoints(v1,v2,beta, numpoints):
    points = []

    for p in range(1,numpoints):
        l = p*beta
        v = l*v1 + (1.0-l)*v2
        points.append(np.array(v))

    points = np.array(points)
    return points

