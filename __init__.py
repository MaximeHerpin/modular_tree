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

from . import addon_updater_ops
import bpy
import nodeitems_utils
from .nodes import node_classes_to_register, node_categories, get_last_memory_match, get_tree_parameters_rec
from .wind import ModalWindOperator


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
    bl_idname = "3D_VIEW_PT_layout_WIND"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.modal_wind_operator", icon="FORCE_WIND")


class ModalModularTreedOperator(bpy.types.Operator):
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

            new_memory = get_tree_parameters_rec("", self.node)
            level = get_last_memory_match(new_memory, self.node.memory)
            if level > 0:
                bpy.ops.object.delete(use_global=False)
                self.node.memory = new_memory
                self.tree = self.node.execute()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        self.node.auto_update = True
        # self.tree = self.node.execute()
        # self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


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
