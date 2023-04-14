import bpy


bl_info = {
    "name": "Test Addon",
    "description": "Addon for testing",
    "author": "Tester",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "category": "Test",
    "location": "View3D > UI > Unity Batch FBX Export",
}


class TESTADDON_PT_TestPanel(bpy.types.Panel):
    bl_idname = "TESTADDON_PT_TestPanel"
    bl_label = "Test Addon"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Test Addon"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="How cool is this!")
        row = layout.row()
        row.label(text="Mighty cool!")
        row = layout.row()
        row.label(text="CCCCCCCCCCCCCCCCC!")


class ObjectMoveX(bpy.types.Operator):
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


def menu_func(self, context):
    self.layout.operator(ObjectMoveX.bl_idname)


def register():
    bpy.utils.register_class(TESTADDON_PT_TestPanel)
    bpy.utils.register_class(ObjectMoveX)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.


def unregister():
    bpy.utils.unregister_class(ObjectMoveX)
    bpy.utils.unregister_class(TESTADDON_PT_TestPanel)
    bpy.types.VIEW3D_MT_object.remove(menu_func)  # Removes the new operator to an existing menu.


if __name__ == "__main__":

    register()
