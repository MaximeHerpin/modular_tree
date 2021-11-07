import os
import bpy

from .resource_utils import ResourceUtils


def distribute_leaves(ob):
    if ob.modifiers.get("leaves") is not None:
        return
    modifier = ob.modifiers.new("leaves", 'NODES')
    modifier.node_group = ResourceUtils.append_geo_node("leaves_distribution")