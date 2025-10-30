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
        
        box = layout.box()
        box.label(text="Quick Actions")
        row = box.row()
        row.operator("structural.add_point", text="Add Point")
        row.operator("structural.add_beam", text="Add Beam")
        row.operator("structural.add_shell", text="Add Shell")
        
        # Collection management
        box = layout.box()
        box.label(text="Collection Management")
        box.operator("structural.organize_collections", text="Organize Collections")

        # Import/Export
        box = layout.box()
        box.label(text="Data Management")
        row = box.row()
        row.operator("structural.import_json", text="Import JSON", icon='IMPORT')
        row.operator("structural.export_json", text="Export JSON", icon='EXPORT')
        
        layout.operator("structural.clear_all", icon='TRASH', text="Clear All")

class VIEW3D_PT_structural_points(Panel):
    bl_label = "Structural Points"
    bl_idname = "VIEW3D_PT_structural_points"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        structural_data = scene.structural_data
        
        row = layout.row()
        row.template_list("STRUCTURAL_UL_points", "", structural_data, "points", 
                         structural_data, "active_point_index")
        
        col = row.column(align=True)
        col.operator("structural.add_point", icon='ADD', text="")
        col.operator("structural.delete_point", icon='REMOVE', text="")
        
        if structural_data.points and structural_data.active_point_index >= 0:
            point = structural_data.points[structural_data.active_point_index]
            box = layout.box()
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
        scene = context.scene
        structural_data = scene.structural_data
        
        row = layout.row()
        row.template_list("STRUCTURAL_UL_beams", "", structural_data, "beams", 
                         structural_data, "active_beam_index")
        
        col = row.column(align=True)
        col.operator("structural.add_beam", icon='ADD', text="")
        col.operator("structural.delete_beam", icon='REMOVE', text="")
        
        if structural_data.beams and structural_data.active_beam_index >= 0:
            beam = structural_data.beams[structural_data.active_beam_index]
            box = layout.box()
            box.label(text=f"Beam: {beam.name}")
            box.prop_search(beam, "start_point", structural_data, "points", text="Start")
            box.prop_search(beam, "end_point", structural_data, "points", text="End")
            box.prop(beam, "diameter")
            box.operator("structural.update_beam", text="Update Beam")

class VIEW3D_PT_structural_shells(Panel):
    bl_label = "Structural Shells"
    bl_idname = "VIEW3D_PT_structural_shells"
    bl_parent_id = "VIEW3D_PT_structural_modeling"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        structural_data = scene.structural_data
        
        row = layout.row()
        row.template_list("STRUCTURAL_UL_shells", "", structural_data, "shells", 
                         structural_data, "active_shell_index")
        
        col = row.column(align=True)
        col.operator("structural.add_shell", icon='ADD', text="")
        col.operator("structural.delete_shell", icon='REMOVE', text="")
        
        if structural_data.shells and structural_data.active_shell_index >= 0:
            shell = structural_data.shells[structural_data.active_shell_index]
            box = layout.box()
            box.label(text=f"Shell: {shell.name}")
            box.prop(shell, "point_list", text="Points")
            box.label(text="Comma separated point names")
            box.prop(shell, "thickness")
            box.operator("structural.update_shell", text="Update Shell")

# Panel classes collection
classes = (
    VIEW3D_PT_structural_modeling,
    VIEW3D_PT_structural_points,
    VIEW3D_PT_structural_beams,
    VIEW3D_PT_structural_shells,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)