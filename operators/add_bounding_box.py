import bmesh
import bpy
from bpy.types import Operator
from bpy_extras.object_utils import object_data_add
from mathutils import Vector

from CollisionHelpers.operators.object_functions import alignObjects, get_bounding_box
from .add_bounding_primitive import OBJECT_OT_add_bounding_object

#TODO: Material, create if none is defined
#TODO: Keep multi edit selection

def add_box_object(context, vertices, newName):
    """Generate a new object from the given vertices"""
    verts = vertices
    edges = []
    faces = [[0, 1, 2, 3], [7, 6, 5, 4], [5, 6, 2, 1], [0, 3, 7, 4], [3, 2, 6, 7], [4, 5, 1, 0]]

    mesh = bpy.data.meshes.new(name=newName)
    mesh.from_pydata(verts, edges, faces)

    # useful for development when the mesh may be invalid.
    # mesh.validate(verbose=True)
    newObj = object_data_add(context, mesh, operator=None, name=None)  # links to object instance

    return newObj


def generate_box(positionsX, positionsY, positionsZ):
    # get the min and max coordinates for the bounding box
    verts = [
        (max(positionsX), max(positionsY), min(positionsZ)),
        (max(positionsX), min(positionsY), min(positionsZ)),
        (min(positionsX), min(positionsY), min(positionsZ)),
        (min(positionsX), max(positionsY), min(positionsZ)),
        (max(positionsX), max(positionsY), max(positionsZ)),
        (max(positionsX), min(positionsY), max(positionsZ)),
        (min(positionsX), min(positionsY), max(positionsZ)),
        (min(positionsX), max(positionsY), max(positionsZ)),
    ]

    #vertex indizes defining the faces of the cube
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    return verts, faces


def verts_faces_to_bbox_collider(self, context, verts_loc, faces, new_name):
    """Create box collider for selected mesh area in edit mode"""

    active_ob = context.object
    root_collection = context.scene.collection

    # add new mesh
    mesh = bpy.data.meshes.new("Box")
    bm = bmesh.new()

    #create mesh vertices
    for v_co in verts_loc:
        bm.verts.new(v_co)

    #connect vertices to faces
    bm.verts.ensure_lookup_table()
    for f_idx in faces:
        bm.faces.new([bm.verts[i] for i in f_idx])

    # update bmesh to draw properly in viewport
    bm.to_mesh(mesh)
    mesh.update()

    # create new object from mesh and link it to collection
    # print("active_ob.name = " + active_ob.name)
    newCollider = bpy.data.objects.new(new_name, mesh)
    root_collection.objects.link(newCollider)

    scene = context.scene

    if scene.my_space == 'LOCAL':
        newCollider.parent = active_ob
        alignObjects(newCollider, active_ob)

    #TODO: Remove the object mode switch that is called for every object to make this operation faster.
    else:
        bpy.ops.object.mode_set(mode='OBJECT')
        self.custom_set_parent(context, active_ob, newCollider)
        bpy.ops.object.mode_set(mode='EDIT')

    return newCollider


def box_Collider_from_Objectmode(self, context, new_name, obj, i):
    """Create box collider for every selected object in object mode"""
    colliderOb = []

    scene = context.scene

    if scene.my_space == 'LOCAL':
        # create BoundingBox object for collider
        bBox = get_bounding_box(obj)
        newCollider = add_box_object(context, bBox, new_name)

        # set parent
        newCollider.parent = obj

        alignObjects(newCollider, obj)


    # Space == 'Global'
    else:
        context.view_layer.objects.active = obj

        bpy.ops.object.mode_set(mode='EDIT')
        me = obj.data
        # Get a BMesh representation
        bm = bmesh.from_edit_mesh(me)
        used_vertices = self.get_vertices(bm, preselect_all=True)
        positionsX, positionsY, positionsZ = self.get_point_positions(obj, scene.my_space, used_vertices)
        verts_loc, faces = generate_box(positionsX, positionsY, positionsZ)
        newCollider = verts_faces_to_bbox_collider(self, context, verts_loc, faces, new_name)

        bpy.ops.object.mode_set(mode='OBJECT')

        # move pivot to center of mass
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

        self.custom_set_parent(context, obj, newCollider)

    return newCollider


class OBJECT_OT_add_bounding_box(OBJECT_OT_add_bounding_object, Operator):
    """Create a new bounding box object"""
    bl_idname = "mesh.add_bounding_box"
    bl_label = "Add Box Collision"

    def invoke(self, context, event):
        super().invoke(context, event)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        status = super().modal(context, event)
        if status == {'FINISHED'}:
            return {'FINISHED'}
        if status == {'CANCELLED'}:
            return {'CANCELLED'}

        scene = context.scene

        # change bounding object settings
        if event.type == 'G' and event.value == 'RELEASE':
            scene.my_space = 'GLOBAL'
            self.execute(context)

        elif event.type == 'L' and event.value == 'RELEASE':
            scene.my_space = 'LOCAL'
            self.execute(context)

        return {'RUNNING_MODAL'}

    def execute(self, context):

        scene = context.scene

        # CLEANUP
        self.remove_objects(self.new_colliders_list)
        self.new_colliders_list = []
        self.displace_modifiers = []
        # Add the active object to selection if it's not selected. This fixes the rare case when the active Edit mode object is not selected in Object mode.

        if context.object not in self.selected_objects:
            self.selected_objects.append(context.object)

        # Create the bounding geometry, depending on edit or object mode.
        for object_count, obj in enumerate(self.selected_objects):
            object_count += 1

            # skip if invalid object
            if obj is None:
                continue

            # skip non Mesh objects like lamps, curves etc.
            if obj.type != "MESH":
                continue


            context.view_layer.objects.active = obj
            collections = obj.users_collection

            prefs = context.preferences.addons["CollisionHelpers"].preferences
            type_suffix = prefs.boxColSuffix
            new_name = super().collider_name(context,type_suffix, object_count)


            if obj.mode == "EDIT":

                # safety check in case of mode changes between iterating through selected meshes
                if bpy.context.mode != 'EDIT_MESH':
                    bpy.ops.object.mode_set(mode='EDIT')

                me = obj.data
                # Get a BMesh representation
                bm = bmesh.from_edit_mesh(me)
                used_vertices = self.get_vertices(bm, preselect_all=False)

                positionsX, positionsY, positionsZ = self.get_point_positions(obj, scene.my_space, used_vertices)
                verts_loc, faces = generate_box(positionsX, positionsY, positionsZ)
                new_collider = verts_faces_to_bbox_collider(self, context, verts_loc, faces,
                                                            new_name)

                # save collision objects to delete when canceling the operation
                self.new_colliders_list.append(new_collider)
                self.primitive_postprocessing(context, new_collider, self.physics_material_name)
                self.add_to_collections(new_collider, collections)

            else:  # mode == "OBJECT":

                new_collider = box_Collider_from_Objectmode(self, context, new_name, obj, object_count)

                # save collision objects to delete when canceling the operation
                self.new_colliders_list.append(new_collider)
                self.primitive_postprocessing(context, new_collider, self.physics_material_name)
                self.add_to_collections(new_collider, collections)

        return {'RUNNING_MODAL'}
