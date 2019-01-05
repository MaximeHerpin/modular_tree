from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree
import random

class MtreeSplit(Node, BaseNode):
    bl_label = "Split Node"
    
    seed = IntProperty(update = BaseNode.property_changed)
    amount = IntProperty(min=0, default=20, update = BaseNode.property_changed) # number of splits
    split_angle = FloatProperty(min=0, max=1.5, default=.6, update = BaseNode.property_changed) # angle of a fork
    max_split_number = IntProperty(min=0, default=3, update = BaseNode.property_changed) # number of forks per split
    radius = FloatProperty(min=0, max=1, default=.6, update = BaseNode.property_changed) # radius of split
    min_height = FloatProperty(min=0, max=1, default=.999, name="start", update = BaseNode.property_changed) # min height at which a split occurs

    properties = ["seed", "amount", "split_angle", "max_split_number", "radius", "min_height"]


    def init(self, context):
        self.outputs.new('TreeSocketType', "0")
        self.inputs.new('TreeSocketType', "Tree")
        self.name = MtreeSplit.bl_label

    def draw_buttons(self, context, layout):        
        col = layout.column()
        for i in self.properties:
            col.prop(self, i)
    
    def execute(self, tree, input_node):
        random.seed(self.seed)
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier
        selection = 0 if input_node == None else input_node.id_data.nodes.find(input_node.name)

        tree.split(self.amount, self.split_angle, self.max_split_number, self.radius, self.min_height, 0, creator, selection)
        for output in self.outputs:
            ''' here the execute function is called recursively on first ouptut of all nodes, the second output of all nodes, ect'''
            links = output.links
            if len(links) > 0:
                links[0].to_node.execute(tree, self)
            