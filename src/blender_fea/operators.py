"""
Operators for Structural Model
"""

# from pathlib import Path
# from sys import path as sys_path
import random
import math
from mathutils import Vector
import bpy
from bpy.types import Operator, UIList
from bpy.props import StringProperty
from . import utils
from . import bl_info  # type: ignore # 
# from blender_fea import bl_info # does not work
import json
import os
import logging
log = logging.getLogger(__name__) # logging added as example

class STRUCTURAL_OT_organize_collections(Operator):
    bl_idname = "structural.organize_collections"
    bl_label = "Organize into Collections"
    bl_description = "Move all structural objects to proper collections"
    
    def execute(self, context):
        
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
        point = structural_data.points.add()
        point.name = f"Point_{len(structural_data.points)}"
        point.x = 0.0
        point.y = 0.0
        point.z = 0.0
        
        # Create visual representation
        with bpy.context.temp_override(**bpy.context.copy()):  # type: ignore
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(point.x, point.y, point.z))
        sphere = context.active_object
        sphere.name = point.name  # type: ignore
        
        # Move to Structural Model collection
        utils.move_to_structural_collection(sphere)

        self.report({'INFO'}, f"Added point: {point.name}")
        return {'FINISHED'}

class STRUCTURAL_OT_delete_point(Operator):
    bl_idname = "structural.delete_point"
    bl_label = "Delete Selected Point"
    
    def execute(self, context):
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
        if structural_data.beams and structural_data.active_beam_index >= 0:
            beam = structural_data.beams[structural_data.active_beam_index]
            
            # Remove old beam and create new one
            if beam.name in bpy.data.objects:
                obj = bpy.data.objects[beam.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            utils.create_beam_from_data(beam, structural_data)
        
        return {'FINISHED'}

class STRUCTURAL_OT_color_beams_by_section_name(bpy.types.Operator):
    bl_idname = "structural.color_beams_by_section_name"
    bl_label = "Color Beams by Section Name"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        beams_colored = 0
        section_materials = {}
        
        for beam_data in structural_data.beams:
            if not beam_data.section_name or beam_data.section_name == "":
                continue  # Skip beams without section assignment
                
            if beam_data.name in bpy.data.objects:
                beam_obj = bpy.data.objects[beam_data.name]
                
                # Create or get material for this specific section name
                if beam_data.section_name not in section_materials:
                    section_materials[beam_data.section_name] = self.create_section_material(beam_data.section_name)
                
                # Assign material to beam
                beam_obj.data.materials.clear()
                beam_obj.data.materials.append(section_materials[beam_data.section_name])
                beams_colored += 1
        
        self.report({'INFO'}, f"Colored {beams_colored} beams by section name")
        return {'FINISHED'}
    
    def create_section_material(self, section_name):
        """Create a unique material for a specific section name"""
        mat_name = f"FEA_Section_{section_name}"
        
        if mat_name in bpy.data.materials:
            return bpy.data.materials[mat_name]
        
        # Create new material with consistent color based on section name
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        
        # Clear default nodes
        material.node_tree.nodes.clear()   # type: ignore
        
        # Create nodes
        bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')   # type: ignore
        output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')   # type: ignore
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])   # type: ignore
        
        # Generate consistent color from section name hash
        color = self.generate_color_from_name(section_name)
        bsdf.inputs['Base Color'].default_value = color   # type: ignore
        
        return material
    
    def generate_color_from_name(self, name):
        """Generate a consistent color from a string name"""
        import hashlib
        
        # Create hash from name for consistent coloring
        hash_obj = hashlib.md5(name.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Use first 6 characters of hash for RGB values
        r = int(hash_hex[0:2], 16) / 255.0
        g = int(hash_hex[2:4], 16) / 255.0
        b = int(hash_hex[4:6], 16) / 255.0
        
        # Ensure reasonable brightness and saturation
        # You can adjust these constraints based on your preference
        r = max(0.3, min(0.9, r))
        g = max(0.3, min(0.9, g)) 
        b = max(0.3, min(0.9, b))
        
        return (r, g, b, 1.0)

class STRUCTURAL_OT_color_beams_by_section_palette(bpy.types.Operator):
    bl_idname = "structural.color_beams_by_section_palette"
    bl_label = "Color Beams by Section (Palette)"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        # Define a nice color palette
        color_palette = [
            (0.8, 0.2, 0.2, 1.0),  # Red
            (0.2, 0.6, 0.8, 1.0),  # Blue
            (0.2, 0.8, 0.3, 1.0),  # Green
            (0.8, 0.6, 0.1, 1.0),  # Yellow
            (0.7, 0.3, 0.8, 1.0),  # Purple
            (0.1, 0.8, 0.8, 1.0),  # Cyan
            (0.9, 0.4, 0.1, 1.0),  # Orange
            (0.6, 0.3, 0.6, 1.0),  # Magenta
        ]
        
        # Map section names to colors
        section_colors = {}
        beams_colored = 0
        
        for i, beam_data in enumerate(structural_data.beams):
            if not beam_data.section_name or beam_data.section_name == "":
                continue
                
            if beam_data.name in bpy.data.objects:
                beam_obj = bpy.data.objects[beam_data.name]
                
                # Assign color based on section name
                if beam_data.section_name not in section_colors:
                    # Use modulo to cycle through palette
                    color_index = len(section_colors) % len(color_palette)
                    section_colors[beam_data.section_name] = color_palette[color_index]
                
                # Create or get material
                mat_name = f"FEA_Section_{beam_data.section_name}"
                if mat_name in bpy.data.materials:
                    material = bpy.data.materials[mat_name]
                else:
                    material = bpy.data.materials.new(name=mat_name)
                    material.use_nodes = True
                    
                    material.node_tree.nodes.clear()   # type: ignore
                    bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')   # type: ignore
                    output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')   # type: ignore
                    material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])   # type: ignore
                    
                    bsdf.inputs['Base Color'].default_value = section_colors[beam_data.section_name]   # type: ignore
                
                # Assign material
                beam_obj.data.materials.clear()
                beam_obj.data.materials.append(material)
                beams_colored += 1
        
        self.report({'INFO'}, f"Colored {beams_colored} beams using {len(section_colors)} different sections")
        return {'FINISHED'}

