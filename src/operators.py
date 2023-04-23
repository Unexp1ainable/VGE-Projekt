from typing import List
import bpy
import bmesh
from bmesh.types import BMVert, BMEdge
from bpy.types import Operator
from .alg import *

class ObjectMoveX(Operator):
    """My Object Moving Script"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.move_x"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Move X by One"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    def execute(self, context):        # execute() is called when running the operator.

        # The original script
        scene = context.scene
        for obj in scene.objects:
            obj.location.x += 1.0

        return {'FINISHED'}            # Lets Blender know the operator finished successfully.
    
class TestOperator(Operator):
    bl_idname = "object.test_operator"
    bl_label = "Test"
    bl_options = {'REGISTER', 'UNDO'}

    def sortEdgeLoop(self, selected: List[BMEdge]):
        if len(selected) < 3:
            raise Exception("At least 3 edges must be selected")

        firstEdge = selected[0]
        connectedOrder = list(firstEdge.verts).copy()
        currVert = connectedOrder[1]
        currEdge = firstEdge
        selected = selected[1:]
        isFirstEdge = True # only one vertex is processed when processing first edge

        while selected:
            atLeastOneEdgeFound = False
            vert : BMVert
            shouldEnd = False
            for vert in currEdge.verts:
                if vert != currVert:
                    continue
                
                for edge in vert.link_edges:
                    if edge != currEdge:
                        if edge in selected:
                            if shouldEnd:
                                raise Exception("More than 2 edges connected to the selected vertex")
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
                raise Exception("Selected edges do not form edge loop")

        # check first-last connectivity
        if connectedOrder[0] != connectedOrder[-1]:
            raise Exception("Selected edges do not form a closed loop")
        connectedOrder = connectedOrder[:-1]
        
        return connectedOrder

        
    def execute(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)
        selected = []
        for edge in mesh.edges:
            edge : BMEdge
            if edge.select:
                selected.append(edge)

        try:
            sortedVertexLoop = self.sortEdgeLoop(selected)
            newFaces = triangulate(sortedVertexLoop, (0,1))
            for v1,v2,v3 in newFaces:
                mesh.faces.new((sortedVertexLoop[v1], sortedVertexLoop[v2], sortedVertexLoop[v3]))
        except Exception as e:
            self.report({"ERROR"}, str(e))

        bmesh.update_edit_mesh(context.object.data)
        # only way to update 3DView I found
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}
