from bpy.types import Panel

visibility_operators = {'ALL': 'All',
'SIMPLE': 'Simple',
'COMPLEX': 'Complex',
'SIMPLE_COMPLEX':'Simple and Complex',
}

class CollissionPanel(Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Collision Panel"
    bl_idname = "COLLISION_PT_Create"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Pipeline"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        scene = context.scene

        # Physics Materials
        layout.separator()

        row = layout.row()
        row.label(text='Physics Materials')

        row = layout.row()
        row.prop(scene, "PhysicsIdentifier", text='Material Filter')

        row = layout.row()
        row.prop(scene, "CollisionMaterials")



        # Visibillity and Selection
        layout.separator()

        col = self.layout.column_flow(columns=5, align = True)

        for value in visibility_operators:
            col.label(text=value)

        for key, value in visibility_operators.items():
            op = col.operator("object.hide_collisions", icon='HIDE_OFF', text='')
            op.hide = False
            op.mode = key

        for key, value in visibility_operators.items():
            op = col.operator("object.hide_collisions", icon='HIDE_ON', text='')
            op.hide = True
            op.mode = key

        for key, value in visibility_operators.items():
            op = col.operator("object.select_collisions", icon='RESTRICT_SELECT_OFF', text='')
            op.invert = False
            op.mode = key

        for key, value in visibility_operators.items():
            op = col.operator("object.select_collisions", icon='RESTRICT_SELECT_ON', text='')
            op.invert = True
            op.mode = key

        # Conversion
        layout.separator()
        row = layout.row(align=True)
        row.label(text='Conversion')

        row = layout.row(align=True)
        row.operator('object.convert_to_collider', icon='PHYSICS')
        row = layout.row(align=True)
        row.operator('object.convert_to_mesh', icon='MESH_MONKEY')

        # Create Collider
        layout.separator()

        row = layout.row(align=True)
        row.label(text='Collision Shapes')
        row = layout.row(align=True)
        row.operator("mesh.add_bounding_box", icon='MESH_CUBE')
        row = layout.row(align=True)
        row.operator("mesh.add_bounding_cylinder", icon='MESH_CYLINDER')
        row = layout.row(align=True)
        row.operator("mesh.add_bounding_convex_hull", icon='MESH_ICOSPHERE')
        row = layout.row(align=True)
        row.operator("mesh.add_bounding_sphere", icon='MESH_UVSPHERE')
        row = layout.row(align=True)
        row.operator("mesh.add_mesh_collision", icon='MESH_MONKEY')

        #special Collider Creation
        layout.separator()

        row = layout.row(align=True)
        row.label(text='Complex Opertations')

        prefs = context.preferences.addons["CollisionHelpers"].preferences
        row = layout.row(align=True)
        if prefs.executable_path:
            row.operator("collision.vhacd", text="Convex Decomposition")
        else:
            row.operator("wm.url_open", text="Convex decomposition: Requires V-HACD", icon='ERROR').url = "https://github.com/kmammou/v-hacd"

