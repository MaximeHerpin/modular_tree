import bpy
from ..base_types.node import MtreePropertyNode
from ....m_tree import RandomProperty, PropertyWrapper

class RandomPropertyNode(bpy.types.Node, MtreePropertyNode):
    bl_idname = "mt_RandomPropertyNode"
    bl_label = "Random Value"

    property_type = RandomProperty

    def init(self, context):
        self.add_input("mt_PropertySocket", "min", property_name="min", property_value=.01)
        self.add_input("mt_PropertySocket", "max", property_name="max", property_value=1)
        self.add_output("mt_PropertySocket", "value", is_property=False)
        