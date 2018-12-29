from bpy.types import Node
import random
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeTrunk(Node, BaseNode):
    bl_label = "Trunk Node"
    
    seed = IntProperty(default=1, update = BaseNode.property_changed)
    length = FloatProperty(min=0, default=25, update = BaseNode.property_changed) # length of trunk
    radius = FloatProperty(min=.0005, default=.5, update = BaseNode.property_changed) # radius of trunk
    end_radius = FloatProperty(min=0, max=1, default=0, update = BaseNode.property_changed) # radius at the end of the trunk
    resolution = FloatProperty(min=.002, default=1, update = BaseNode.property_changed) # how many loops the trunk has
    shape = FloatProperty(min=0.01, default=1, update = BaseNode.property_changed) # how the radius decreases with length
    randomness = FloatProperty(min=0, max=0.5, default=.1, update = BaseNode.property_changed) 
    axis_attraction = FloatProperty(min=0, max=1, default=.25, update = BaseNode.property_changed)

    properties = ["seed", "length", "radius", "end_radius", "resolution", "shape", "randomness", "axis_attraction"]
    
    def init(self, context):
        self.outputs.new('TreeSocketType', "0")

        self.name = MtreeTrunk.bl_label

    def draw_buttons(self, context, layout):        
        col = layout.column()
        for i in self.properties:
            col.prop(self, i)
    
    def execute(self, tree):
        random.seed(self.seed)
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier

        tree.add_trunk(self.length, self.radius, self.end_radius, self.shape, self.resolution, self.randomness, self.axis_attraction, creator)
        for output in self.outputs:
            ''' here the execute function is called recursively on first ouptut of all nodes, the second output of all nodes, ect'''
            links = output.links
            if len(links) > 0:
                links[0].to_node.execute(tree, self)
            