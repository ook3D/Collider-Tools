import bpy

from . import add_bounding_box
from . import add_bounding_convex_hull
from . import add_bounding_cylinder
from . import add_bounding_primitive
from . import add_bounding_sphere
from . import add_collision_mesh
from . import add_minimum_bounding_box
from . import conversion_operators
from . import user_groups
from . import visibility_selection_deletion
from . import visibility_settings

default_groups_enum = [('ALL_COLLIDER', "Colliders", "Show/Hide all objects that are colliders.", '', 1),
                       ('OBJECTS', "Non Colliders", "Show/Hide all objects that are not colliders.", '', 2),
                       ('USER_01', "User Group 01",
                        "Show/Hide all objects that are part of User Group 01", '', 4),
                       ('USER_02', "User Group 02", "Show/Hide all objects that are part of User Group 02", '', 8),
                       ('USER_03', "User Group 03", "Show/Hide all objects that are part of User Group 03", '', 16)]


def update_hide(self, context):
    print("self.hide = " + str(self.hide))
    for ob in bpy.context.view_layer.objects:
        if self.mode == 'ALL_COLLIDER':
            if ob.get('isCollider') == True:
                ob.hide_viewport = self.hide
        elif self.mode == 'OBJECTS':
            if not ob.get('isCollider'):
                ob.hide_viewport = self.hide
        else:  # if self.mode == 'USER_02' or self.mode == 'USER_03'
            if ob.get('isCollider') and ob.get('collider_type') == self.mode:
                ob.hide_viewport = self.hide


def update_selected(self, context):
    print("self.selected = " + str(self.selected))
    for ob in bpy.data.objects:
        if self.mode == 'ALL_COLLIDER':
            if ob.get('isCollider'):
                ob.select_set(self.selected)
            else:
                ob.select_set(not self.selected)
        elif self.mode == 'OBJECTS':
            if not ob.get('isCollider'):
                ob.select_set(self.selected)
            else:
                ob.select_set(not self.selected)
        else:  # if self.mode == 'USER_02' or self.mode == 'USER_03'
            if ob.get('isCollider') and ob.get('collider_type') == self.mode:
                ob.select_set(self.selected)
            else:
                ob.select_set(not self.selected)


def update_display_colliders(self, context):
    for obj in bpy.data.objects:
        if obj.get('isCollider'):
            obj.display_type = self.display_type
    return {'FINISHED'}


class ColliderGroup(bpy.types.PropertyGroup):

    def get_groups_enum(self):
        '''Set name and description according to type'''
        for group in default_groups_enum:
            if group[4] == self["mode"]:
                from .user_groups import get_complexity_name
                from .user_groups import get_complexity_suffix
                from .user_groups import get_group_color
                # self.identifier = get_complexity_suffix(group[0])
                self.name = get_complexity_name(group[0])
                self.identifier = get_complexity_suffix(group[0])
                self.icon = group[3]
                color = get_group_color(group[0])
                self.color = color[0], color[1], color[2]

        return self["mode"]

    def set_groups_enum(self, val):
        self["mode"] = val
        # ColliderGroup.mode.val = str(val)

    mode: bpy.props.EnumProperty(name="Group",
                                 items=default_groups_enum,
                                 description="",
                                 default='ALL_COLLIDER',
                                 get=get_groups_enum,
                                 set=set_groups_enum
                                 )

    name: bpy.props.StringProperty()
    identifier: bpy.props.StringProperty()
    icon: bpy.props.StringProperty()

    color: bpy.props.FloatVectorProperty(name="Color",
                                         subtype='COLOR',
                                         options={'TEXTEDIT_UPDATE'},
                                         size=3,
                                         default=[0.0, 0.0, 0.0])

    hide: bpy.props.BoolProperty(default=False, update=update_hide,
                                 name='Disable in Viewport',
                                 description="Show/Hide all objects that are not colliders.")

    select: bpy.props.BoolProperty(default=False, name="Select/Deselect", update=update_selected)

    show_icon: bpy.props.StringProperty(default='RESTRICT_VIEW_OFF')
    hide_icon: bpy.props.StringProperty(default='RESTRICT_VIEW_ON')

    show_text: bpy.props.StringProperty(default='')
    hide_text: bpy.props.StringProperty(default='')

    # select_icon: bpy.props.StringProperty(default='NONE')
    # deselect_icon: bpy.props.StringProperty(default='NONE')
    # select_text: bpy.props.StringProperty(default='Select')
    # deselect_text: bpy.props.StringProperty(default='Deselect')

    select_icon: bpy.props.StringProperty(default='RESTRICT_SELECT_ON')
    deselect_icon: bpy.props.StringProperty(default='RESTRICT_SELECT_OFF')
    select_text: bpy.props.StringProperty(default='')
    deselect_text: bpy.props.StringProperty(default='')

    delete_icon: bpy.props.StringProperty(default='TRASH')
    delete_text: bpy.props.StringProperty(default='')


