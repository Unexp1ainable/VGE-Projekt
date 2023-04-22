import bpy

from bpy.types import Panel

class AddonPanel(Panel):
    bl_idname = "VGE_PT_TestPanel"
    bl_label = "VGE Addon"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "VGE Addon"
    bl_context = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="How cool is this!")
        row = layout.row()
        row.operator("object.move_x", text="Object move X")
        row = layout.row()
        row.operator("object.test_operator", text="Test operator")

