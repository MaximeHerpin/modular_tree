from bpy.utils import register_class, unregister_class
from gpu_extras.batch import batch_for_shader
import time
import bpy
import bmesh
import gpu
import numpy as np

from .. import m_tree
from .resources.node_groups import distribute_leaves


class ExecuteNodeFunction(bpy.types.Operator):
    bl_idname = "mtree.node_function"
    bl_label = "Node Function callback"
    bl_options = {'REGISTER', 'UNDO'}

    node_tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    function_name : bpy.props.StringProperty()

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_name]
        getattr(node, self.function_name)()
        return {'FINISHED'}


class AddLeavesModifier(bpy.types.Operator):
    bl_idname = "mtree.add_leaves"
    bl_label = "Add leaves distribution modifier to tree"
    bl_options = {'REGISTER', 'UNDO'}

    object_id: bpy.props.StringProperty()

    def execute(self, context):
        ob = bpy.data.objects.get(self.object_id)
        if ob is not None:
            distribute_leaves(ob)
        return {'FINISHED'}


def register():
    register_class(ExecuteNodeFunction)
    register_class(AddLeavesModifier)

def unregister():
    unregister_class(ExecuteNodeFunction)
    unregister_class(AddLeavesModifier)
