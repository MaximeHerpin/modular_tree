import bpy
from .base_types.node import MtreeFunctionNode
from ... m_tree import BranchFunction

class BranchNode(bpy.types.Node, MtreeFunctionNode):
    bl_idname = "mt_BranchNode"
    bl_label = "Branch Node"

    tree_function = BranchFunction

    def init(self, context):
        self.add_input("mt_TreeSocket", "Tree", is_property=False)

        self.add_input("mt_FloatSocket", "Start", min_value=0, max_value=1, property_name="start", property_value=.1)
        self.add_input("mt_FloatSocket", "End", min_value=0, max_value=1, property_name="end", property_value=.95)
        self.add_input("mt_PropertySocket", "Length", min_value=0, property_name="length", property_value=9)
        self.add_input("mt_FloatSocket", "Resolution", min_value=0.0001, property_name="resolution", property_value=3)
        self.add_input("mt_FloatSocket", "Start Radius", min_value=0.0001, property_name="start_radius", property_value=.4)
        self.add_input("mt_FloatSocket", "Randomness", min_value=0.0001, property_name="randomness", property_value=.5)
        self.add_input("mt_FloatSocket", "Gravity Strength", property_name="gravity_strength", property_value=20)
        self.add_input("mt_FloatSocket", "Stiffness", property_name="stiffness", property_value=5)
        self.add_input("mt_FloatSocket", "Up Attraction", property_name="up_attraction", property_value=5)
        self.add_input("mt_FloatSocket", "Phillotaxis", min_value=0, max_value = 360, property_name="phillotaxis", property_value=137.5)
        self.add_input("mt_FloatSocket", "Branches density", min_value=0.0001, property_name="branches_density", property_value=2)
        self.add_input("mt_FloatSocket", "Split radius", min_value=0.0001, property_name="split_radius", property_value=.8)
        self.add_input("mt_FloatSocket", "Start angle", min_value=0, max_value=180, property_name="start_angle", property_value=45)
        self.add_input("mt_FloatSocket", "Split proba", min_value=0, max_value=1, property_name="split_proba", property_value=.5)
        self.add_input("mt_FloatSocket", "Split angle", min_value=0, max_value=180, property_name="split_angle", property_value=35.)

        self.add_output("mt_TreeSocket", "Tree", is_property=False)
        