class STRUCTURAL_OT_color_all_beams_with_sections(bpy.types.Operator):
    bl_idname = "structural.color_all_beams_with_sections"
    bl_label = "Color All Beams (Include Unassigned)"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        beams_colored = 0
        section_materials = {}
        
        for beam_data in structural_data.beams:
            if beam_data.name in bpy.data.objects:
                beam_obj = bpy.data.objects[beam_data.name]
                
                # Determine section name (use "Unassigned" if none)
                section_name = beam_data.section_name if beam_data.section_name else "Unassigned"
                
                # Create or get material
                if section_name not in section_materials:
                    section_materials[section_name] = self.create_section_material(section_name)
                
                # Assign material
                beam_obj.data.materials.clear()
                beam_obj.data.materials.append(section_materials[section_name])
                beams_colored += 1
        
        self.report({'INFO'}, f"Colored {beams_colored} beams ({len(section_materials)} different sections)")
        return {'FINISHED'}
    
    def create_section_material(self, section_name):
        """Create material with appropriate color"""
        mat_name = f"FEA_Section_{section_name}"
        
        if mat_name in bpy.data.materials:
            return bpy.data.materials[mat_name]
        
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        
        # Setup nodes
        material.node_tree.nodes.clear()   # type: ignore
        bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')   # type: ignore
        output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')   # type: ignore
        material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])   # type: ignore
        
        # Special color for unassigned sections
        if section_name == "Unassigned":
            color = (0.5, 0.5, 0.5, 1.0)  # Gray
        else:
            # Generate color from name
            import hashlib
            hash_hex = hashlib.md5(section_name.encode()).hexdigest()
            r = int(hash_hex[0:2], 16) / 255.0
            g = int(hash_hex[2:4], 16) / 255.0
            b = int(hash_hex[4:6], 16) / 255.0
            color = (r, g, b, 1.0)
        
        bsdf.inputs['Base Color'].default_value = color   # type: ignore
        return material

