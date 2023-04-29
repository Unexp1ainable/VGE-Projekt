from enum import Enum
from functools import cache
from typing import List, Tuple, Union
import bpy
import bmesh
from bmesh.types import BMVert, BMEdge, BMFace, BMFaceSeq
from mathutils import Vector
import numpy as np

PI = 3.14159265358979
requiresAccessTriangle = False

class Strategy(Enum):
    DELAUNAY = "DELAUNAY",
    MINIMUM_AREA = "MINIMUM_AREA",
    DELAUNAY_DIHEDRAL = "DEL_DIHEDRAL"

def costFunctionDeLaunay(v1: BMVert, v2: BMVert, v3: BMVert, v4: Union[BMVert, None]) -> float:
    """Cost function for optimization goal of DeLaunay triangles

    Args:
        v1 (BMVert): Access edge vertex 1
        v2 (BMVert): Access edge vertex 1
        v3 (BMVert): New chosen vertex
        v4 (Union[BMVert, None]): Input vertex from triangle outside this domain, making triangle with access edge. (None if no such vertex exists)

    Returns:
        float: Calculated weight
    """
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
    return (PI - min(angle1, angle2, angle3))

def costFunctionMinimumArea(v1: BMVert, v2: BMVert, v3: BMVert, v4: Union[BMVert, None]):
    """Cost function for optimization goal of minimum triangle area

    Args:
        v1 (BMVert): Access edge vertex 1
        v2 (BMVert): Access edge vertex 1
        v3 (BMVert): New chosen vertex
        v4 (Union[BMVert, None]): Input vertex from triangle outside this domain, making triangle with access edge. (None if no such vertex exists)

    Returns:
        float: Calculated weight
    """
        
    # min area
    vec1 = v2.co - v3.co
    vec0 = v2.co - v1.co
    area = vec0.cross(vec1).length / 2
    return area


def costFunctionDihedral(v1: BMVert, v2: BMVert, v3: BMVert, v4: Union[BMVert, None]) -> float:
    """Cost function for optimization goal of maximal dihedral angles

    Args:
        v1 (BMVert): Access edge vertex 1
        v2 (BMVert): Access edge vertex 1
        v3 (BMVert): New chosen vertex
        v4 (Union[BMVert, None]): Input vertex from triangle outside this domain, making triangle with access edge. (None if no such vertex exists)

    Returns:
        float: Calculated weight
    """
    if not v4:
        return 0
    n0: Vector
    n1: Vector
    n0 = (v1.co - v3.co).cross(v1.co - v2.co)
    n1 = (v4.co - v1.co).cross(v4.co - v2.co)

    if n0 == Vector((0.0, 0.0, 0.0)) or n1 == Vector((0.0, 0.0, 0.0)):
        return PI
    
    angle4 = abs(n0.angle(n1))

    if angle4 > PI:
        angle4 -= PI

    # more is better
    return PI - angle4

costFn = costFunctionDeLaunay

def proxy(v : Union[BMVert, None]) -> Union[BMVert, None]:
    if requiresAccessTriangle:
        return v
    return None

@cache
def calculateWeight(vertices: Tuple[BMVert], accessEdge: Tuple[int, int], accessTriangleVertex : Union[BMVert, None]):
    if len(vertices) == 2:
        return 0, -1

    if len(vertices) == 3:
        return costFn(*vertices, accessTriangleVertex), -1

    if abs(accessEdge[0] - accessEdge[1]) != 1 and abs(accessEdge[0] - accessEdge[1]) != len(vertices) - 1:
        raise Exception("Access edge is not an edge.")

    vertices = list(vertices)
    righterVertexI = max(accessEdge)
    lefterVertexI = min(accessEdge)
    if righterVertexI == len(vertices)-1:
        righterVertexI = min(accessEdge)
        lefterVertexI = max(accessEdge)

    weights = []

    selectedVertex = (righterVertexI+1) % len(vertices)
    d1Vertices = [vertices[righterVertexI], vertices[selectedVertex]]
    d2Vertices = vertices.copy()
    d2Vertices.remove(vertices[righterVertexI])

    righterVertex = vertices[righterVertexI]
    lefterVertex = vertices[lefterVertexI]

    for _ in range(len(vertices)-2):
        wt = costFn(vertices[accessEdge[0]], vertices[accessEdge[1]], vertices[selectedVertex],  proxy(accessTriangleVertex))
        wD1, _ = calculateWeight(tuple(d1Vertices), (0, selectedVertex-righterVertexI), proxy(lefterVertex))
        wD2, _ = calculateWeight(tuple(d2Vertices), (0, 1), proxy(righterVertex))
        weights.append(wt + wD1 + wD2)

        d2Vertices.remove(vertices[selectedVertex])
        selectedVertex = (selectedVertex+1) % len(vertices)
        d1Vertices.append(vertices[selectedVertex])

    resI = np.argmin(weights)

    return weights[resI], resI+righterVertexI+1


def triangulationFn(vertices: List[BMVert], accessEdge: Tuple[int, int], accessTriangleVertex : Union[BMVert, None]) -> List[Tuple[int,int,int]]:
    if len(vertices) < 3:
        return []
    
    if len(vertices) == 3:
        third = 0   # non accessEdge vertex
        if not 1 in accessEdge:
            third = 1
        elif not 2 in accessEdge:
            third = 2 
        return [(*accessEdge, third)]
    
    _, vertex = calculateWeight(tuple(vertices), accessEdge, proxy(accessTriangleVertex))

    result = []
    result.append((*accessEdge, vertex))

    tmpRes1 = triangulationFn([vertices[vertex]]+vertices[1:vertex], (0,1), proxy(vertices[0]))
    tmpRes2 = triangulationFn([vertices[0]] + vertices[vertex:], (0,1), proxy(vertices[1]))

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
    global costFn, requiresAccessTriangle
    
    if strategy == Strategy.DELAUNAY:
        costFn = costFunctionDeLaunay
        requiresAccessTriangle = False
    elif strategy == Strategy.MINIMUM_AREA:
        costFn = costFunctionMinimumArea
        requiresAccessTriangle = False
    elif strategy == Strategy.DELAUNAY_DIHEDRAL:
        costFn = costFunctionDihedral
        requiresAccessTriangle = True

    return triangulationFn(vertices, (0,1), None)
