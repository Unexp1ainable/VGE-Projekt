"""
=========================================================================
Brief: Blender GUI panel for VGE project
Authors:
    Marek Mudroň (xmudro04)
    Matej Kunda  (xkunda00)
    Samuel Repka (xrepka07)
File: panel.py
Date: April 2023
=========================================================================
"""

from bpy.types import Panel, PropertyGroup
from bpy.props import EnumProperty

from .alg import Strategy


class AddonPanel(Panel):
    """Gui panel
    """

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
        placeholder = context.scene.costFunctionDropdownProperties
        row.prop(placeholder, "dropdown_box", text="")
        row = layout.row()
        row.operator("object.triangulation_operator", text="Test operator")


class CostFunctionDropdownProperties(PropertyGroup):
    """Contents of the dropdown box with triangulation strategies
    """

    dropdown_box: EnumProperty(
        items=(
            (Strategy.DELAUNAY.name, "DeLaunay", "Enforce DeLaunay triangles"),
            (Strategy.MINIMUM_AREA.name, "Minimum area", "Minimize surface area of triangles"),
            (Strategy.DELAUNAY_DIHEDRAL_MAX.name, "Max dihedral angle", "Optimize for maximal dihedral angle"),
            (Strategy.DELAUNAY_DIHEDRAL_MIN.name, "Min dihedral angle", "Optimize for minimal dihedral angle"),
        ),
        name="Optimization strategy",
        default=Strategy.DELAUNAY.name,
        description="Select triangulation strategy",
    )
