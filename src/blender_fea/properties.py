import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, CollectionProperty, IntProperty

class StructuralPoint(PropertyGroup):
    name: StringProperty(name="Point Name")
    x: FloatProperty(name="X", default=0.0)
    y: FloatProperty(name="Y", default=0.0)
    z: FloatProperty(name="Z", default=0.0)

class StructuralBeam(PropertyGroup):
    name: StringProperty(name="Beam Name")
    start_point: StringProperty(name="Start Point")
    end_point: StringProperty(name="End Point")
    diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)

class StructuralShell(PropertyGroup):
    name: StringProperty(name="Shell Name")
    point_list: StringProperty(name="Points (comma separated)")
    thickness: FloatProperty(name="Thickness", default=0.05, min=0.0)

class StructuralProperties(PropertyGroup):
    points: CollectionProperty(type=StructuralPoint)
    beams: CollectionProperty(type=StructuralBeam)
    shells: CollectionProperty(type=StructuralShell)
    active_point_index: IntProperty(default=0)
    active_beam_index: IntProperty(default=0)
    active_shell_index: IntProperty(default=0)

# Registration
classes = (
    StructuralPoint,
    StructuralBeam,
    StructuralShell,
    StructuralProperties,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    bpy.types.Scene.structural_data = bpy.props.PointerProperty(type=StructuralProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    
    del bpy.types.Scene.structural_data