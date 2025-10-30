import math
import bpy
import bmesh
from mathutils import Vector

from . import DEFAULT_UNITS

# scale is the factor that needs to be applied to the value 
# to convert it to the default unit
UNITS_DICT = {
    's': {'name': 'seconds', 'type': 'time', 'scale': 1.0},
    'min': {'name': 'minutes', 'type': 'time', 'scale': 60.0},
    'hour': {'name': 'hours', 'type': 'time', 'scale': 3600.0},

    'm': {'name': 'metres', 'type': 'length', 'scale': 1.0},
    'cm': {'name': 'centimetres', 'type': 'length', 'scale': 0.01},
    'in': {'name': 'inches', 'type': 'length', 'scale': 0.0254},
    'ft': {'name': 'feet', 'type': 'length', 'scale': 0.3048},

    'm/s': {'name': 'metres per second', 'type': 'velocity', 'scale': 1.0},
    'kph': {'name': 'kilometres per hour', 'type': 'velocity', 'scale': 3.6},
    'in/s': {'name': 'inches per second', 'type': 'velocity', 'scale': 0.0254},
    'ft/s': {'name': 'feet per second', 'type': 'velocity', 'scale': 0.3048},

    'm/s2': {'name': 'metres per second squared', 'type': 'acceleration', 'scale': 1.0},
    'g': {'name': 'gravity', 'type': 'acceleration', 'scale': 9.81},
    'gal': {'name': 'cm per second squared', 'type': 'acceleration', 'scale': 0.01},
    'in/s2': {'name': 'inches per second squared', 'type': 'acceleration', 'scale': 0.0254},
    'ft/s2': {'name': 'feet per second squared', 'type': 'acceleration', 'scale': 0.3048},

    'lb': {'name': 'pounds', 'type': 'mass', 'scale': 0.45359237},
    'lbm': {'name': 'pounds', 'type': 'mass', 'scale': 0.45359237},
    'kip': {'name': 'kilopound', 'type': 'mass', 'scale': 453.59237},
    'g': {'name': 'grams', 'type': 'mass', 'scale': 0.001},
    'kg': {'name': 'kilograms', 'type': 'mass', 'scale': 1.0},
    't': {'name': 'tonnes', 'type': 'mass', 'scale': 1000.0},
    'tonne': {'name': 'tonnes', 'type': 'mass', 'scale': 1000.0},
    'ton': {'name': 'short tons', 'type': 'mass', 'scale': 907.185},

    'Nm': {'name': 'newton metres', 'type': 'moment', 'scale': 1.0},
    'kNm': {'name': 'kilonewton metres', 'type': 'moment', 'scale': 1000.0},
    'MNm': {'name': 'Meganewton metres', 'type': 'moment', 'scale': 1000000.0},
    'kip-in': {'name': 'kip-in', 'type': 'moment', 'scale': 112.985},
    'kip-ft': {'name': 'kip-ft', 'type': 'moment', 'scale': 1355.82},

    'N': {'name': 'newtons', 'type': 'force', 'scale': 1.0},
    'kN': {'name': 'newtons', 'type': 'force', 'scale': 1000.0},
    'MN': {'name': 'newtons', 'type': 'force', 'scale': 1000000.0},
    'kgf': {'name': 'kilograms-force', 'type': 'force', 'scale': 9.80665},
    'lbf': {'name': 'pounds-force', 'type': 'force', 'scale': 4.44822},
    'tonf': {'name': 'ton-force', 'type': 'force', 'scale': 8896.443230521},
    'kipf': {'name': 'pounds-force', 'type': 'force', 'scale': 4448.22},
    'dyna': {'name': 'dynes', 'type': 'force', 'scale': 0.00001},

    'kN/m': {'name': 'kilonewtons per metre', 'type': 'force', 'scale': 1.0},
    'plf': {'name': 'pounds per linear foot', 'type': 'line load', 'scale': 14.5939},


    'Pa': {'name': 'pascals', 'type': 'pressure', 'scale': 1.0},
    'kPa': {'name': 'pascals', 'type': 'pressure', 'scale': 1000.0},
    'MPa': {'name': 'pascals', 'type': 'pressure', 'scale': 1000000.0},
    'psi': {'name': 'pounds per square inch', 'type': 'pressure', 'scale': 6894.75729},
    'ksi': {'name': 'pounds per square inch', 'type': 'pressure', 'scale': 6894757.29},
    'bar': {'name': 'bar', 'type': 'pressure', 'scale': 100000.0},
    'kgf/cm2': {'name': 'kilograms force per square centimetre', 'type': 'pressure', 'scale': 98066.5},
    'ksc': {'name': 'kilograms force per square centimetre', 'type': 'pressure', 'scale': 98066.5},
    'atm': {'name': 'atmospheres', 'type': 'pressure', 'scale': 101325.0},

    'N/m3': {'name': 'newtons per cubic metre', 'type': 'density', 'scale': 1.0},
    'kg/m3': {'name': 'kilograms per cubic metre', 'type': 'mass density', 'scale': 1.0},
    'kN/m3': {'name': 'kilonewtons per cubic metre', 'type': 'density', 'scale': 1000.0},
    'pci': {'name': 'pounds per cubic inch', 'type': 'density', 'scale': 271447.0},
    'pcf': {'name': 'pounds per cubic foot', 'type': 'density', 'scale': 157.09},

    'm2': {'name': 'square metres', 'type': 'area', 'scale': 1.0},
    'in2': {'name': 'square inches', 'type': 'area', 'scale': 0.00064516},
    'ft2': {'name': 'square feet', 'type': 'area', 'scale': 0.092903},

    'm3': {'name': 'cubic metres', 'type': 'volume', 'scale': 1.0},
    'in3': {'name': 'cubic inches', 'type': 'volume', 'scale': 1.6387e-05},
    'L': {'name': 'litres', 'type': 'volume', 'scale': 0.001},

    'deg': {'name': 'degrees', 'type': 'angle', 'scale': math.pi / 180.0},
    'rad': {'name': 'radians', 'type': 'angle', 'scale': 1.0},
    'rpm': {'name': 'revolutions per minute', 'type': 'angular velocity', 'scale': math.pi / 30.0},

    'C': {'name': 'Celsius', 'type': 'temperature', 'scale': 1.0, 'offset': 273.15},  # Special case
    'K': {'name': 'Kelvin', 'type': 'temperature', 'scale': 1.0},
    'F':  {'name': 'Fahrenheit', 'type': 'temperature', 'scale': 5/9, 'offset': 459.67}, # Special case,
    'R': {'name': 'Rankine', 'type': 'temperature', 'scale': 5/9}
}

