bl_info = {
    "name": "Modular trees",
    "author": "Herpin Maxime",
    "version": (3, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Generates an organic tree with correctly modeled branching.",
    "warning": "Unstable branch, use at your own risk !",
    "wiki_url": "https://github.com/MaximeHerpin/modular_tree/wiki",
    "tracker_url": "https://github.com/MaximeHerpin/modular_tree/issues/new",
    "category": "Add Mesh"}

import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty, PointerProperty
import nodeitems_utils

from .nodes import node_classes_to_register, node_categories
from .generator_operators import MakeTreeFromNodes
from .wind import ModalWindOperator

class WindPanel(bpy.types.Panel):
    bl_label = "Modular tree wind"
    bl_idname = "3D_VIEW_PT_layout_WIND"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.modal_wind_operator", icon="FORCE_WIND")



classes_to_register = [MakeTreeFromNodes]
classes_to_register += node_classes_to_register


def register():
    nodeitems_utils.register_node_categories("MODULAR_TREE_NODES", node_categories)

    bpy.utils.register_module(__name__)

    # for i in classes_to_register:
    #     bpy.utils.register_class(i)


def unregister():
    nodeitems_utils.unregister_node_categories("MODULAR_TREE_NODES")
    bpy.utils.unregister_module(__name__)
    # for i in classes_to_register:
    #     bpy.utils.unregister_class(i)


if __name__ == "__main__":
    register()
