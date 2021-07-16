from bpy.types import Node
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree
import random

class MtreeGrow(Node, BaseNode):
    bl_label = "Grow Node"

    seed: IntProperty()   
    length: FloatProperty(min=0, default=7, update = BaseNode.property_changed) # length of trunk
    shape_start: FloatProperty(min=0, default=.5, update = BaseNode.property_changed) # length at the base of the tree
    shape_end: FloatProperty(min=0, default=.5, update = BaseNode.property_changed) # length at the end of the tree
    shape_convexity: FloatProperty(default=1, update = BaseNode.property_changed) # how curved the length will be in function of the height of the branch
    resolution: FloatProperty(min=.002, default=1, update = BaseNode.property_changed) # how many loops a branch has
    randomness: FloatProperty(default=.1, update = BaseNode.property_changed) # how unregular the branches look
    split_proba: FloatProperty(min=0, max=1, default=.1, update = BaseNode.property_changed) # how likely is a branch to fork
    split_angle: FloatProperty(min=0, max=1, default=.3, update = BaseNode.property_changed) # angle of a fork
    split_radius: FloatProperty(min=0, max=1, default=.9, update = BaseNode.property_changed) # radius of forked branches
    split_flatten: FloatProperty(min=0, max=1, default=.5, update = BaseNode.property_changed) # how constraint on the horizontal axis the splits are
    end_radius: FloatProperty(min=0, max=1, default=0, update = BaseNode.property_changed) # the relative radius of vranches at the end of growth
    can_spawn_leafs: BoolProperty(default=True, update = BaseNode.property_changed)
    gravity_strength: FloatProperty(default=.1, update = BaseNode.property_changed) # how much branches go towards the floor/sky
    floor_avoidance: FloatProperty(min=0, default=1, update = BaseNode.property_changed) # how much the branches avoid the floor

    properties = ["seed", "length", "shape_start", "shape_end", "shape_convexity", "resolution", "randomness",
                  "split_proba", "split_angle", "split_radius", "split_flatten", "end_radius", "can_spawn_leafs", "gravity_strength", "floor_avoidance"]

    def init(self, context):
        self.outputs.new('TreeSocketType', "0")
        self.inputs.new('TreeSocketType', "Tree")
        self.name = MtreeGrow.bl_label

    def draw_buttons(self, context, layout):        
        col = layout.column()
        for i in self.properties:
            col.prop(self, i)
    
    def execute(self, tree, input_node):
        random.seed(self.seed)
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier
        selection = 0 if input_node == None else input_node.id_data.nodes.find(input_node.name)

        tree.grow(self.length, self.shape_start, self.shape_end, self.shape_convexity, self.resolution,
                  self.randomness, self.split_proba, self.split_angle, self.split_radius, self.split_flatten,
                  self.end_radius, self.gravity_strength, self.floor_avoidance, self.can_spawn_leafs, creator, selection)
        for output in self.outputs:
            ''' here the execute function is called recursively on first ouptut of all nodes, the second output of all nodes, ect'''
            links = output.links
            if len(links) > 0:
                links[0].to_node.execute(tree, self)
            
