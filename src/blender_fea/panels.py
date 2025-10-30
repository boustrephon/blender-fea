import bpy
from bpy.types import Panel

class VIEW3D_PT_structural_modeling(Panel):
    bl_label = "Structural Modeling"
    bl_idname = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Structural"
    
    def draw(self, context):
        layout = self.layout
        
        box = layout.box()    # type: ignore
        box.label(text="Quick Actions")
        row = box.row()
        row.operator("structural.add_point", text="Add Point")
        row.operator("structural.add_beam", text="Add Beam")
        row.operator("structural.add_shell", text="Add Shell")
        
        # Collection management
        box = layout.box()   # type: ignore
        box.label(text="Collection Management")
        box.operator("structural.organize_collections", text="Organize Collections")

        # Import/Export
        box = layout.box()   # type: ignore
        box.label(text="Data Management")
        row = box.row()
        row.operator("structural.import_json", text="Import JSON", icon='IMPORT')
        row.operator("structural.export_json", text="Export JSON", icon='EXPORT')
        
        layout.operator("structural.clear_all", icon='TRASH', text="Clear All")   # type: ignore

class VIEW3D_PT_structural_points(Panel):
    bl_label = "Structural Points"
    bl_idname = "VIEW3D_PT_structural_points"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        structural_data = context.scene.structural_data   # type: ignore
        
        row = layout.row()   # type: ignore
        row.template_list("STRUCTURAL_UL_points", "", structural_data, "points", 
                         structural_data, "active_point_index")
        
        col = row.column(align=True)
        col.operator("structural.add_point", icon='ADD', text="")
        col.operator("structural.delete_point", icon='REMOVE', text="")
        
        if structural_data.points and structural_data.active_point_index >= 0:
            point = structural_data.points[structural_data.active_point_index]
            box = layout.box()   # type: ignore
            box.label(text=f"Point: {point.name}")
            box.prop(point, "x")
            box.prop(point, "y")
            box.prop(point, "z")
            box.operator("structural.update_point_position", text="Update Position")

class VIEW3D_PT_structural_beams(Panel):
    bl_label = "Structural Beams"
    bl_idname = "VIEW3D_PT_structural_beams"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        structural_data = context.scene.structural_data   # type: ignore
        
        row = layout.row()   # type: ignore
        row.template_list("STRUCTURAL_UL_beams", "", structural_data, "beams", 
                         structural_data, "active_beam_index")
        
        col = row.column(align=True)
        col.operator("structural.add_beam", icon='ADD', text="")
        col.operator("structural.delete_beam", icon='REMOVE', text="")
        
        if structural_data.beams and structural_data.active_beam_index >= 0:
            beam = structural_data.beams[structural_data.active_beam_index]
            box = layout.box()   # type: ignore
            box.label(text=f"Beam: {beam.name}")
            box.prop_search(beam, "start_point", structural_data, "points", text="Start")
            box.prop_search(beam, "end_point", structural_data, "points", text="End")
            
            # Section selection
            box.prop_search(beam, "section_name", structural_data, "sections", text="Section")
            
            # Legacy diameter (for backward compatibility)
            if not beam.section_name:
                box.prop(beam, "diameter")
            
            box.operator("structural.update_beam", text="Update Beam")

class VIEW3D_PT_structural_sections(Panel):
    bl_label = "Section Profiles"
    bl_idname = "VIEW3D_PT_structural_sections"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        structural_data = context.scene.structural_data   # type: ignore
        
        row = layout.row()   # type: ignore
        row.template_list("STRUCTURAL_UL_sections", "", structural_data, "sections", 
                         structural_data, "active_section_index")
        
        col = row.column(align=True)
        col.operator("structural.add_section", icon='ADD', text="")
        col.operator("structural.delete_section", icon='REMOVE', text="")
        
        if structural_data.sections and structural_data.active_section_index >= 0:
            section = structural_data.sections[structural_data.active_section_index]
            box = layout.box()   # type: ignore
            box.label(text=f"Section: {section.name}")
            box.prop(section, "section_type")
            
            if section.section_type == 'CIRCULAR':
                box.prop(section, "diameter")
            elif section.section_type == 'RECTANGULAR':
                box.prop(section, "width")
                box.prop(section, "height")
            elif section.section_type == 'POLYGONAL':
                box.prop(section, "sides")
                box.prop(section, "poly_diameter")

