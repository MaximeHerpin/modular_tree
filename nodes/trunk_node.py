from bpy.types import Node, Operator
import bpy
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
    use_grease_pencil = BoolProperty(default=False, update = BaseNode.property_changed)

    properties = ["seed", "length", "radius", "end_radius", "resolution", "shape", "randomness", "axis_attraction", "use_grease_pencil"]
    
    def init(self, context):
        self.outputs.new('TreeSocketType', "0")

        self.name = MtreeTrunk.bl_label

    def draw_buttons(self, context, layout):  
        col = layout.column()
        col.prop(self, "use_grease_pencil")
        if self.use_grease_pencil:
            col.prop(self, "radius")
            col.prop(self, "resolution")
            op = layout.operator("mtree.update_gp_strokes", text="update strokes") # will call ExecuteMtreeNodeTreeOperator.execute
            op.node_group_name = self.id_data.name # set name of node group to operator
        else:
            for i in self.properties[:-1]:
                col.prop(self, i)
        
    def execute(self, tree):
        creator = self.id_data.nodes.find(self.name) # get index of node in node tree and use it as tree function identifier
        if self.use_grease_pencil:
            tree.build_tree_from_grease_pencil(.4/self.resolution, self.radius, creator)
        else:
            random.seed(self.seed)
            tree.add_trunk(self.length, self.radius, self.end_radius, self.shape, self.resolution, self.randomness, self.axis_attraction, creator)

        for output in self.outputs:
            ''' here the execute function is called recursively on first ouptut of all nodes, the second output of all nodes, ect'''
            links = output.links
            if len(links) > 0:
                links[0].to_node.execute(tree, self)


class UpdateGreasePencil(Operator):
    """Update grease pencil strokes"""
    bl_idname = "mtree.update_gp_strokes"
    bl_label = "Reset Active Tree Object"
    
    node_group_name = StringProperty()

    def execute(self, context):
        parameters_node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        parameters_node.has_changed = True
        parameters_node.execute()
        return {'FINISHED'}