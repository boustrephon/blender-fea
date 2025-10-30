import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, CollectionProperty, IntProperty, EnumProperty

# Define ALL PropertyGroup classes first
class StructuralPoint(PropertyGroup):
    name: StringProperty(name="Point Name")    # type: ignore
    x: FloatProperty(name="X", default=0.0)    # type: ignore
    y: FloatProperty(name="Y", default=0.0)    # type: ignore
    z: FloatProperty(name="Z", default=0.0)    # type: ignore

class StructuralBeam(PropertyGroup):
    name: StringProperty(name="Beam Name")    # type: ignore
    start_point: StringProperty(name="Start Point")    # type: ignore
    end_point: StringProperty(name="End Point")    # type: ignore
    diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)    # type: ignore
    section_name: StringProperty(name="Section")    # type: ignore

class StructuralShell(PropertyGroup):
    name: StringProperty(name="Shell Name")    # type: ignore
    point_list: StringProperty(name="Points (comma separated)")    # type: ignore
    thickness: FloatProperty(name="Thickness", default=0.05, min=0.0)    # type: ignore

class StructuralSection(PropertyGroup):
    name: StringProperty(name="Section Name")    # type: ignore
    section_type: EnumProperty(    # type: ignore
        name="Section Type",
        items=[
            ('CIRCULAR', "Circular", "Circular cross-section"),
            ('RECTANGULAR', "Rectangular", "Rectangular cross-section"),
            ('POLYGONAL', "Polygonal", "Polygonal cross-section"),
        ],
        default='CIRCULAR'
    )
    diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)    # type: ignore
    width: FloatProperty(name="Width", default=0.1, min=0.01)    # type: ignore
    height: FloatProperty(name="Height", default=0.15, min=0.01)    # type: ignore
    sides: IntProperty(name="Sides", default=6, min=3, max=12)    # type: ignore
    poly_diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)    # type: ignore

class StructuralProperties(PropertyGroup):
    points: CollectionProperty(type=StructuralPoint)    # type: ignore
    beams: CollectionProperty(type=StructuralBeam)    # type: ignore
    shells: CollectionProperty(type=StructuralShell)    # type: ignore
    sections: CollectionProperty(type=StructuralSection)    # type: ignore
    
    active_point_index: IntProperty(default=0)    # type: ignore
    active_beam_index: IntProperty(default=0)    # type: ignore
    active_shell_index: IntProperty(default=0)    # type: ignore
    active_section_index: IntProperty(default=0)    # type: ignore

# Collect ALL classes for registration
classes = (
    StructuralPoint,
    StructuralBeam,
    StructuralShell,
    StructuralSection,  # Must be registered before StructuralProperties
    StructuralProperties,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
        print(f"BlenderFEA - Registered property class: {cls.__name__}")
    
    # Register scene property AFTER all classes are registered
    bpy.types.Scene.structural_data = bpy.props.PointerProperty(type=StructuralProperties)    # type: ignore

def unregister():
    from bpy.utils import unregister_class
    
    # Remove scene property first
    if hasattr(bpy.types.Scene, 'structural_data'):
        del bpy.types.Scene.structural_data    # type: ignore
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        unregister_class(cls)
