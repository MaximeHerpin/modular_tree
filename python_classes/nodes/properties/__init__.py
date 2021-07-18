import bpy
from bpy.utils import register_class, unregister_class
import nodeitems_utils

from .random_property import RandomPropertyNode
from .ramp_property import RampPropertyNode

classes = [RandomPropertyNode, RampPropertyNode]

def register():
    for cls in classes:
        register_class(cls)

def unregister():
    for cls in classes:
        unregister_class(cls)
