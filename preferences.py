import bpy
from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)

class CollisionAddonPrefs(bpy.types.AddonPreferences):
    """Contains the blender addon preferences"""
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__  ### __package__ works on multifile and __name__ not

    meshColSuffix: bpy.props.StringProperty(name="Mesh", default="_MESH")
    convexColSuffix: bpy.props.StringProperty(name="Convex Suffix", default="_CONVEX")
    boxColSuffix: bpy.props.StringProperty(name="Box Suffix", default="_BOX")
    colPreSuffix: bpy.props.StringProperty(name="Collision", default="_COL")
    colSuffix: bpy.props.StringProperty(name="Collision", default="_SIMULATION_SCENE")

    props = [
        "meshColSuffix",
        "convexColSuffix",
        "boxColSuffix",
        "colPreSuffix",
        "colSuffix",
    ]

    # here you specify how they are drawn
    def draw(self, context):
        layout = self.layout
        for propName in self.props:
            raw = layout.row()
            raw.prop(self, propName)
