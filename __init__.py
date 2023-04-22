import bpy

from .src.operators import *
from .src.panel import AddonPanel

bl_info = {
    "name": "VGE Addon",
    "description": "Addon for VGE",
    "author": "VGE team",
    "blender": (2, 80, 0),
    "version": (1, 0, 0),
    "category": "Object",
    "location": "View3D > UI > VGElocation",
}

classes = (ObjectMoveX, TestOperator, AddonPanel)

def menu_func(self, context):
    self.layout.operator(ObjectMoveX.bl_idname)


def register():
    for c in classes:
        bpy.utils.register_class(c)

    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)

    bpy.types.VIEW3D_MT_object.remove(menu_func)  # Removes the new operator to an existing menu.


if __name__ == "__main__":

    register()
