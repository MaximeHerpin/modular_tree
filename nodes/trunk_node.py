from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeTrunk(Node, BaseNode):
    bl_label = "Trunk Node"
    
    length = FloatProperty(min=0, default=7) # length of trunk
    radius = FloatProperty(min=.0005, default=.8) # radius of trunk
    resolution = FloatProperty(min=.002, default=1) # how many loops the trunk has
    shape = FloatProperty(min=0.01, default=1) # how the radius decreases with length
    randomness = FloatProperty(default=.1) 
    up_attraction = FloatProperty(default=.7)

    def init(self, context):
        self.outputs.new('TreeSocketType', "Tree")

        self.name = MtreeTrunk.bl_label

    def draw_buttons(self, context, layout):        
        properties = ["length", "radius", "resolution", "shape", "randomness", "randomness", "up_attraction"]
        col = layout.column()
        for i in properties:
            col.prop(self, i)
    
    def execute(self, tree):
        tree.add_trunk(self.length, self.radius, self.shape, self.resolution, self.randomness, 0)
        links = self.outputs["Tree"].links
        print("trunk has been executed")
        if len(links) > 0:
            links[0].to_node.execute(tree)
            