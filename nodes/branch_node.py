from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree
import random

class MtreeBranch(Node, BaseNode):
    bl_label = "Branch Node"

    seed = IntProperty()
    amount = IntProperty(min=0, default=20) # number of splits
    split_angle = FloatProperty(min=0, max=1.5, default=.6) # angle of a fork
    max_split_number = IntProperty(min=0, default=3) # number of forks per split
    radius = FloatProperty(min=0, max=1, default=.6) # radius of split
    end_radius = FloatProperty(min=0, max=1, default=0)
    min_height = FloatProperty(min=0, default=3, name="start") # min height at which a split occurs
    
    length = FloatProperty(min=0, default=7) # length of trunk
    shape_start = FloatProperty(min=0, default=1) # length at the base of the tree
    shape_end = FloatProperty(min=0, default=1) # length at the end of the tree
    shape_convexity = FloatProperty(default=.3) # how curved the length will be in function of the height of the branch
    resolution = FloatProperty(min=.002, default=1) # how many loops a branch has
    randomness = FloatProperty(default=.15) # how unregular the branches look
    split_proba = FloatProperty(min=0, max=1, default=.1) # how likely is a branch to fork
    split_flatten = FloatProperty(min=0, max=1, default=.5) # how constraint on the horizontal axis the splits are
    gravity_strength = FloatProperty(default=.3) # how much branches go towards the floor/sky
    floor_avoidance = FloatProperty(min=0, default=1) # how much the branches avoid the floor 


    properties = ["seed", "amount", "split_angle", "max_split_number", "radius", "end_radius", "min_height", "length", "shape_start", "shape_end",
                  "shape_convexity", "resolution", "randomness", "split_proba", "split_flatten", "gravity_strength", "floor_avoidance"]

    def init(self, context):
        self.outputs.new('TreeSocketType', "0")
        self.inputs.new('TreeSocketType', "Tree")
        self.name = MtreeBranch.bl_label

    def draw_buttons(self, context, layout):        
        col = layout.column()
        for i in self.properties:
            col.prop(self, i)
    
    def execute(self, tree, input_node):
        random.seed(self.seed)
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier
        selection = 0 if input_node == None else input_node.id_data.nodes.find(input_node.name)

        tree.add_branches(self.amount, self.split_angle, self.max_split_number, self.radius, self.end_radius, self.min_height,
                           self.length, self.shape_start, self.shape_end, self.shape_convexity, self.resolution,
                           self.randomness, self.split_proba, self.split_flatten, self.gravity_strength, self.floor_avoidance, creator, selection )
        for output in self.outputs:
            ''' here the execute function is called recursively on first ouptut of all nodes, the second output of all nodes, ect'''
            links = output.links
            if len(links) > 0:
                links[0].to_node.execute(tree, self)
            