class STRUCTURAL_OT_color_beams_emission(bpy.types.Operator):
    bl_idname = "structural.color_beams_emission"
    bl_label = "Color Beams (Emission - Super Bright)"
    
    emission_strength: bpy.props.FloatProperty(  # type: ignore
        name="Emission Strength",
        description="How bright the emission should be",
        default=3.0,
        min=1.0,
        max=10.0
    )
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        beams_colored = 0
        section_materials = {}
        
        for beam_data in structural_data.beams:
            if not beam_data.section_name:
                continue
                
            if beam_data.name in bpy.data.objects:
                beam_obj = bpy.data.objects[beam_data.name]
                
                if beam_data.section_name not in section_materials:
                    section_materials[beam_data.section_name] = self.create_emission_material(
                        beam_data.section_name, self.emission_strength
                    )
                
                beam_obj.data.materials.clear()
                beam_obj.data.materials.append(section_materials[beam_data.section_name])
                beams_colored += 1
        
        # Switch to material preview
        for area in context.screen.areas:    # type: ignore
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'    # type: ignore
        
        self.report({'INFO'}, f"Applied emission colors to {beams_colored} beams")
        return {'FINISHED'}
    
    def create_emission_material(self, section_name, emission_strength):
        """Create emission-based material for maximum brightness"""
        import hashlib
        
        mat_name = f"FEA_Emission_{section_name}"
        
        if mat_name in bpy.data.materials:
            material = bpy.data.materials[mat_name]
        else:
            material = bpy.data.materials.new(name=mat_name)
            material.use_nodes = True
        
        # Clear and setup emission nodes
        material.node_tree.nodes.clear()    # type: ignore
        
        # Create emission shader
        emission = material.node_tree.nodes.new(type='ShaderNodeEmission')    # type: ignore
        output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')    # type: ignore
        material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])    # type: ignore
        
        # Generate vibrant color
        hash_hex = hashlib.md5(section_name.encode()).hexdigest()
        r = int(hash_hex[0:2], 16) / 255.0
        g = int(hash_hex[2:4], 16) / 255.0
        b = int(hash_hex[4:6], 16) / 255.0
        
        # Make colors more vibrant
        r = min(1.0, r * 1.5)
        g = min(1.0, g * 1.5)
        b = min(1.0, b * 1.5)
        
        emission.inputs['Color'].default_value = (r, g, b, 1.0)    # type: ignore
        emission.inputs['Strength'].default_value = emission_strength    # type: ignore
        
        return material
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)    # type: ignore

class STRUCTURAL_OT_add_shell(Operator):
    bl_idname = "structural.add_shell"
    bl_label = "Add Structural Shell"
    
    def execute(self, context):
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
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
        structural_data = context.scene.structural_data # type: ignore
        
        if structural_data.shells and structural_data.active_shell_index >= 0:
            shell = structural_data.shells[structural_data.active_shell_index]
            
            if shell.name in bpy.data.objects:
                obj = bpy.data.objects[shell.name]
                bpy.data.objects.remove(obj, do_unlink=True)
            
            utils.create_shell_from_data(shell, structural_data)
        
        return {'FINISHED'}

