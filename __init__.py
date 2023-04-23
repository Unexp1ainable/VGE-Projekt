import bpy

from .src.operators import *
from .src.panel import AddonPanel, PlaceholderProperties
from bpy.types import Panel, PropertyGroup, Scene, WindowManager
from bpy.utils import register_class

from bpy.props import (
    IntProperty,
    EnumProperty,
    StringProperty,
    PointerProperty,
)

bl_info = {
    "name": "VGE Addon",
    "description": "Addon for VGE",
    "author": "VGE team",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "category": "Object",
    "location": "View3D > UI > VGElocation",
}

classes = (TestOperator, AddonPanel, PlaceholderProperties)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    Scene.placeholder = PointerProperty(type=PlaceholderProperties)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del Scene.placeholder
    


if __name__ == "__main__":

    register()
