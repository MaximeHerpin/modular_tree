from bpy.types import Node
import random
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeRoots(Node, BaseNode):
    bl_label = "Roots Node"
    
    seed: IntProperty(default=9, update = BaseNode.property_changed)
    length: FloatProperty(min=0, default=14, update = BaseNode.property_changed) # length of trunk
    resolution: FloatProperty(min=.002, default=2, update = BaseNode.property_changed) # how many loops the trunk has
    split_proba: FloatProperty(min=0, max=1, default=.2, update = BaseNode.property_changed)
    randomness: FloatProperty(min=0, max=0.5, default=.2, update = BaseNode.property_changed) 

    properties = ["seed", "length", "resolution", "split_proba", "randomness"]
    
    def init(self, context):
        self.inputs.new('TreeSocketType', "0")
        self.name = MtreeRoots.bl_label

    def draw_buttons(self, context, layout):        
        col = layout.column()
        for i in self.properties:
            col.prop(self, i)
    
    def execute(self, tree, input_node):
        random.seed(self.seed)
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier

        tree.roots(self.length, self.resolution, self.split_proba, self.randomness, creator)            
