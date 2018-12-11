import bpy
from bpy.types import Node, Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeParameters(Node, BaseNode):
    bl_label = "Tree paramteters"
    

    def init(self, context):
        self.name = MtreeParameters.bl_label

    def draw_buttons(self, context, layout):
        op = layout.operator("object.mtree_execute_tree", text='execute') # will call ExecuteMtreeNodeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator

    def execute(self):
        tree = MTree()
        node_tree = self.id_data
        trunk = [node for node in node_tree.nodes if node.bl_idname == "MtreeTrunk"][0] # get trunk function
        # TODO : check that there is only one trunk node
        trunk.execute(tree)
        verts, faces = tree.build_mesh_data()
        ob = bpy.context.object
        mesh = bpy.data.meshes.new("test")
        mesh.from_pydata(verts, [], [])
        ob.data = mesh
    

class ExecuteMtreeNodeTreeOperator(Operator):

    bl_idname = "object.mtree_execute_tree"
    bl_label = "Execute Mtree node tree"
    node_group_name = StringProperty()

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        node.execute()
        return {'FINISHED'}