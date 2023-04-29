"""
=========================================================================
Brief: Initialization of the blender addon for VGE project
Authors:
    Marek Mudroň (xmudro04)
    Matej Kunda  (xkunda00)
    Samuel Repka (xrepka07)
File: __init__.py
Date: April 2023
=========================================================================
"""

from .src.operators import *
from .src.panel import AddonPanel, CostFunctionDropdownProperties

import bpy
from bpy.types import Scene
from bpy.props import PointerProperty

bl_info = {
    "name": "VGE Addon",
    "description": "Addon for VGE project",
    "author": "VGE team",
    "blender": (3, 0, 0),
    "version": (1, 0, 0),
    "category": "Object",
    "location": "View3D > SidePanel > VGE Addon",
}

classes = (TriangulationOperator, AddonPanel, CostFunctionDropdownProperties)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    Scene.costFunctionDropdownProperties = PointerProperty(type=CostFunctionDropdownProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del Scene.costFunctionDropdownProperties


if __name__ == "__main__":
    register()
