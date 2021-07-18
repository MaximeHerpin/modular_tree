import bpy
from bpy.utils import register_class, unregister_class
import nodeitems_utils

from .branch_node import BranchNode
from .tree_mesher_node import TreeMesherNode
from .trunk_node import TrunkNode

classes = [BranchNode, TreeMesherNode, TrunkNode]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)
