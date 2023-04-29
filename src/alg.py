"""
=========================================================================
Brief: Implementation of the triangulation algorithm for VGE project
Authors:
    Marek Mudroň (xmudro04)
    Matej Kunda  (xkunda00)
    Samuel Repka (xrepka07)
File: alg.py
Date: April 2023
=========================================================================
"""

from enum import Enum
from functools import cache
from typing import List, Tuple, Union
from bmesh.types import BMVert
import numpy as np
from .cost_functions import *

NO_VERTEX = -1


class Strategy(Enum):
    """Triangulation strategy"""

    DELAUNAY = "DELAUNAY"
    MINIMUM_AREA = "MINIMUM_AREA"
    DELAUNAY_DIHEDRAL_MAX = "DEL_DIHEDRAL_MAX"
    DELAUNAY_DIHEDRAL_MIN = "DEL_DIHEDRAL_MIN"


requiresAccessTriangle = False
costFn = costFunctionDeLaunay


class VGEException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def proxy(v: Union[BMVert, None]) -> Union[BMVert, None]:
    """Proxy function for access triagle vertex. Returns None if requiresAccessTriangle is set to True. (improves caching efficiency)

    Args:
        v (Union[BMVert, None]): Access triangle vertex

    Returns:
        Union[BMVert, None]: Vertex or None, depending on requiresAccessTriangle global
    """
    if requiresAccessTriangle:
        return v
    return None


@cache
def calculateCost(vertices: Tuple[BMVert],
                  accessEdge: Tuple[int, int],
                  accessTriangleVertex: Union[BMVert, None]) -> Tuple[float, int]:
    """Calculate cost of the triangulation for the polygon with this accessEdge.

    Args:
        vertices (Tuple[BMVert]): Vertices of the polygon in order as connected by edges.
        accessEdge (Tuple[int, int]): Access edge of the polygon
        accessTriangleVertex (Union[BMVert, None]): Access triangle vertex

    Raises:
        VGEException: if access edge is not from neighbouring vertices

    Returns:
        Tuple[float, int]: Tuple (calculated cost, best vertex index)
    """
    if len(vertices) == 2:
        return 0, NO_VERTEX

    if len(vertices) == 3:
        return costFn(*vertices, accessTriangleVertex), NO_VERTEX

    if abs(accessEdge[0] - accessEdge[1]) != 1 and abs(accessEdge[0] - accessEdge[1]) != len(vertices) - 1:
        raise VGEException("Access edge is not an edge.")

    # prepare for the iterations
    vertices = list(vertices)  # vertices must be tuple in order to be able to use @cache decorator
    # index of the accessEdge vertex at the beginning of the vertices list
    righterVertexI = max(accessEdge)
    # index of the accessEdge vertex at the end of the vertices list
    lefterVertexI = min(accessEdge)
    if righterVertexI == len(vertices)-1:
        righterVertexI = min(accessEdge)
        lefterVertexI = max(accessEdge)

    costs = []

    # vertex that is currently selected and being cost calculated
    selectedVertex = (righterVertexI+1) % len(vertices)
    # vertices belonging to the domain D1
    d1Vertices = [vertices[righterVertexI], vertices[selectedVertex]]
    # vertices belonging to the domain D2
    d2Vertices = vertices.copy()
    d2Vertices.remove(vertices[righterVertexI])

    righterVertex = vertices[righterVertexI]
    lefterVertex = vertices[lefterVertexI]

    # iteratively calculate cost for each possible triangulation
    for _ in range(len(vertices)-2):
        wt = costFn(
            vertices[accessEdge[0]],
            vertices[accessEdge[1]],
            vertices[selectedVertex],
            proxy(accessTriangleVertex))
        wD1, _ = calculateCost(tuple(d1Vertices), (0, selectedVertex-righterVertexI), proxy(lefterVertex))
        wD2, _ = calculateCost(tuple(d2Vertices), (0, 1), proxy(righterVertex))
        costs.append(wt + wD1 + wD2)

        d2Vertices.remove(vertices[selectedVertex])
        selectedVertex = (selectedVertex+1) % len(vertices)
        d1Vertices.append(vertices[selectedVertex])

    # find the best cost
    resI = np.argmin(costs)
    bestCost = costs[resI]
    bestVertex = resI+righterVertexI+1

    return bestCost, bestVertex


def triangulationFn(vertices: List[BMVert],
                    accessEdge: Tuple[int, int],
                    accessTriangleVertex: Union[BMVert, None]) -> List[Tuple[int, int, int]]:
    """Recursive triangulation function

    Args:
        vertices (List[BMVert]): Vertices to triangulate in order as connected by edges
        accessEdge (Tuple[int, int]): Access edge
        accessTriangleVertex (Union[BMVert, None]): Access triangle vertex if requiresAccessTriangle is set to True

    Returns:
        List[Tuple[int,int,int]]: List of tuples, denoting indices of vertices creating a new triangulated faces
    """

    if len(vertices) < 3:
        return []

    if len(vertices) == 3:
        third = 0   # non accessEdge vertex
        if not 1 in accessEdge:
            third = 1
        elif not 2 in accessEdge:
            third = 2
        return [(*accessEdge, third)]

    # find a vertex, that creates a new face with the access edge
    _, vertex = calculateCost(tuple(vertices), accessEdge, proxy(accessTriangleVertex))

    result = [(*accessEdge, vertex)]

    # results of triangulation of connected domains
    tmpRes1 = triangulationFn([vertices[vertex]]+vertices[1:vertex], (0, 1), proxy(vertices[0]))
    tmpRes2 = triangulationFn([vertices[0]] + vertices[vertex:], (0, 1), proxy(vertices[1]))

    # correct vertex indices for the current domain
    for v1, v2, v3 in tmpRes1:
        if v1 == 0:
            v1 += vertex
        result.append((v1, v2, v3))

    # correct vertex indices for the current domain
    for v1, v2, v3 in tmpRes2:
        if v1 != 0:
            v1 += vertex - 1
        result.append((v1, v2+vertex-1, v3+vertex-1))

    return result


def triangulate(vertices: List[BMVert], strategy: Strategy) -> List[Tuple[int, int, int]]:
    """Dispatch function for the triangulationn

    Args:
        vertices (List[BMVert]): Vertices to triangluate in edge-connected order
        strategy (Strategy): Triangulation strategy

    Returns:
        List[Tuple[int,int,int]]: List of tuples, denoting indices of vertices creating a new triangulated faces
    """
    global costFn, requiresAccessTriangle

    # set required strategy
    if strategy == Strategy.DELAUNAY:
        costFn = costFunctionDeLaunay
        requiresAccessTriangle = False
    elif strategy == Strategy.MINIMUM_AREA:
        costFn = costFunctionMinimumArea
        requiresAccessTriangle = False
    elif strategy == Strategy.DELAUNAY_DIHEDRAL_MAX:
        costFn = costFunctionDihedralMax
        requiresAccessTriangle = True
    elif strategy == Strategy.DELAUNAY_DIHEDRAL_MIN:
        costFn = costFunctionDihedralMin
        requiresAccessTriangle = True

    # execute triangulation
    return triangulationFn(vertices, (0, 1), None)