class STRUCTURAL_OT_color_shells_by_thickness(Operator):
    bl_idname = "structural.color_shells_by_thickness"
    bl_label = "Color Shells by Thickness"
    
    color_min: bpy.props.FloatVectorProperty(  # type: ignore
        name="Min Thickness Color",
        description="Color for minimum thickness",
        default=(0.0, 0.0, 1.0, 1.0),  # Blue
        size=4,
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    color_max: bpy.props.FloatVectorProperty(  # type: ignore
        name="Max Thickness Color", 
        description="Color for maximum thickness",
        default=(1.0, 0.0, 0.0, 1.0),  # Red
        size=4,
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    color_zero: bpy.props.FloatVectorProperty(  # type: ignore
        name="Zero Thickness Color",
        description="Color for zero/undefined thickness",
        default=(0.5, 0.5, 0.5, 1.0),  # Gray
        size=4,
        min=0.0,
        max=1.0,
        subtype='COLOR'
    )
    
    use_emission: bpy.props.BoolProperty(  # type: ignore
        name="Use Emission",
        description="Use emission shader for brighter colors",
        default=True
    )
    
    emission_strength: bpy.props.FloatProperty(  # type: ignore
        name="Emission Strength",
        description="Brightness of emission colors",
        default=1.0,
        min=0.1,
        max=5.0
    )
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        if not structural_data.shells:
            self.report({'WARNING'}, "No shells found to color")
            return {'CANCELLED'}
        
        # Find thickness range (only positive thicknesses)
        thicknesses = [shell.thickness for shell in structural_data.shells if shell.thickness > 0]
        
        shells_colored = 0
        shells_with_zero = 0
        shells_with_positive = 0
        
        if not thicknesses:
            # All shells have zero or negative thickness
            self.report({'WARNING'}, "No shells with positive thickness found - using zero thickness color")
            
            for shell_data in structural_data.shells:
                if shell_data.name in bpy.data.objects:
                    shell_obj = bpy.data.objects[shell_data.name]
                    material = self.create_thickness_material(
                        shell_data, self.color_zero, self.use_emission, self.emission_strength
                    )
                    shell_obj.data.materials.clear()
                    shell_obj.data.materials.append(material)
                    shells_colored += 1
                    shells_with_zero += 1
            
            self.report({'INFO'}, f"Colored {shells_colored} shells with zero thickness color")
            return {'FINISHED'}
        
        # We have some positive thicknesses
        min_thickness = min(thicknesses)
        max_thickness = max(thicknesses)
        thickness_range = max_thickness - min_thickness
        
        self.report({'INFO'}, f"Thickness range: {min_thickness:.3f} to {max_thickness:.3f}")
        
        for shell_data in structural_data.shells:
            if shell_data.name in bpy.data.objects:
                shell_obj = bpy.data.objects[shell_data.name]
                
                if shell_data.thickness <= 0:
                    # Zero or negative thickness - use special color
                    color = self.color_zero
                    shells_with_zero += 1
                else:
                    # Positive thickness - calculate gradient color
                    if thickness_range > 0:
                        normalized_thickness = (shell_data.thickness - min_thickness) / thickness_range
                    else:
                        # All positive thicknesses are the same
                        normalized_thickness = 0.5
                    
                    color = self.interpolate_color(self.color_min, self.color_max, normalized_thickness)
                    shells_with_positive += 1
                
                # Create or get material
                material = self.create_thickness_material(shell_data, color, self.use_emission, self.emission_strength)
                
                # Assign material to shell
                shell_obj.data.materials.clear()
                shell_obj.data.materials.append(material)
                shells_colored += 1
        
        # Switch to material preview
        for area in context.screen.areas:  # type: ignore
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'  # type: ignore
        
        # Detailed report
        report_msg = f"Colored {shells_colored} shells"
        if shells_with_positive > 0:
            report_msg += f" ({shells_with_positive} with thickness gradient)"
        if shells_with_zero > 0:
            report_msg += f" ({shells_with_zero} with zero thickness)"
        
        self.report({'INFO'}, report_msg)
        return {'FINISHED'}
    
    def interpolate_color(self, color_min, color_max, factor):
        """Interpolate between two colors based on factor (0-1)"""
        r = color_min[0] + (color_max[0] - color_min[0]) * factor
        g = color_min[1] + (color_max[1] - color_min[1]) * factor
        b = color_min[2] + (color_max[2] - color_min[2]) * factor
        a = color_min[3]  # Keep alpha constant
        
        return (r, g, b, a)
    
    def create_thickness_material(self, shell_data, color, use_emission, emission_strength):
        """Create material for shell with thickness-based color"""
        mat_name = f"FEA_Shell_Thickness_{shell_data.name}"
        
        if mat_name in bpy.data.materials:
            material = bpy.data.materials[mat_name]
            # Update existing material color
            if material.use_nodes:
                if use_emission:
                    emission = material.node_tree.nodes.get('Emission')  # type: ignore
                    if emission:
                        emission.inputs['Color'].default_value = color  # type: ignore
                        emission.inputs['Strength'].default_value = emission_strength  # type: ignore
                else:
                    bsdf = material.node_tree.nodes.get('Principled BSDF')  # type: ignore
                    if bsdf:
                        bsdf.inputs['Base Color'].default_value = color  # type: ignore
            return material
        
        # Create new material
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        material.node_tree.nodes.clear()  # type: ignore
        
        if use_emission:
            # Use emission shader for bright, clear colors
            emission = material.node_tree.nodes.new(type='ShaderNodeEmission')  # type: ignore
            output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')  # type: ignore
            material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])  # type: ignore
            
            emission.inputs['Color'].default_value = color  # type: ignore
            emission.inputs['Strength'].default_value = emission_strength  # type: ignore
        else:
            # Use principled BSDF for more natural look
            bsdf = material.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')  # type: ignore
            output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')  # type: ignore
            material.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])  # type: ignore
            
            bsdf.inputs['Base Color'].default_value = color  # type: ignore
            bsdf.inputs['Metallic'].default_value = 0.0  # type: ignore
            bsdf.inputs['Roughness'].default_value = 0.3  # type: ignore
        
        return material
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)  # type: ignore