classes = (
    ColliderGroup,
    add_bounding_box.OBJECT_OT_add_bounding_box,
    add_minimum_bounding_box.OBJECT_OT_add_aligned_bounding_box,
    add_bounding_cylinder.OBJECT_OT_add_bounding_cylinder,
    add_bounding_sphere.OBJECT_OT_add_bounding_sphere,
    add_bounding_convex_hull.OBJECT_OT_add_convex_hull,
    add_collision_mesh.OBJECT_OT_add_mesh_collision,
    visibility_selection_deletion.COLLISION_OT_Visibility,
    visibility_selection_deletion.COLLISION_OT_Selection,
    conversion_operators.OBJECT_OT_convert_to_collider,
    conversion_operators.OBJECT_OT_convert_to_mesh,
    user_groups.COLLISION_OT_assign_user_group,
    visibility_selection_deletion.COLLISION_OT_Deletion,
    visibility_selection_deletion.COLLISION_OT_simple_select,
    visibility_selection_deletion.COLLISION_OT_simple_deselect,
    visibility_selection_deletion.COLLISION_OT_simple_delete,
    visibility_selection_deletion.COLLISION_OT_complex_select,
    visibility_selection_deletion.COLLISION_OT_complex_deselect,
    visibility_selection_deletion.COLLISION_OT_complex_delete,
    visibility_selection_deletion.COLLISION_OT_simple_complex_select,
    visibility_selection_deletion.COLLISION_OT_simple_complex_deselect,
    visibility_selection_deletion.COLLISION_OT_simple_complex_delete,
    visibility_selection_deletion.COLLISION_OT_all_select,
    visibility_selection_deletion.COLLISION_OT_all_deselect,
    visibility_selection_deletion.COLLISION_OT_all_delete,
    visibility_selection_deletion.COLLISION_OT_non_collider_select,
    visibility_selection_deletion.COLLISION_OT_non_collider_deselect,
    visibility_selection_deletion.COLLISION_OT_non_collider_delete,
    visibility_selection_deletion.COLLISION_OT_simple_show,
    visibility_selection_deletion.COLLISION_OT_simple_hide,
    visibility_selection_deletion.COLLISION_OT_complex_show,
    visibility_selection_deletion.COLLISION_OT_complex_hide,
    visibility_selection_deletion.COLLISION_OT_simple_complex_show,
    visibility_selection_deletion.COLLISION_OT_simple_complex_hide,
    visibility_selection_deletion.COLLISION_OT_all_show,
    visibility_selection_deletion.COLLISION_OT_all_hide,
    visibility_selection_deletion.COLLISION_OT_non_collider_show,
    visibility_selection_deletion.COLLISION_OT_non_collider_hide,
    visibility_selection_deletion.COLLISION_OT_toggle_collider_visibility,
    visibility_settings.VIEW3D_OT_object_view,
    visibility_settings.VIEW3D_OT_material_view,
)


