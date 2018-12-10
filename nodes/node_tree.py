import bpy
from bpy.types import NodeTree
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from trunk_node import TrunkNode


class ModularTree(NodeTree):
    '''Mtree node editor'''
    bl_idname = 'ModularTreeType'
    bl_label = 'Mtree Node Tree'
    bl_icon = 'NODETREE'




### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.



# our own base class with an appropriate poll function,
# so the categories only show up in our own tree type

nodes = [TrunkNode]

class MtreeNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'CustomTreeType'


Mtree_node_categories = [
    MtreeNodeCategory('Trunk', "Trunk", items=[
        NodeItem("CustomNodeType"),
    ])]


classes = [ModularTree] + nodes