class STRUCTURAL_OT_color_shells_thickness_simple(Operator):
    bl_idname = "structural.color_shells_thickness_simple"
    bl_label = "Color Shells by Thickness (Simple)"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        if not structural_data.shells:
            self.report({'WARNING'}, "No shells found")
            return {'CANCELLED'}
        
        # Find thickness range (only positive)
        thicknesses = [shell.thickness for shell in structural_data.shells if shell.thickness > 0]
        
        shells_colored = 0
        shells_zero = 0
        
        # Color definitions
        color_zero = (0.7, 0.7, 0.7, 1.0)  # Gray for zero thickness
        color_min = (0.0, 0.3, 1.0, 1.0)   # Blue for min thickness
        color_max = (1.0, 0.0, 0.0, 1.0)   # Red for max thickness
        
        if not thicknesses:
            # Case 1: All shells have zero thickness
            self.report({'INFO'}, "All shells have zero thickness - coloring gray")
            for shell_data in structural_data.shells:
                if shell_data.name in bpy.data.objects:
                    self.color_shell(shell_data, color_zero)
                    shells_colored += 1
                    shells_zero += 1
        elif len(thicknesses) == 1:
            # Case 2: Only one unique positive thickness
            single_thickness = thicknesses[0]
            self.report({'INFO'}, f"All positive thicknesses are {single_thickness:.3f} - using mid-color")
            for shell_data in structural_data.shells:
                if shell_data.name in bpy.data.objects:
                    if shell_data.thickness <= 0:
                        self.color_shell(shell_data, color_zero)
                        shells_zero += 1
                    else:
                        # All same thickness - use middle of gradient
                        mid_color = self.interpolate_color(color_min, color_max, 0.5)
                        self.color_shell(shell_data, mid_color)
                    shells_colored += 1
        else:
            # Case 3: Multiple different thicknesses
            min_thickness = min(thicknesses)
            max_thickness = max(thicknesses)
            thickness_range = max_thickness - min_thickness
            
            self.report({'INFO'}, f"Thickness: {min_thickness:.3f} to {max_thickness:.3f}")
            
            for shell_data in structural_data.shells:
                if shell_data.name in bpy.data.objects:
                    if shell_data.thickness <= 0:
                        self.color_shell(shell_data, color_zero)
                        shells_zero += 1
                    else:
                        normalized = (shell_data.thickness - min_thickness) / thickness_range
                        color = self.interpolate_color(color_min, color_max, normalized)
                        self.color_shell(shell_data, color)
                    shells_colored += 1
        
        # Update viewport
        for area in context.screen.areas:     # type: ignore
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.shading.type = 'MATERIAL'     # type: ignore
        
        # Detailed report
        if shells_zero > 0:
            self.report({'INFO'}, f"Colored {shells_colored} shells ({shells_zero} with zero thickness)")
        else:
            self.report({'INFO'}, f"Colored {shells_colored} shells")
        
        return {'FINISHED'}
    
    def color_shell(self, shell_data, color):
        """Apply color to a single shell"""
        shell_obj = bpy.data.objects[shell_data.name]
        mat_name = f"FEA_Shell_{shell_data.name}"
        
        if mat_name in bpy.data.materials:
            material = bpy.data.materials[mat_name]
            # Update color
            if material.use_nodes:
                emission = material.node_tree.nodes.get('Emission')     # type: ignore
                if emission:
                    emission.inputs['Color'].default_value = color     # type: ignore
            return material
        
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
        material.node_tree.nodes.clear()     # type: ignore
        
        # Use emission for bright colors
        emission = material.node_tree.nodes.new(type='ShaderNodeEmission')     # type: ignore
        output = material.node_tree.nodes.new(type='ShaderNodeOutputMaterial')     # type: ignore
        material.node_tree.links.new(emission.outputs['Emission'], output.inputs['Surface'])     # type: ignore
        
        emission.inputs['Color'].default_value = color     # type: ignore
        emission.inputs['Strength'].default_value = 1.5     # type: ignore
        
        shell_obj.data.materials.clear()
        shell_obj.data.materials.append(material)
        
        return material
    
    def interpolate_color(self, color_a, color_b, factor):
        r = color_a[0] + (color_b[0] - color_a[0]) * factor
        g = color_a[1] + (color_b[1] - color_a[1]) * factor
        b = color_a[2] + (color_b[2] - color_a[2]) * factor
        return (r, g, b, 1.0)

class STRUCTURAL_OT_show_thickness_info(bpy.types.Operator):
    bl_idname = "structural.show_thickness_info"
    bl_label = "Show Thickness Info"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        if not structural_data.shells:
            self.report({'INFO'}, "No shells in scene")
            return {'CANCELLED'}
        
        # Count different cases
        total_shells = len(structural_data.shells)
        positive_thickness = [s.thickness for s in structural_data.shells if s.thickness > 0]
        zero_thickness = [s for s in structural_data.shells if s.thickness <= 0]
        
        if not positive_thickness:
            self.report({'INFO'}, f"All {total_shells} shells have zero/undefined thickness")
        elif len(positive_thickness) == 1:
            self.report({'INFO'}, f"All {len(positive_thickness)} positive thickness shells are {positive_thickness[0]:.4f} (+ {len(zero_thickness)} zero thickness)")
        else:
            min_thick = min(positive_thickness)
            max_thick = max(positive_thickness)
            avg_thick = sum(positive_thickness) / len(positive_thickness)
            
            info_msg = f"Thickness: {min_thick:.4f} to {max_thick:.4f} (avg: {avg_thick:.4f})"
            if zero_thickness:
                info_msg += f" + {len(zero_thickness)} zero thickness shells"
            
            self.report({'INFO'}, info_msg)
        
        return {'FINISHED'}


