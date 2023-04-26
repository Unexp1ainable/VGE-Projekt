import bpy
from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.utils import register_class
from .alg import Strategy

from bpy.props import (
    IntProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)

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
        row.label(text="Optimization strategy")
        row = layout.row()
        placeholder = context.scene.placeholder
        row.prop(placeholder, "dropdown_box", text="")
        row = layout.row()
        row.operator("object.test_operator", text="Test operator")



class PlaceholderProperties(PropertyGroup):
    dropdown_box: EnumProperty(
        items=(
            (Strategy.DELAUNAY.name, "DeLaunay", "Enforce DeLaunay triangles"),
            (Strategy.MINIMUM_AREA.name, "Minimum area", "Minimize surface area of triangles"),
            (Strategy.DELAUNAY_DIHEDRAL.name, "Max dihedral angle", "Optimize for maximal dihedral angle"),
        ),
        name="Optimization strategy",
        default=Strategy.DELAUNAY.name,
        description="Select triangulation strategy",
    )
