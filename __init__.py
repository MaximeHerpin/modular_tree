# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Mtree",
    "author": "Maxime Herpin",
    "version": (3, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Create natural trees with the node editor",
    "wiki_url": "https://github.com/MaximeHerpin/modular_tree/wiki",
    "tracker_url": "https://github.com/MaximeHerpin/modular_tree/issues/new",
    "category": "Add Mesh"}

import os
from .nodes import nodes_classes
from . import addon_updater_ops
# from .toolbar_functions import TrunkDisplacement, Twigoperator
# from .color_ramp_sampler import ColorRampSampler,ColorRampPanel

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
import nodeitems_utils
import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

from .wind import FastWind
from .grease_pencil import ConnectStrokes



classes = [FastWind, ConnectStrokes]
classes += nodes_classes

class Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout
        addon_updater_ops.update_settings_ui(self, context)

classes += [Preferences]
# class WindPanel(bpy.types.Panel):
#     bl_label = "Modular tree wind"
#     bl_idname = "mod_tree.wind_panel"
#     bl_space_type = 'VIEW_3D'
#     bl_region_type = 'TOOLS'
#     bl_context = "objectmode"
#     bl_category = 'Tree'


#     def draw(self, context):
#         layout = self.layout
#         row = layout.row()
#         row.operator("mod_tree.modal_wind_operator", icon="FORCE_WIND")
#         row.operator("mod_tree.fast_wind", icon="FORCE_WIND")



def register():
    addon_updater_ops.register(bl_info)

    from bpy.utils import register_class
    from .nodes.node_tree import node_categories
    for cls in classes:
        register_class(cls)

    nodeitems_utils.register_node_categories('MTREE_NODES', node_categories)


def unregister():
    addon_updater_ops.unregister()
    nodeitems_utils.unregister_node_categories('MTREE_NODES')

    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

# if __name__ == "__main__":
#     register()