class STRUCTURAL_OT_clear_all(Operator):
    bl_idname = "structural.clear_all"
    bl_label = "Clear All Structural Data"
    bl_description = "Remove all structural elements and data"
    
    def execute(self, context):
        structural_data = context.scene.structural_data # type: ignore
        
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
    
    filepath: StringProperty( # type: ignore
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024, 
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty( # type: ignore
        default='*.json', options={'HIDDEN'}
        )
    
    def execute(self, context):
        structural_data = context.scene.structural_data # type: ignore
        
        try:
            # Verify file exists before trying to open it
            import os
            if not os.path.exists(self.filepath):
                self.report({'ERROR'}, f"File not found: {self.filepath}")
                return {'CANCELLED'}
            
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Clear existing data
            bpy.ops.structural.clear_all() # type: ignore
            
            # Import points
            if 'points' in data.get('structural_data', {}):
                for point_name, coords in data['structural_data']['points'].items():
                    point = structural_data.points.add()
                    point.name = point_name
                    point.x, point.y, point.z = coords
                    # Create visual representation
                    with bpy.context.temp_override(**bpy.context.copy()): # type: ignore
                        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(point.x, point.y, point.z))
                    sphere = context.active_object
                    sphere.name = point_name  # type: ignore
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
        context.window_manager.fileselect_add(self) # type: ignore
        return {'RUNNING_MODAL'}