def register():
    scene = bpy.types.Scene
    obj = bpy.types.Object

    # Display setting of the bounding object in the viewport
    scene.my_hide = bpy.props.BoolProperty(name="Hide After Creation",
                                           description="Hide Bounding Object After Creation.", default=False)

    # Tranformation space to be used for creating the bounding object.
    scene.my_space = bpy.props.EnumProperty(name="Generation Axis",
                                            items=(('LOCAL', "Local",
                                                    "Generate the collision based on the local space of the object vertices."),
                                                   ('GLOBAL', "Global",
                                                    "Generate the collision based on the global space of the object vertices.")),
                                            default="LOCAL")

    scene.display_type = bpy.props.EnumProperty(name="Collider Display",
                                                items=(
                                                    ('SOLID', "Solid", "Display the colliders as solid"),
                                                    ('WIRE', "Wire", "Display the colliders as wireframe"),
                                                ),
                                                default="SOLID",
                                                update=update_display_colliders)

    scene.wireframe_mode = bpy.props.EnumProperty(name="Wireframe Mode",
                                                  items=(('OFF', "Off",
                                                          "There is no wireframe preview on the collision mesh."),
                                                         ('PREVIEW', "Preview",
                                                          "The wireframes are only visible during the generation."),
                                                         ('ALWAYS', "Always",
                                                          "The wireframes remain visible afterwards.")),
                                                  description="Hide Bounding Object After Creation.", default='PREVIEW')

    # OBJECT
    obj.basename = bpy.props.StringProperty(default='geo', name='Basename',
                                            description='Default naming used for collisions when the name is not inherited from a parent (Name from parent is disabled).')

    obj.collider_type = bpy.props.EnumProperty(name="Shading",
                                               items=[('BOX', "Box", "Used to descibe boxed shape collision shapes."),
                                                      (
                                                          'SHERE', "Sphere",
                                                          "Used to descibe spherical collision shapes."),
                                                      ('CONVEX', "CONVEX",
                                                       "Used to descibe convex shaped collision shapes."),
                                                      ('MESH', "Triangle Mesh",
                                                       "Used to descibe complex triangle mesh collisions.")],
                                               default='BOX')

    obj.collider_complexity = bpy.props.EnumProperty(name="collider complexity", items=[
        ('USER_01', "Simple Complex",
         "(Simple and Complex) Custom value to distinguish different types of collisions in a game engine."),
        ('USER_02', "Simple", "(Simple) Custom value to distinguish different types of collisions in a game engine."),
        (
            'USER_03', "Complex",
            "(Complex) Custom value to distinguish different types of collisions in a game engine.")],
                                                     default="USER_01")

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    scene.visibility_toggle_list = []

    # # Pointer Properties have to be initialized after classes
    scene.visibility_toggle_all = bpy.props.PointerProperty(type=ColliderGroup)
    scene.visibility_toggle_obj = bpy.props.PointerProperty(type=ColliderGroup)
    scene.visibility_toggle_user_group_01 = bpy.props.PointerProperty(type=ColliderGroup)
    scene.visibility_toggle_user_group_02 = bpy.props.PointerProperty(type=ColliderGroup)
    scene.visibility_toggle_user_group_03 = bpy.props.PointerProperty(type=ColliderGroup)


def unregister():
    scene = bpy.types.Scene
    obj = bpy.types.Object

    del scene.visibility_toggle_user_group_03
    del scene.visibility_toggle_user_group_02
    del scene.visibility_toggle_user_group_01
    del scene.visibility_toggle_obj
    del scene.visibility_toggle_all

    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)

    # delete custom properties on unregister
    del scene.wireframe_mode
    del scene.my_space
    del scene.my_hide

    del obj.collider_complexity
    del obj.collider_type
    del obj.basename
