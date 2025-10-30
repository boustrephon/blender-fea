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
    
    filepath: StringProperty(subtype='FILE_PATH')
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        log.info("Import operation started")
        
        try:
            with open(self.filepath, 'r') as file:
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
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(point.x, point.y, point.z))
                    sphere = context.active_object
                    sphere.name = point.name
            
            # Import beams
            if 'beams' in data.get('structural_data', {}):
                for beam_name, points in data['structural_data']['beams'].items():
                    if len(points) == 2:
                        beam = structural_data.beams.add()
                        beam.name = beam_name
                        beam.start_point, beam.end_point = points
                        beam.diameter = 0.1  # Default diameter
                        utils.create_beam_from_data(beam, structural_data)
            
            # Import shells
            if 'shells' in data.get('structural_data', {}):
                for shell_name, point_list in data['structural_data']['shells'].items():
                    if len(point_list) >= 3:
                        shell = structural_data.shells.add()
                        shell.name = shell_name
                        shell.point_list = ",".join(point_list)
                        shell.thickness = 0.05  # Default thickness
                        utils.create_shell_from_data(shell, structural_data)
            
            self.report({'INFO'}, f"Successfully imported {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Import failed: {str(e)}")
            return {'CANCELLED'}
        
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class STRUCTURAL_OT_export_json(Operator):
    bl_idname = "structural.export_json"
    bl_label = "Export Structural JSON"
    bl_description = "Export structural data to JSON file"
    
    filepath: StringProperty(subtype='FILE_PATH')
    filter_glob: StringProperty(default='*.json', options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene
        structural_data = scene.structural_data
        
        try:
            # Build data structure
            data = {
                "structural_data": {
                    "points": {},
                    "beams": {},
                    "shells": {},
                    "metadata": {
                        "version": "1.0",
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
                data["structural_data"]["beams"][beam.name] = [beam.start_point, beam.end_point]
            
            # Export shells
            for shell in structural_data.shells:
                data["structural_data"]["shells"][shell.name] = [p.strip() for p in shell.point_list.split(",")]
            
            # Write to file
            with open(self.filepath, 'w') as file:
                json.dump(data, file, indent=2)
            
            self.report({'INFO'}, f"Successfully exported to {self.filepath}")
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Export failed: {str(e)}")
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        # Set default filename
        self.filepath = "structural_data.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    

# UI Lists
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
    STRUCTURAL_OT_organize_collections,  # ← Make sure this is here
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