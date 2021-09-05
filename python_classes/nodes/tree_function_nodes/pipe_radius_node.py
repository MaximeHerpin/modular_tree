import bpy
from ..base_types.node import MtreeFunctionNode
from ....m_tree import PipeRadiusFunction

class PipeRadiusNode(bpy.types.Node, MtreeFunctionNode):
    bl_idname = "mt_PipeRadiusNode"
    bl_label = "Radius Override"


    tree_function = PipeRadiusFunction

    def init(self, context):
        self.add_input("mt_TreeSocket", "Tree", is_property=False)

        self.add_input("mt_FloatSocket", "End Radius", min_value=0.0001, property_name="end_radius", property_value=.01)
        self.add_input("mt_FloatSocket", "Constant Growth", min_value=0, property_name="constant_growth", property_value=.2)
        self.add_input("mt_FloatSocket", "Accumulation Power", min_value=0.1, property_name="power", property_value=2.5)

        self.add_output("mt_TreeSocket", "Tree", is_property=False)
