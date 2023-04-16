import bpy
import bmesh
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


    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        
        mesh = bmesh.from_edit_mesh(context.object.data)
        for vert in mesh.verts:
            print(vert)
            vert.co.x += 1
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
