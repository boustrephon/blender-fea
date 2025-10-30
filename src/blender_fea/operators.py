import bpy
from bpy.types import Operator, UIList
from bpy.props import StringProperty
from . import utils
import json
import os
import logging
log = logging.getLogger(__name__) # logging added as example



class STRUCTURAL_OT_organize_collections(Operator):
    bl_idname = "structural.organize_collections"
    bl_label = "Organize into Collections"
    bl_description = "Move all structural objects to proper collections"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        # Ensure collection exists
        structural_collection = utils.ensure_structural_collection()
        
        # Move points
        for point in structural_data.points:
            if point.name in bpy.data.objects:
                obj = bpy.data.objects[point.name]
                utils.move_to_structural_collection(obj)
        
        # Move beams
        for beam in structural_data.beams:
            if beam.name in bpy.data.objects:
                obj = bpy.data.objects[beam.name]
                utils.move_to_structural_collection(obj)
        
        # Move shells
        for shell in structural_data.shells:
            if shell.name in bpy.data.objects:
                obj = bpy.data.objects[shell.name]
                utils.move_to_structural_collection(obj)
        
        self.report({'INFO'}, "All structural objects organized into collections")
        return {'FINISHED'}

class STRUCTURAL_OT_add_section(Operator):
    bl_idname = "structural.add_section"
    bl_label = "Add Section Profile"
    bl_description = "Add a new cross-section profile"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        section = structural_data.sections.add()
        section.name = f"Section_{len(structural_data.sections)}"
        section.section_type = 'CIRCULAR'
        section.diameter = 0.1
        section.width = 0.1
        section.height = 0.15
        section.sides = 6
        section.poly_diameter = 0.1
        
        self.report({'INFO'}, f"Added section: {section.name}")
        return {'FINISHED'}

class STRUCTURAL_OT_delete_section(Operator):
    bl_idname = "structural.delete_section"
    bl_label = "Delete Section"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.sections and structural_data.active_section_index >= 0:
            section = structural_data.sections[structural_data.active_section_index]
            
            # Check if any beams are using this section
            beams_using_section = []
            for beam in structural_data.beams:
                if beam.section_name == section.name:
                    beams_using_section.append(beam.name)
            
            if beams_using_section:
                self.report({'WARNING'}, f"Cannot delete: used by beams {beams_using_section}")
                return {'CANCELLED'}
            
            structural_data.sections.remove(structural_data.active_section_index)
            
            if structural_data.active_section_index >= len(structural_data.sections):
                structural_data.active_section_index = len(structural_data.sections) - 1
        
        return {'FINISHED'}

class STRUCTURAL_OT_add_point(Operator):
    bl_idname = "structural.add_point"
    bl_label = "Add Structural Point"
    bl_description = "Add a new structural point"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        point = structural_data.points.add()
        point.name = f"Point_{len(structural_data.points)}"
        point.x = 0.0
        point.y = 0.0
        point.z = 0.0
        
        # Create visual representation
        with bpy.context.temp_override(**bpy.context.copy()):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(point.x, point.y, point.z))
        sphere = context.active_object
        sphere.name = point.name
        
        # Move to Structural Model collection
        utils.move_to_structural_collection(sphere)

        self.report({'INFO'}, f"Added point: {point.name}")
        return {'FINISHED'}

