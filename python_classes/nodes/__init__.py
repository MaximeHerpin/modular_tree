import bpy
from bpy.utils import register_class, unregister_class
import nodeitems_utils

from . import base_types
from . import sockets
from . import node_categories

from .branch_node import BranchNode
from .tree_mesher_node import TreeMesherNode
from .trunk_node import TrunkNode

classes = [BranchNode, TreeMesherNode, TrunkNode]

def register():
    base_types.register()
    sockets.register()
    for cls in classes:
        register_class(cls)
    node_categories.register()

def unregister():
    node_categories.unregister()
    base_types.unregister()
    sockets.unregister()
    for cls in classes:
        unregister_class(cls)
