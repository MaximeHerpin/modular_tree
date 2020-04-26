import bpy
from .base_types.node import MtreeFunctionNode
from ... m_tree import TrunkFunction

class TrunkNode(bpy.types.Node, MtreeFunctionNode):
    bl_idname = "mt_TrunkNode"
    bl_label = "Trunk Node"

    test : bpy.props.FloatProperty(name = "test")

    radius : bpy.props.FloatProperty(min=.001, default=.3)
    resolution : bpy.props.FloatProperty(min=.001, default=1)

    exposed_parameters = ["radius", "resolution"]

    tree_function = TrunkFunction

    def init(self, context):
        self.add_input("mt_TreeSocket", "Tree", is_property=False)

        self.add_input("mt_FloatSocket", "Length", min_value=0, property_name="length", property_value=7)

        self.add_output("mt_TreeSocket", "Tree", is_property=False)
