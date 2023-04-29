"""
=========================================================================
Brief: Implementation of the blender operator
Authors:
    Marek Mudroň (xmudro04)
    Matej Kunda  (xkunda00)
    Samuel Repka (xrepka07)
File: operators.py
Date: April 2023
=========================================================================
"""

from .alg import *

from typing import List

import bpy
import bmesh
from bpy.types import Operator
from bmesh.types import BMVert, BMEdge


class TriangulationOperator(Operator):
    bl_idname = "object.triangulation_operator"
    bl_label = "TriangulationOperator"
    bl_options = {'REGISTER', 'UNDO'}

    def sortEdgeLoop(self, selected: List[BMEdge]) -> List[BMVert]:
        """Check if the edges form a loop and return its vertices in connected order.

        Args:
            selected (List[BMEdge]): List of edges

        Raises:
            VGEException: If some condition is not satisfied

        Returns:
            List[BMVert]: List of ordered vertices
        """

        if len(selected) < 3:
            raise VGEException("At least 3 edges must be selected")

        firstEdge = selected[0]
        connectedOrder = list(firstEdge.verts).copy()
        currVert = connectedOrder[1]
        currEdge = firstEdge
        selected = selected[1:]
        isFirstEdge = True  # only one vertex is processed when processing first edge

        while selected:
            atLeastOneEdgeFound = False
            shouldEnd = False
            vert: BMVert
            for vert in currEdge.verts:
                if vert != currVert:
                    continue

                for edge in vert.link_edges:
                    if edge != currEdge and edge in selected:
                        if shouldEnd:
                            raise VGEException("More than 2 edges connected to the selected vertex")

                        currVert = edge.verts[0] if edge.verts[0] != vert else edge.verts[1]
                        connectedOrder.append(currVert)
                        currEdge = edge
                        selected.remove(currEdge)
                        shouldEnd = True
                        atLeastOneEdgeFound = True

                # only one vertex is processed when processing first edge
                if isFirstEdge:
                    isFirstEdge = False
                    break

            if not atLeastOneEdgeFound:
                raise VGEException("Selected edges do not form an edge loop")

        # check first-last connectivity
        if connectedOrder[0] != connectedOrder[-1]:
            raise VGEException("Selected edges do not form a closed loop")
        connectedOrder = connectedOrder[:-1]

        return connectedOrder

    def execute(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)

        # extract selected edges
        selected = []
        for edge in mesh.edges:
            edge: BMEdge
            if edge.select:
                selected.append(edge)

        try:
            # check and sort
            sortedVertices = self.sortEdgeLoop(selected)
            # acquire triangulated faces
            newFaces = triangulate(sortedVertices, Strategy[context.scene.costFunctionDropdownProperties.dropdown_box])
            # create new faces
            for v1, v2, v3 in newFaces:
                mesh.faces.new((sortedVertices[v1], sortedVertices[v2], sortedVertices[v3]))
        except VGEException as e:
            self.report({"ERROR"}, str(e))

        bmesh.update_edit_mesh(context.object.data)

        # only way to update 3DView I found
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}
