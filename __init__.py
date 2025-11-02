"""
BlenderFEA (blender-fea)

Program Structure:

__init__.py register()
    → operators.register() 
        → Registers all operator classes in operators.py
    → panels.register()
        → Registers all panel classes in panels.py  
    → properties.register()
        → Registers all property classes


For Future Development:
New operators: Add to operators.py - they'll auto-register
New panels: Add to panels.py and include in the classes tuple
New properties: Add to properties.py and include in the classes tuple
"""

bl_info = {
    "name": "BlenderFEA",
    "author": "Andrew Mole",
    "version": (0, 1, 1),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > BlenderFEA",
    "description": "Create, view and manage structural FEA models",
    "category": "3D View",
    "support": "COMMUNITY",
}

from pathlib import Path
from sys import path as sys_path
import time
from datetime import datetime


import bpy
from .src.blender_fea import operators, panels, properties, utils

# Module loading system
modules = (properties, operators, panels)

def register():
    import logging
    
    # Set up logging once in the main registration
    log = logging.getLogger('blenderfea')
    log.setLevel(logging.INFO)
    
    # Only add handler if it doesn't exist
    if not log.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.info(f"BlenderFEA v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]} starting registration")
    
    for module in modules:
        if hasattr(module, 'register'):
            module.register()
    
    log.info("BlenderFEA registration completed")

def unregister():
    for module in reversed(modules):
        if hasattr(module, 'unregister'):
            module.unregister()

if __name__ == "__main__":
    register()