class STRUCTURAL_OT_export_json(Operator):
    bl_idname = "structural.export_json"
    bl_label = "Export Structural JSON"
    bl_description = "Export structural data to JSON file"
    
    filepath: StringProperty( # type: ignore
        name="File Path", 
        description="Filepath used for exporting the file", 
        maxlen=1024,
        subtype='FILE_PATH'
    )
    
    filter_glob: StringProperty( # type: ignore
        default='*.json', options={'HIDDEN'}
        )
    
    def execute(self, context):
        structural_data = context.scene.structural_data # type: ignore
        
        try:
            # Ensure the filepath has .json extension
            if not self.filepath.lower().endswith('.json'):
                self.filepath += '.json'
            
            # Get version from bl_info
            version_name = bl_info['name']
            version_tuple = bl_info['version']
            version_string = f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"
            scene_units = context.scene.unit_settings.system   # type: ignore
            scale_length = context.scene.unit_settings.scale_length   # type: ignore
            length_unit = context.scene.unit_settings.length_unit   # type: ignore
            
            # Build data structure
            data = {
                "structural_data": {
                    "points": {},
                    "beams": {},
                    "shells": {},
                    "sections": {},
                    "metadata": {
                        "version": version_string,
                        "exported_from": version_name, 
                        "units": scene_units,
                        "scale_length": scale_length,
                        "length_unit": length_unit,
                        "blender_version": bpy.app.version_string
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
        context.window_manager.fileselect_add(self)   # type: ignore
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

# Test Operators


class STRUCTURAL_OT_create_hexagon_points(Operator):
    bl_idname = "structural.create_hexagon_points"
    bl_label = "Create Hexagon Test Points"
    bl_description = "Create 6 points in a randomly deformed hexagon pattern"
    
    radius: bpy.props.FloatProperty(  # type: ignore
        name="Base Radius",
        description="Radius of the base hexagon",
        default=2.0,
        min=0.1,
        max=10.0
    )
    
    center_x: bpy.props.FloatProperty(  # type: ignore
        name="Center X",
        description="X coordinate of hexagon center",
        default=0.0
    )
    
    center_y: bpy.props.FloatProperty(  # type: ignore
        name="Center Y", 
        description="Y coordinate of hexagon center",
        default=0.0
    )
    
    center_z: bpy.props.FloatProperty(  # type: ignore
        name="Center Z",
        description="Z coordinate of hexagon center", 
        default=0.0
    )
    
    deformation_strength: bpy.props.FloatProperty(  # type: ignore
        name="Deformation Strength",
        description="How much to randomly deform the hexagon",
        default=0.3,
        min=0.0,
        max=1.0
    )
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        # Clear existing test points if they exist
        self.cleanup_existing_test_points(structural_data)
        
        # Create hexagon points
        points_data = self.generate_hexagon_points()
        
        # Add points to structural data and create visual objects
        point_names = []
        for i, (x, y, z) in enumerate(points_data):
            point = structural_data.points.add()
            point.name = f"HexPoint_{i+1}"
            point.x = x
            point.y = y
            point.z = z
            point_names.append(point.name)
            
            # Create visual representation
            self.create_point_visual(point)
        
        # Auto-create a shell using these points
        shell = structural_data.shells.add()
        shell.name = "Hexagon_Shell"
        shell.point_list = ", ".join(point_names)
        shell.thickness = 0.1
        
        # Create the shell geometry
        try:
            from . import utils
            utils.create_shell_from_data(shell, structural_data)
        except Exception as e:
            self.report({'WARNING'}, f"Created points but shell creation failed: {str(e)}")
        else:
            self.report({'INFO'}, f"Created hexagon with 6 points and shell")
        
        return {'FINISHED'}
    
    def generate_hexagon_points(self):
        """Generate 6 points in a randomly deformed hexagon"""
        points = []
        center = Vector((self.center_x, self.center_y, self.center_z))
        
        # Generate base regular hexagon points
        for i in range(6):
            angle = 2 * math.pi * i / 6  # 60 degree increments
            base_x = math.cos(angle) * self.radius
            base_y = math.sin(angle) * self.radius
            
            # Apply random deformation
            deform_x = random.uniform(-self.deformation_strength, self.deformation_strength)
            deform_y = random.uniform(-self.deformation_strength, self.deformation_strength)
            deform_z = random.uniform(-self.deformation_strength * 0.5, self.deformation_strength * 0.5)
            
            # Final point coordinates
            x = center.x + base_x + deform_x
            y = center.y + base_y + deform_y  
            z = center.z + deform_z  # Slight variation in Z for non-planar test
            
            points.append((x, y, z))
        
        return points
    
    def create_point_visual(self, point):
        """Create visual sphere for point"""
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=0.1, 
            location=(point.x, point.y, point.z)
        )
        sphere = bpy.context.active_object
        sphere.name = point.name    # type: ignore
        
        # Move to Structural Model collection
        from . import utils
        utils.move_to_structural_collection(sphere)
    
    def cleanup_existing_test_points(self, structural_data):
        """Remove any existing test points and objects"""
        points_to_remove = []
        
        # Find test points
        for i, point in enumerate(structural_data.points):
            if point.name.startswith("HexPoint_"):
                points_to_remove.append(i)
                # Remove visual object
                if point.name in bpy.data.objects:
                    obj = bpy.data.objects[point.name]
                    bpy.data.objects.remove(obj, do_unlink=True)
        
        # Remove from structural data (reverse to maintain indices)
        for i in sorted(points_to_remove, reverse=True):
            structural_data.points.remove(i)
        
        # Remove test shell
        shells_to_remove = []
        for i, shell in enumerate(structural_data.shells):
            if shell.name.startswith("Hexagon"):
                shells_to_remove.append(i)
                if shell.name in bpy.data.objects:
                    obj = bpy.data.objects[shell.name]
                    bpy.data.objects.remove(obj, do_unlink=True)
        
        for i in sorted(shells_to_remove, reverse=True):
            structural_data.shells.remove(i)
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)  # type: ignore


class STRUCTURAL_OT_create_simple_hexagon(Operator):
    bl_idname = "structural.create_simple_hexagon"
    bl_label = "Create Simple Hexagon"
    bl_description = "Create a simple hexagon with one click"
    
    def execute(self, context):
        structural_data = context.scene.structural_data  # type: ignore
        
        # Clear existing test points
        self.cleanup_test_points(structural_data)
        
        # Create 6 points in hexagon pattern
        hex_points = [
            ( 2.0,  0.0, 0.0),    # Right
            ( 1.0,  1.73, 0.0),   # Top-right  
            (-1.0,  1.73, 0.0),   # Top-left
            (-2.0,  0.0, 0.0),    # Left
            (-1.0, -1.73, 0.0),   # Bottom-left
            ( 1.0, -1.73, 0.0)    # Bottom-right
        ]
        
        point_names = []
        for i, (x, y, z) in enumerate(hex_points):
            point = structural_data.points.add()
            point.name = f"Hex_{i+1}"
            point.x = x
            point.y = y
            point.z = z
            point_names.append(point.name)
            
            # Create visual
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z))
            sphere = bpy.context.active_object
            sphere.name = point.name    # type: ignore
            from . import utils
            utils.move_to_structural_collection(sphere)
        
        # Create shell
        shell = structural_data.shells.add()
        shell.name = "Test_Hexagon"
        shell.point_list = ", ".join(point_names)
        shell.thickness = 0.15
        
        # Create shell geometry
        try:
            from . import utils
            utils.create_shell_from_data(shell, structural_data)
            self.report({'INFO'}, "Created regular hexagon with 6 points")
        except Exception as e:
            self.report({'ERROR'}, f"Shell creation failed: {str(e)}")
            return {'CANCELLED'}
        
        return {'FINISHED'}
    
    def cleanup_test_points(self, structural_data):
        """Clean up previous test points"""
        # Remove points
        points_to_remove = []
        for i, point in enumerate(structural_data.points):
            if point.name.startswith(("Hex_", "HexPoint_")):
                points_to_remove.append(i)
                if point.name in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects[point.name], do_unlink=True)
        
        for i in sorted(points_to_remove, reverse=True):
            structural_data.points.remove(i)
        
        # Remove shells  
        shells_to_remove = []
        for i, shell in enumerate(structural_data.shells):
            if shell.name.startswith(("Hexagon", "Test_Hexagon")):
                shells_to_remove.append(i)
                if shell.name in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects[shell.name], do_unlink=True)
        
        for i in sorted(shells_to_remove, reverse=True):
            structural_data.shells.remove(i)

			
