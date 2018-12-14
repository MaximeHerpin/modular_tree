import bpy
from bpy.types import NodeTree, Node, NodeSocket
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from .base_node import BaseNode

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class MtreeNodeTree(NodeTree):
    '''Mtree node editor'''
    bl_idname = 'MtreeNodeTree'
    bl_label = "Mtree Node Tree"
    bl_icon = 'NODETREE'


class TreeSocket(NodeSocket):
    """Tree socket type"""
    bl_idname = "TreeSocketType"
    bl_label = "Tree Socket"

    default_value = None
    def draw(self, context, layout, node, text):
        pass

    def draw_color(self, context, node):
        return .125, .571, .125, 1


class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'MtreeNodeTree'


# all categories in a list
node_categories = [
    # identifier, label, items list
    MyNodeCategory('NODES', "Nodes", items=[
        NodeItem("MtreeTrunk"),
        NodeItem("MtreeParameters"),
        NodeItem("MtreeGrow"),
        NodeItem("MtreeSplit"),
        NodeItem("MtreeBranch"),
    ]),
]
classes = [
    MtreeNodeTree,
    TreeSocket,
]




