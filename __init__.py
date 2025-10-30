bl_info = {
    "name": "BlenderFEA",
    "author": "Andrew Mole",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > BlenderFEA",
    "description": "Create, view and manage structural FEA models",
    "category": "3D View",
    "support": "COMMUNITY",
}

import bpy
from .src.blender_fea import operators, panels, properties, utils

# Module loading system
modules = (properties, operators, panels)

def register():
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

def unregister():
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()

if __name__ == "__main__":
    register()