class STRUCTURAL_PT_visualization(Panel):
    bl_label = "Beam Visualization"
    bl_idname = "STRUCTURAL_PT_visualization"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Structural'
    
    def draw(self, context):
        layout = self.layout
        
        layout.label(text="Switch to Material Preview (Z) to see colors")   # type: ignore
        layout.separator()   # type: ignore
        
        # Beam coloring section
        layout.label(text="Beam Coloring:")   # type: ignore
        layout.operator("structural.color_beams_by_section_name")   # type: ignore
        layout.operator("structural.color_beams_emission", text="Bright Beams")   # type: ignore
        layout.separator()   # type: ignore
        
        # Shell coloring section
        layout.label(text="Shell Coloring:")   # type: ignore
        layout.operator("structural.color_shells_by_thickness", text="Color Shells by Thickness")   # type: ignore
        layout.operator("structural.color_shells_thickness_simple", text="Quick Thickness Colors")   # type: ignore
        layout.operator("structural.show_thickness_info", text="Show Thickness Range")   # type: ignore
        
        # Show shell thickness statistics
        structural_data = context.scene.structural_data  # type: ignore
        if structural_data.shells:
            thicknesses = [s.thickness for s in structural_data.shells if s.thickness > 0]
            if thicknesses:
                min_t = min(thicknesses)
                max_t = max(thicknesses)
                layout.separator()   # type: ignore
                layout.label(text="Shell Thickness Range:")   # type: ignore
                layout.label(text=f"  Min: {min_t:.4f}")   # type: ignore
                layout.label(text=f"  Max: {max_t:.4f}")   # type: ignore

class VIEW3D_PT_structural_shells(Panel):
    bl_label = "Structural Shells"
    bl_idname = "VIEW3D_PT_structural_shells"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        structural_data = context.scene.structural_data   # type: ignore
        
        row = layout.row()   # type: ignore
        row.template_list("STRUCTURAL_UL_shells", "", structural_data, "shells", 
                         structural_data, "active_shell_index")
        
        col = row.column(align=True)
        col.operator("structural.add_shell", icon='ADD', text="")
        col.operator("structural.delete_shell", icon='REMOVE', text="")
        
        if structural_data.shells and structural_data.active_shell_index >= 0:
            shell = structural_data.shells[structural_data.active_shell_index]
            box = layout.box()   # type: ignore
            box.label(text=f"Shell: {shell.name}")
            box.prop(shell, "point_list", text="Points")
            box.label(text="Comma separated point names")
            box.prop(shell, "thickness")
            box.operator("structural.update_shell", text="Update Shell")


# Testing...
class STRUCTURAL_PT_test_objects(Panel):
    bl_label = "Test Objects"
    bl_idname = "STRUCTURAL_PT_test_objects"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Structural'
    
    def draw(self, context):
        layout = self.layout # This is your UILayout object        
        layout.label(text="Hexagon Test Creation:")    # type: ignore
        layout.operator("structural.create_hexagon_points", text="Custom Hexagon")    # type: ignore
        layout.operator("structural.create_simple_hexagon", text="Simple Hexagon")     # type: ignore
        layout.operator("structural.create_nonplanar_hexagon", text="Non-Planar Hexagon")    # type: ignore


# Panel classes collection
classes = (
    VIEW3D_PT_structural_modeling,
    VIEW3D_PT_structural_points,
    VIEW3D_PT_structural_beams,
    VIEW3D_PT_structural_shells,
    VIEW3D_PT_structural_sections,
    STRUCTURAL_PT_visualization,
    STRUCTURAL_PT_test_objects,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)