class STRUCTURAL_OT_create_nonplanar_hexagon(Operator):
    bl_idname = "structural.create_nonplanar_hexagon"
    bl_label = "Create Non-Planar Hexagon"
    bl_description = "Create a hexagon with points at different Z heights"
    
    def execute(self, context):
        structural_data = context.scene.structural_data    # type: ignore
        
        self.cleanup_test_points(structural_data)
        
        # Create a "bowl-shaped" hexagon with varying Z heights
        hex_points = [
            ( 2.0,  0.0, 0.2),    # Slightly raised
            ( 1.0,  1.73, 0.5),   # Higher
            (-1.0,  1.73, 0.3),   # Medium
            (-2.0,  0.0, 0.0),    # Base level
            (-1.0, -1.73, 0.4),   # Medium-high
            ( 1.0, -1.73, 0.1)    # Slightly raised
        ]
        
        point_names = []
        for i, (x, y, z) in enumerate(hex_points):
            point = structural_data.points.add()
            point.name = f"Hex3D_{i+1}"
            point.x = x
            point.y = y
            point.z = z
            point_names.append(point.name)
            
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y, z))
            sphere = bpy.context.active_object
            sphere.name = point.name    # type: ignore
            from . import utils
            utils.move_to_structural_collection(sphere)
        
        # Create shell - this will test non-planar handling
        shell = structural_data.shells.add()
        shell.name = "NonPlanar_Hexagon"
        shell.point_list = ", ".join(point_names)
        shell.thickness = 0.1
        
        try:
            from . import utils
            result = utils.create_shell_from_data(shell, structural_data)
            if result:
                self.report({'INFO'}, "Created non-planar hexagon - check console for warnings")
            else:
                self.report({'WARNING'}, "Non-planar hexagon creation may have issues")
        except Exception as e:
            self.report({'ERROR'}, f"Non-planar shell failed: {str(e)}")
        
        return {'FINISHED'}
    
    def cleanup_test_points(self, structural_data):
        """Clean up test points"""
        # Implementation similar to previous example
        pass



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
    STRUCTURAL_OT_color_beams_by_section_name,
    STRUCTURAL_OT_color_beams_by_section_palette,
    STRUCTURAL_OT_color_all_beams_with_sections,
    STRUCTURAL_OT_color_beams_emission,
    STRUCTURAL_OT_add_shell,
    STRUCTURAL_OT_delete_shell,
    STRUCTURAL_OT_update_shell,
    STRUCTURAL_OT_color_shells_by_thickness,
    STRUCTURAL_OT_color_shells_thickness_simple,
    STRUCTURAL_OT_show_thickness_info,
    STRUCTURAL_OT_clear_all,
    STRUCTURAL_UL_sections,
    STRUCTURAL_UL_points,
    STRUCTURAL_UL_beams,
    STRUCTURAL_UL_shells,
    STRUCTURAL_OT_import_json,
    STRUCTURAL_OT_export_json,
    STRUCTURAL_OT_create_hexagon_points,
    STRUCTURAL_OT_create_simple_hexagon,
    STRUCTURAL_OT_create_nonplanar_hexagon,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)