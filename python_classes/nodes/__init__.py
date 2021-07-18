import bpy
from bpy.utils import register_class, unregister_class
import nodeitems_utils

from . import base_types
from . import sockets
from . import node_categories
from . import tree_function_nodes
from . import properties

def register():
    base_types.register()
    sockets.register()
    tree_function_nodes.register()
    properties.register()
    node_categories.register()

def unregister():
    node_categories.unregister()
    base_types.unregister()
    sockets.unregister()
    properties.unregister()
    tree_function_nodes.unregister()
