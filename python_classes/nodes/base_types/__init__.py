import bpy
from bpy.utils import register_class, unregister_class
from .node_tree import MtreeNodeTree

classes = [MtreeNodeTree]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in reversed(classes):
        unregister_class(cls)