class STRUCTURAL_OT_delete_point(Operator):
    bl_idname = "structural.delete_point"
    bl_label = "Delete Selected Point"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.points and structural_data.active_point_index >= 0:
            point = structural_data.points[structural_data.active_point_index]
            
            # Remove visual object
            if point.name in bpy.data.objects:
                obj = bpy.data.objects[point.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            # Remove from collection
            structural_data.points.remove(structural_data.active_point_index)
            
            # Adjust active index
            if structural_data.active_point_index >= len(structural_data.points):
                structural_data.active_point_index = len(structural_data.points) - 1
        
        return {'FINISHED'}

class STRUCTURAL_OT_update_point_position(Operator):
    bl_idname = "structural.update_point_position"
    bl_label = "Update Point Position"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.points and structural_data.active_point_index >= 0:
            point = structural_data.points[structural_data.active_point_index]
            
            # Update visual object position
            if point.name in bpy.data.objects:
                obj = bpy.data.objects[point.name]
                obj.location = (point.x, point.y, point.z)
        
        return {'FINISHED'}

class STRUCTURAL_OT_add_beam(Operator):
    bl_idname = "structural.add_beam"
    bl_label = "Add Structural Beam"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if len(structural_data.points) < 2:
            self.report({'ERROR'}, "Need at least 2 points to create a beam")
            return {'CANCELLED'}
        
        beam = structural_data.beams.add()
        beam.name = f"Beam_{len(structural_data.beams)}"
        beam.start_point = structural_data.points[0].name
        beam.end_point = structural_data.points[1].name
        
        # Create the beam geometry
        utils.create_beam_from_data(beam, structural_data)
        
        self.report({'INFO'}, f"Added beam: {beam.name}")
        return {'FINISHED'}

class STRUCTURAL_OT_delete_beam(Operator):
    bl_idname = "structural.delete_beam"
    bl_label = "Delete Selected Beam"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.beams and structural_data.active_beam_index >= 0:
            beam = structural_data.beams[structural_data.active_beam_index]
            
            # Remove visual object
            if beam.name in bpy.data.objects:
                obj = bpy.data.objects[beam.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            structural_data.beams.remove(structural_data.active_beam_index)
            
            if structural_data.active_beam_index >= len(structural_data.beams):
                structural_data.active_beam_index = len(structural_data.beams) - 1
        
        return {'FINISHED'}

class STRUCTURAL_OT_update_beam(Operator):
    bl_idname = "structural.update_beam"
    bl_label = "Update Beam"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.beams and structural_data.active_beam_index >= 0:
            beam = structural_data.beams[structural_data.active_beam_index]
            
            # Remove old beam and create new one
            if beam.name in bpy.data.objects:
                obj = bpy.data.objects[beam.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            utils.create_beam_from_data(beam, structural_data)
        
        return {'FINISHED'}

class STRUCTURAL_OT_add_shell(Operator):
    bl_idname = "structural.add_shell"
    bl_label = "Add Structural Shell"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if len(structural_data.points) < 3:
            self.report({'ERROR'}, "Need at least 3 points to create a shell")
            return {'CANCELLED'}
        
        shell = structural_data.shells.add()
        shell.name = f"Shell_{len(structural_data.shells)}"
        
        # Use first 3 points by default
        point_names = [p.name for p in structural_data.points[:3]]
        shell.point_list = ",".join(point_names)
        
        utils.create_shell_from_data(shell, structural_data)
        
        self.report({'INFO'}, f"Added shell: {shell.name}")
        return {'FINISHED'}

class STRUCTURAL_OT_delete_shell(Operator):
    bl_idname = "structural.delete_shell"
    bl_label = "Delete Selected Shell"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.shells and structural_data.active_shell_index >= 0:
            shell = structural_data.shells[structural_data.active_shell_index]
            
            if shell.name in bpy.data.objects:
                obj = bpy.data.objects[shell.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            structural_data.shells.remove(structural_data.active_shell_index)
            
            if structural_data.active_shell_index >= len(structural_data.shells):
                structural_data.active_shell_index = len(structural_data.shells) - 1
        
        return {'FINISHED'}

class STRUCTURAL_OT_update_shell(Operator):
    bl_idname = "structural.update_shell"
    bl_label = "Update Shell"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        if structural_data.shells and structural_data.active_shell_index >= 0:
            shell = structural_data.shells[structural_data.active_shell_index]
            
            if shell.name in bpy.data.objects:
                obj = bpy.data.objects[shell.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            utils.create_shell_from_data(shell, structural_data)
        
        return {'FINISHED'}

class STRUCTURAL_OT_clear_all(Operator):
    bl_idname = "structural.clear_all"
    bl_label = "Clear All Structural Data"
    bl_description = "Remove all structural elements and data"
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        # Remove all objects created by this addon
        for point in structural_data.points:
            if point.name in bpy.data.objects:
                obj = bpy.data.objects[point.name]
                bpy.data.objects.remove(obj, do_unlink=True)
        
        for beam in structural_data.beams:
            if beam.name in bpy.data.objects:
                obj = bpy.data.objects[beam.name]
                bpy.data.objects.remove(obj, do_unlink=True)
        
        for shell in structural_data.shells:
            if shell.name in bpy.data.objects:
                obj = bpy.data.objects[shell.name]
                bpy.data.objects.remove(obj, do_unlink=True)
        
        # Clear all collections
        structural_data.points.clear()
        structural_data.beams.clear()
        structural_data.shells.clear()
        
        structural_data.active_point_index = 0
        structural_data.active_beam_index = 0
        structural_data.active_shell_index = 0
        
        self.report({'INFO'}, "Cleared all structural data")
        return {'FINISHED'}

class STRUCTURAL_OT_import_json(Operator):
    bl_idname = "structural.import_json"
    bl_label = "Import Structural JSON"
    bl_description = "Import structural data from JSON file"
    
    filepath: StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024, 
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        try:
            # Verify file exists before trying to open it
            import os
            if not os.path.exists(self.filepath):
                self.report({'ERROR'}, f"File not found: {self.filepath}")
                return {'CANCELLED'}
            
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Clear existing data
            bpy.ops.structural.clear_all()
            
            # Import points
            if 'points' in data.get('structural_data', {}):
                for point_name, coords in data['structural_data']['points'].items():
                    point = structural_data.points.add()
                    point.name = point_name
                    point.x, point.y, point.z = coords
                    # Create visual representation
                    with bpy.context.temp_override(**bpy.context.copy()):
                        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(point.x, point.y, point.z))
                    sphere = context.active_object
                    sphere.name = point_name
                    utils.move_to_structural_collection(sphere)
            
            # Import sections (BEFORE beams)
            if 'sections' in data.get('structural_data', {}):
                for section_name, section_data in data['structural_data']['sections'].items():
                    section = structural_data.sections.add()
                    section.name = section_name
                    section.section_type = section_data.get('type', 'CIRCULAR')
                    
                    if section.section_type == 'CIRCULAR':
                        section.diameter = section_data.get('diameter', 0.1)
                    elif section.section_type == 'RECTANGULAR':
                        section.width = section_data.get('width', 0.1)
                        section.height = section_data.get('height', 0.15)
                    elif section.section_type == 'POLYGONAL':
                        section.poly_diameter = section_data.get('diameter', 0.1)
                        section.sides = section_data.get('sides', 6)
            
            # Import beams (AFTER sections)
            if 'beams' in data.get('structural_data', {}):
                for beam_name, beam_data in data['structural_data']['beams'].items():
                    if isinstance(beam_data, dict) and 'start_point' in beam_data and 'end_point' in beam_data:
                        beam = structural_data.beams.add()
                        beam.name = beam_name
                        beam.start_point = beam_data['start_point']
                        beam.end_point = beam_data['end_point']
                        
                        if 'section' in beam_data:
                            beam.section_name = beam_data['section']
                        else:
                            beam.diameter = beam_data.get('diameter', 0.1)
                        
                        utils.create_beam_from_data(beam, structural_data)
            
            # Import shells
            if 'shells' in data.get('structural_data', {}):
                for shell_name, shell_data in data['structural_data']['shells'].items():
                    if isinstance(shell_data, dict) and 'points' in shell_data:
                        shell = structural_data.shells.add()
                        shell.name = shell_name
                        shell.point_list = ",".join(shell_data['points'])
                        shell.thickness = shell_data.get('thickness', 0.05)
                        utils.create_shell_from_data(shell, structural_data)
            
            self.report({'INFO'}, f"Successfully imported {os.path.basename(self.filepath)}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
            import traceback
            traceback.print_exc()  # This will show the full error in console
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
class STRUCTURAL_OT_export_json(Operator):
    bl_idname = "structural.export_json"
    bl_label = "Export Structural JSON"
    bl_description = "Export structural data to JSON file"
    
    filepath: StringProperty(
        name="File Path", 
        description="Filepath used for exporting the file", 
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        try:
            # Ensure the filepath has .json extension
            if not self.filepath.lower().endswith('.json'):
                self.filepath += '.json'
            
            # Build data structure
            data = {
                "structural_data": {
                    "points": {},
                    "beams": {},
                    "shells": {},
                    "sections": {},
                    "metadata": {
                        "version": "1.1",
                        "exported_from": "Blender Structural Modeling", 
                        "units": "blender_units"
                    }
                }
            }
            
            # Export points
            for point in structural_data.points:
                data["structural_data"]["points"][point.name] = [point.x, point.y, point.z]
            
            # Export beams
            for beam in structural_data.beams:
                beam_data = {
                    "start_point": beam.start_point,
                    "end_point": beam.end_point
                }
                if beam.section_name:
                    beam_data["section"] = beam.section_name
                else:
                    beam_data["diameter"] = beam.diameter
                
                data["structural_data"]["beams"][beam.name] = beam_data
            
            # Export shells
            for shell in structural_data.shells:
                data["structural_data"]["shells"][shell.name] = {
                    "points": [p.strip() for p in shell.point_list.split(",")],
                    "thickness": shell.thickness
                }
            
            # Export sections
            for section in structural_data.sections:
                section_data = {
                    "type": section.section_type
                }
                
                if section.section_type == 'CIRCULAR':
                    section_data["diameter"] = section.diameter
                elif section.section_type == 'RECTANGULAR':
                    section_data["width"] = section.width
                    section_data["height"] = section.height
                elif section.section_type == 'POLYGONAL':
                    section_data["diameter"] = section.poly_diameter
                    section_data["sides"] = section.sides
                
                data["structural_data"]["sections"][section.name] = section_data
            
            # Write to file with proper error handling
            import os
            directory = os.path.dirname(self.filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(self.filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            self.report({'INFO'}, f"Successfully exported to {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            import traceback
            traceback.print_exc()  # This will show the full error in console
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Set a sensible default filename
        import time
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.filepath = f"structural_data_{timestamp}.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# UI Lists
class STRUCTURAL_UL_sections(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=item.section_type.title())

class STRUCTURAL_UL_points(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=f"({item.x:.2f}, {item.y:.2f}, {item.z:.2f})")

class STRUCTURAL_UL_beams(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=f"{item.start_point} → {item.end_point}")

class STRUCTURAL_UL_shells(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=f"Points: {item.point_list}")

# Operator classes collection
classes = (
    STRUCTURAL_OT_add_section,
    STRUCTURAL_OT_delete_section,
    STRUCTURAL_OT_organize_collections,
    STRUCTURAL_OT_add_point,
    STRUCTURAL_OT_delete_point,
    STRUCTURAL_OT_update_point_position,
    STRUCTURAL_OT_add_beam,
    STRUCTURAL_OT_delete_beam,
    STRUCTURAL_OT_update_beam,
    STRUCTURAL_OT_add_shell,
    STRUCTURAL_OT_delete_shell,
    STRUCTURAL_OT_update_shell,
    STRUCTURAL_OT_clear_all,
    STRUCTURAL_UL_sections,
    STRUCTURAL_UL_points,
    STRUCTURAL_UL_beams,
    STRUCTURAL_UL_shells,
    STRUCTURAL_OT_import_json,
    STRUCTURAL_OT_export_json,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)