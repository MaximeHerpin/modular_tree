import bpy
from bpy.utils import register_class, unregister_class
from .float_socket import MtreeFloatSocket
from .tree_socket import TreeSocket

classes = [MtreeFloatSocket, TreeSocket]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)