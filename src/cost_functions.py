"""
=========================================================================
Brief: Implementation of triangulation cost functions
Authors:
    Marek Mudroň (xmudro04)
    Matej Kunda  (xkunda00)
    Samuel Repka (xrepka07)
File: cost_functions.py
Date: April 2023
=========================================================================
"""

from bmesh.types import BMVert
from mathutils import Vector
from typing import Union


PI = 3.14159265358979


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


def costFunctionDihedralMax(v1: BMVert, v2: BMVert, v3: BMVert, v4: Union[BMVert, None]) -> float:
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


def costFunctionDihedralMin(v1: BMVert, v2: BMVert, v3: BMVert, v4: Union[BMVert, None]) -> float:
    """Cost function for optimization goal of minimal dihedral angles

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

    return angle4
