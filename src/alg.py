from enum import Enum
from functools import cache
from typing import List, Tuple
import bpy
import bmesh
from bmesh.types import BMVert, BMEdge, BMFace, BMFaceSeq
from mathutils import Vector
import numpy as np

PI = 3.14159265358979

class Strategy(Enum):
    DELAUNAY = "DELAUNAY",
    MINIMUM_AREA = "MINIMUM_AREA" 

def costFunctionDeLaunay(v1: BMVert, v2: BMVert, v3: BMVert):
    # min angle
    vec0: Vector
    vec1: Vector
    vec1 = v1.co - v3.co
    vec0 = v1.co - v2.co
    angle1 = vec0.angle(vec1)

    vec0: Vector
    vec1: Vector
    vec1 = v2.co - v3.co
    vec0 = v2.co - v1.co
    angle2 = vec0.angle(vec1)
    angle3 = PI - angle1 - angle2

    # more is better
    return (PI - min(angle1, angle2, angle3))/PI

def costFunctionMinimumArea(v1: BMVert, v2: BMVert, v3: BMVert):
    # min area
    vec1 = v2.co - v3.co
    vec0 = v2.co - v1.co
    area = vec0.cross(vec1).length / 2
    return area

costFn = costFunctionDeLaunay

@cache
def calculateWeight(vertices: Tuple[BMVert], accessEdge: Tuple[int, int]):
    if len(vertices) == 2:
        return 0, -1

    if len(vertices) == 3:
        return costFn(*vertices), -1

    if abs(accessEdge[0] - accessEdge[1]) != 1 and abs(accessEdge[0] - accessEdge[1]) != len(vertices) - 1:
        raise Exception("Access edge is not an edge.")

    vertices = list(vertices)
    righterVertex = max(accessEdge)
    if righterVertex == len(vertices)-1:
        righterVertex = min(accessEdge)
    weights = []

    selectedVertex = (righterVertex+1) % len(vertices)
    d1Vertices = [vertices[righterVertex], vertices[selectedVertex]]
    d2Vertices = vertices.copy()
    d2Vertices.remove(vertices[righterVertex])

    for _ in range(len(vertices)-2):
        wt = costFn(vertices[accessEdge[0]], vertices[accessEdge[1]], vertices[selectedVertex])
        wD1, _ = calculateWeight(tuple(d1Vertices), (0, selectedVertex-righterVertex))
        wD2, _ = calculateWeight(tuple(d2Vertices), (0, 1))
        weights.append(wt + wD1 + wD2)

        d2Vertices.remove(vertices[selectedVertex])
        selectedVertex = (selectedVertex+1) % len(vertices)
        d1Vertices.append(vertices[selectedVertex])

    resI = np.argmin(weights)

    return weights[resI], resI+righterVertex+1


def triangulationFn(vertices: List[BMVert], accessEdge: Tuple[int, int]) -> List[Tuple[int,int,int]]:
    if len(vertices) < 3:
        return []
    
    if len(vertices) == 3:
        third = 0
        if not 1 in accessEdge:
            third = 1
        elif not 2 in accessEdge:
            third = 2 
        return [(*accessEdge, third)]
    
    _, vertex = calculateWeight(tuple(vertices), accessEdge)

    result = []
    result.append((*accessEdge, vertex))

    # righterVertex = max(accessEdge)
    # if righterVertex == len(vertices)-1:
    #     righterVertex = min(accessEdge)

    # vD1 = []
    # vD2 = []

    # for i in range(min(accessEdge), min(accessEdge) + len(vertices)):
    #     index = i % len(vertices)
    #     vD1 

    tmpRes1 = triangulationFn([vertices[vertex]]+vertices[1:vertex], (0,1))
    tmpRes2 = triangulationFn([vertices[0]] + vertices[vertex:], (0,1))

    for v1,v2,v3 in tmpRes1:
        if v1 == 0:
            v1 += vertex
        result.append((v1,v2,v3))

    for v1,v2,v3 in tmpRes2:
        if v1 != 0:
            v1 += vertex - 1
        result.append((v1,v2+vertex-1,v3+vertex-1))

    return result


def triangulate(vertices: List[BMVert], strategy : Strategy) -> List[Tuple[int,int,int]]:
    global costFn
    
    if strategy == Strategy.DELAUNAY:
        costFn = costFunctionDeLaunay
    elif strategy == Strategy.MINIMUM_AREA:
        costFn = costFunctionMinimumArea

    return triangulationFn(vertices, (0,1))
