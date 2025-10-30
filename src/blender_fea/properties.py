import bpy
from bpy.types import PropertyGroup
from bpy.props import StringProperty, FloatProperty, CollectionProperty, IntProperty, EnumProperty

# Define ALL PropertyGroup classes first
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
    section_name: StringProperty(name="Section")

class StructuralShell(PropertyGroup):
    name: StringProperty(name="Shell Name")
    point_list: StringProperty(name="Points (comma separated)")
    thickness: FloatProperty(name="Thickness", default=0.05, min=0.0)

class StructuralSection(PropertyGroup):
    name: StringProperty(name="Section Name")
    section_type: EnumProperty(
        name="Section Type",
        items=[
            ('CIRCULAR', "Circular", "Circular cross-section"),
            ('RECTANGULAR', "Rectangular", "Rectangular cross-section"),
            ('POLYGONAL', "Polygonal", "Polygonal cross-section"),
        ],
        default='CIRCULAR'
    )
    diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)
    width: FloatProperty(name="Width", default=0.1, min=0.01)
    height: FloatProperty(name="Height", default=0.15, min=0.01)
    sides: IntProperty(name="Sides", default=6, min=3, max=12)
    poly_diameter: FloatProperty(name="Diameter", default=0.1, min=0.01)

class StructuralProperties(PropertyGroup):
    points: CollectionProperty(type=StructuralPoint)
    beams: CollectionProperty(type=StructuralBeam)
    shells: CollectionProperty(type=StructuralShell)
    sections: CollectionProperty(type=StructuralSection)
    
    active_point_index: IntProperty(default=0)
    active_beam_index: IntProperty(default=0)
    active_shell_index: IntProperty(default=0)
    active_section_index: IntProperty(default=0)

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
    bpy.types.Scene.structural_data = bpy.props.PointerProperty(type=StructuralProperties)

def unregister():
    from bpy.utils import unregister_class
    
    # Remove scene property first
    if hasattr(bpy.types.Scene, 'structural_data'):
        del bpy.types.Scene.structural_data
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        unregister_class(cls)