def convert_units(value, from_unit, to_unit, units_dict):
    if from_unit not in units_dict or to_unit not in units_dict:
        if from_unit not in units_dict and to_unit not in units_dict:
            raise ValueError(f'Invalid units: {from_unit} and {to_unit}')
        elif from_unit not in units_dict:
            raise ValueError(f'Invalid unit: {from_unit}')
        else:
            raise ValueError(f'Invalid unit: {to_unit}')
    elif from_unit == to_unit:
        return value
    elif units_dict[from_unit]['type'] != units_dict[to_unit]['type']:
        raise ValueError("Cannot convert between different unit types")
    else:
        # Convert to default unit first
        if 'offset' in units_dict[from_unit]:
            default_value = (value + units_dict[from_unit]['offset']) * units_dict[from_unit]['scale']
        else:
            default_value = value / units_dict[from_unit]['scale']

        # Convert from default unit to the target unit
        if 'offset' in units_dict[to_unit]:
            result = (default_value - units_dict[to_unit]['offset']) / units_dict[to_unit]['scale']
        else:
            result = default_value * units_dict[to_unit]['scale']

        return result

def get_point_coordinates(point_name, structural_data):
    """Get coordinates for a point by name"""
    for point in structural_data.points:
        if point.name == point_name:
            return Vector((point.x, point.y, point.z))
    return None

def ensure_structural_collection():
    """Ensure Structural Model collection exists and return it"""
    collection_name = "Structural Model"
    
    # Check if collection already exists
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    
    # Create new collection
    structural_collection = bpy.data.collections.new(collection_name)
    
    # Link to scene collection
    bpy.context.scene.collection.children.link(structural_collection)   # type: ignore
    
    print(f"Created collection: {collection_name}")
    return structural_collection

def move_to_structural_collection(obj):
    """Move object to Structural Model collection and remove from others"""
    structural_collection = ensure_structural_collection()
    
    # Remove from all current collections
    for collection in obj.users_collection:
        collection.objects.unlink(obj)
    
    # Add to structural collection
    structural_collection.objects.link(obj)
    
    return obj

