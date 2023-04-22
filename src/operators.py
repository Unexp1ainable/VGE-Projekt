from typing import List
import bpy
import bmesh
from bmesh.types import BMVert, BMEdge
from bpy.types import Operator

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
        connectedOrder = [firstEdge]
        currEdge = firstEdge
        selected = selected[1:]
        isFirstEdge = True # only one vertex is processed when processing first edge

        while selected:
            vert : BMVert
            atLeastOneEdgeFound = False
            for vert in currEdge.verts:
                shouldEnd = False
                for edge in vert.link_edges:
                    if edge != currEdge:
                        if edge in selected:
                            if shouldEnd:
                                raise Exception("More than 2 edges connected to the selected vertex")
                            connectedOrder.append(edge)
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
        last = connectedOrder[-1]
        isClosed = False
        for vertex in firstEdge.verts:
            for edge in vertex.link_edges:
                if edge == last:
                    isClosed = True
                    break

        if not isClosed:
            raise Exception("Selected edges do not form a closed loop")
        
        return connectedOrder

        
    def execute(self, context):
        mesh = bmesh.from_edit_mesh(context.object.data)
        selected = []
        for edge in mesh.edges:
            edge : BMEdge
            if edge.select:
                selected.append(edge)

        sortedEdgeLoop = self.sortEdgeLoop(selected)

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}
