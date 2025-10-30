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
    'in': {'name': 'inches', 'type': 'length', 'scale': 0.0254},
    'ft': {'name': 'feet', 'type': 'length', 'scale': 0.3048},

    'lb': {'name': 'pounds', 'type': 'mass', 'scale': 0.453592},
    'g': {'name': 'grams', 'type': 'mass', 'scale': 0.001},
    'kg': {'name': 'kilograms', 'type': 'mass', 'scale': 1.0},
    't': {'name': 'tonnes', 'type': 'mass', 'scale': 1000.0},
    'tonne': {'name': 'tonnes', 'type': 'mass', 'scale': 1000.0},
    'ton': {'name': 'short tons', 'type': 'mass', 'scale': 907.185},

    'lbf': {'name': 'pounds-force', 'type': 'force', 'scale': 4.44822},
    'N': {'name': 'newtons', 'type': 'force', 'scale': 1.0},

    'Pa': {'name': 'pascals', 'type': 'pressure', 'scale': 1.0},
    'kPa': {'name': 'pascals', 'type': 'pressure', 'scale': 1000.0},
    'MPa': {'name': 'pascals', 'type': 'pressure', 'scale': 1000000.0},
    'psi': {'name': 'pounds per square inch', 'type': 'pressure', 'scale': 6894.75729},
    'ksi': {'name': 'pounds per square inch', 'type': 'pressure', 'scale': 6894757.29},
    'bar': {'name': 'bar', 'type': 'pressure', 'scale': 100000.0},
    'atm': {'name': 'atmospheres', 'type': 'pressure', 'scale': 101325.0},

    'm2': {'name': 'square metres', 'type': 'area', 'scale': 1.0},
    'in2': {'name': 'square inches', 'type': 'area', 'scale': 0.00064516},
    'ft2': {'name': 'square feet', 'type': 'area', 'scale': 0.092903},

    'm3': {'name': 'cubic metres', 'type': 'volume', 'scale': 1.0},
    'in3': {'name': 'cubic inches', 'type': 'volume', 'scale': 1.6387e-05},
    'L': {'name': 'litres', 'type': 'volume', 'scale': 0.001},

    'deg': {'name': 'degrees', 'type': 'angle', 'scale': math.pi / 180.0},
    'rad': {'name': 'radians', 'type': 'angle', 'scale': 1.0},

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
    bpy.context.scene.collection.children.link(structural_collection)
    
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
    """Create beam geometry from beam data"""
    start_coords = get_point_coordinates(beam.start_point, structural_data)
    end_coords = get_point_coordinates(beam.end_point, structural_data)
    
    if not start_coords or not end_coords:
        return None
    
    # Calculate beam properties
    distance = (end_coords - start_coords).length
    center = (start_coords + end_coords) / 2
    
    # Create cylinder with modern context handling
    with bpy.context.temp_override(**bpy.context.copy()):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8,
            radius=beam.diameter/2,
            depth=distance,
            location=center
        )
    
    beam_obj = bpy.context.active_object
    beam_obj.name = beam.name
    
    # Rotate to align with points
    direction = end_coords - start_coords
    beam_obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    
    # Move to Structural Model collection
    move_to_structural_collection(beam_obj)

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