def create_beam_from_data(beam, structural_data):
    """Create beam geometry from beam data with section properties"""
    start_coords = get_point_coordinates(beam.start_point, structural_data)
    end_coords = get_point_coordinates(beam.end_point, structural_data)
    
    if not start_coords or not end_coords:
        return None
    
    # Calculate beam properties
    distance = (end_coords - start_coords).length
    center = (start_coords + end_coords) / 2
    
    # Get section properties
    section = get_section_by_name(beam.section_name, structural_data)
    
    if not section:
        # Fallback to circular with diameter
        section_type = 'CIRCULAR'
        size1 = beam.diameter
        size2 = beam.diameter
        sides = 8
    else:
        section_type = section.section_type
        if section_type == 'CIRCULAR':
            size1 = section.diameter
            size2 = section.diameter
            sides = 8
        elif section_type == 'RECTANGULAR':
            size1 = section.width
            size2 = section.height
            sides = 4
        elif section_type == 'POLYGONAL':
            size1 = section.poly_diameter
            size2 = section.poly_diameter
            sides = section.sides
    
    # Create beam based on section type
    if section_type == 'RECTANGULAR':
        beam_obj = create_rectangular_beam(center, start_coords, end_coords, size1, size2, distance)
    else:
        # Circular or Polygonal
        beam_obj = create_polygonal_beam(center, start_coords, end_coords, size1, sides, distance)
    
    beam_obj.name = beam.name   # type: ignore
    
    # Move to Structural Model collection
    move_to_structural_collection(beam_obj)
    
    return beam_obj

def get_section_by_name(section_name, structural_data):
    """Find section by name in structural data"""
    for section in structural_data.sections:
        if section.name == section_name:
            return section
    return None

def create_rectangular_beam(center, start_coords, end_coords, width, height, distance):
    """Create rectangular beam using cube primitive with correct orientation"""
    if bpy.context.copy() is None:
        raise ValueError("bpy.context.copy() is None")
    
    with bpy.context.temp_override(**bpy.context.copy()):    # type: ignore
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=center)
    
    beam_obj = bpy.context.active_object
    
    # Scale to rectangular cross-section
    # Note: X=width, Y=height, Z=length (distance)
    beam_obj.scale = (width/2, height/2, distance)   # type: ignore
    
    # Apply scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Rotate to align with points
    # We need to align the Z-axis (length) with the beam direction
    direction = (end_coords - start_coords).normalized()
    
    # Create rotation to point Z-axis along the beam direction
    beam_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()   # type: ignore
    
    return beam_obj

def create_polygonal_beam(center, start_coords, end_coords, diameter, sides, distance):
    """Create circular or polygonal beam using cylinder primitive with correct orientation"""
    with bpy.context.temp_override(**bpy.context.copy()):     # type: ignore
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=sides,
            radius=diameter/2,
            depth=distance,  # This should now be correct
            location=center
        )
    
    beam_obj = bpy.context.active_object
    
    # Rotate to align with points
    # The cylinder primitive creates with depth along Z-axis
    direction = (end_coords - start_coords).normalized()
    beam_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()   # type: ignore
    
    return beam_obj

def create_shell_from_data(shell, structural_data):
    """Create shell geometry from shell data and place in Structural Model collection"""
    point_names = [name.strip() for name in shell.point_list.split(",")]
    vertices = []
    
    for point_name in point_names:
        coords = get_point_coordinates(point_name, structural_data)
        if coords:
            vertices.append(coords)
    
    if len(vertices) < 3:
        return None
    
    # Create mesh and object
    mesh = bpy.data.meshes.new(shell.name)
    obj = bpy.data.objects.new(shell.name, mesh)
    
    # Move to Structural Model collection (instead of default collection)
    move_to_structural_collection(obj)
    
    # Create bmesh
    bm = bmesh.new()
    
    # Add vertices and create face
    bm_verts = [bm.verts.new(v) for v in vertices]
    
    try:
        face = bm.faces.new(bm_verts)
        bm.faces.ensure_lookup_table()
    except ValueError:
        print(f"Could not create face for shell {shell.name}")
        bm.free()
        return None
    
    # Extrude for thickness if specified
    if shell.thickness > 0:
        extruded = bmesh.ops.extrude_face_region(bm, geom=[face])
        bmesh.ops.translate(
            bm, 
            vec=face.normal * shell.thickness,
            verts=[v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
        )
    
    bm.to_mesh(mesh)
    bm.free()
    
    return obj



# No registration needed for utils - they're just helper functions