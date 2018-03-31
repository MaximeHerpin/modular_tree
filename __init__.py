bl_info = {
    "name": "Modular trees",
    "author": "Herpin Maxime",
    "version": (3, 0, 0),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Create natural trees with the node editor",
    "wiki_url": "https://github.com/MaximeHerpin/modular_tree/wiki",
    "tracker_url": "https://github.com/MaximeHerpin/modular_tree/issues/new",
    "category": "Add Mesh"}

import os

from . import addon_updater_ops
from .nodes import node_classes_to_register, node_categories, get_last_memory_match, get_tree_parameters_rec, get_change_level
from .wind import ModalWindOperator, FastWind
from .toolbar_functions import TrunkDisplacement, Twigoperator
from .color_ramp_sampler import ColorRampSampler,ColorRampPanel


import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty

import nodeitems_utils


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


class WindPanel(bpy.types.Panel):
    bl_label = "Modular tree wind"
    bl_idname = "mod_tree.wind_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'


    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mod_tree.modal_wind_operator", icon="FORCE_WIND")
        row.operator("mod_tree.fast_wind", icon="FORCE_WIND")


class DetailsPanel(bpy.types.Panel):
    bl_label = "Tree tools"
    bl_idname = "mod_tree.details_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        layout = self.layout
        layout.operator("mod_tree.bark_materials")
        layout.operator("mod_tree.trunk_displace", icon="MOD_DISPLACE")
        layout.operator("mod_tree.twig")


class ModalModularTreedOperator(Operator):
    """real time tree tweaking"""
    bl_idname = "object.modal_tree_operator"
    bl_label = "Modal Tree Operator"
    _timer = None

    node = None
    tree = None

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            self.node.auto_update = False
            return {'CANCELLED'}

        if event.type == 'TIMER':

            new_memory = get_tree_parameters_rec("", self.node, None)
            # level = get_last_memory_match(new_memory, self.node.memory)
            level = get_change_level(new_memory, self.node.memory)
            if level != "unchanged":
                print(level)
                delete_old_tree(level)
                self.node.memory = new_memory
                self.tree = self.node.execute(level, self.tree)
                if self.tree is None:
                    self.report({'ERROR'}, "Invalid Node Tree")
                    self.node.auto_update = False
                    return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        self.node.auto_update = True
        delete_old_tree(level="gen")
        self.tree = self.node.execute()
        # self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        self.node.auto_update = False
        wm.event_timer_remove(self._timer)


class MakeTreeFromNodes(Operator):
    """makes a tree from a node group"""
    bl_idname = "mod_tree.tree_from_nodes"
    bl_label = " Make Tree"
    bl_options = {"REGISTER", "UNDO"}

    node_group_name = StringProperty()
    node_name = StringProperty()

    def draw(self, context):
        pass

    def execute(self, context):
        delete_old_tree()
        # node = bpy.data.node_groups.get("NodeTree.002").nodes.get("BuildTree")
        node = context.active_node.id_data.nodes.get("BuildTree")
        tree = node.execute()
        if tree is None:
            self.report({'ERROR'}, "Invalid Node Tree")
            node.auto_update = False
            return {'CANCELLED'}


        # bpy.ops.object.subdivision_set(level=1)

        return {'FINISHED'}


class VisualizeWithCurves(Operator):
    """makes a tree from a node group"""
    bl_idname = "mod_tree.visualize"
    bl_label = " visualize Tree"
    bl_options = {"REGISTER", "UNDO"}

    node_group_name = StringProperty()
    node_name = StringProperty()

    def draw(self, context):
        pass

    def execute(self, context):
        bpy.ops.object.delete(use_global=False)
        print("tree")
        print(self.node_name)
        print(self.node_group_name)
        node = bpy.data.node_groups.get("NodeTree.002").nodes.get("BuildTree")
        node.execute()

        # bpy.ops.object.subdivision_set(level=1)

        return {'FINISHED'}


def delete_old_tree(level="gen"):
    obj = bpy.context.object
    bpy.ops.object.select_all(action='DESELECT')
    if obj is not None:# and obj.select: #and obj.get("is_tree") is not None:
        print(obj.select)
        if level == "gen":
            print("selecting")
            obj.select = True
        if obj.get("amt") is not None and level in {"amt", "gen"}:
            amt = bpy.context.scene.objects.get(obj.get("amt"))
            if amt is not None:
                amt.select = True
        if obj.get("emitter") is not None and level in {"emitter", "gen"}:
            emitter = bpy.context.scene.objects.get(obj.get("emitter"))
            if emitter is not None:
                emitter.select = True
    bpy.ops.object.delete(use_global=False)


def register():
    addon_updater_ops.register(bl_info)
    nodeitems_utils.register_node_categories("MODULAR_TREE_NODES", node_categories)
    bpy.utils.register_module(__name__)


def unregister():
    addon_updater_ops.unregister()
    nodeitems_utils.unregister_node_categories("MODULAR_TREE_NODES")
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
