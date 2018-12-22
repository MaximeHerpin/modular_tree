import bpy
from bpy.types import Node, Operator
import bmesh
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeParameters(Node, BaseNode):
    bl_label = "Tree paramteters"
    
    resolution = IntProperty(min=0, default=16)

    def init(self, context):
        self.name = MtreeParameters.bl_label

    def draw_buttons(self, context, layout):
        layout.prop(self, "resolution")
        op = layout.operator("object.mtree_execute_tree", text='execute') # will call ExecuteMtreeNodeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator

    def execute(self):
        tree = MTree()
        node_tree = self.id_data
        trunk = [node for node in node_tree.nodes if node.bl_idname == "MtreeTrunk"][0] # get trunk function
        # TODO : check that there is only one trunk node
        trunk.execute(tree)
        print("-"*50)
        ob = bpy.context.object
        ob = generate_tree_object(ob, tree, self.resolution)

        leaf_ob = generate_leafs_object(tree, 5000, 0, .2)
        leaf_ob.parent = ob
        


def generate_tree_object(ob, tree, resolution):
    verts, faces, radii, uvs = tree.build_mesh_data(resolution)
    mesh = bpy.data.meshes.new("tree")
    mesh.from_pydata(verts, [], faces)
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    bm.loops.layers.uv.new()
    uv_layer = bm.loops.layers.uv.active
    for index, face in enumerate(bm.faces):
        for j, loop in enumerate(face.loops):
            loop[uv_layer].uv = uvs[index][j]

    bm.to_mesh(mesh)
    bm.free()

    ob.data = mesh
    for i in ob.vertex_groups:
        ob.vertex_groups.remove(i)
    v_group = ob.vertex_groups.new() # adding radius vertex group
    for v, w in radii:
        v_group.add(v, w, "ADD")
    return ob

def generate_leafs_object(tree, number, weight, max_radius, ob=None):
    mesh = bpy.data.meshes.new("leafs")
    if ob == None:
        ob = bpy.data.objects.new('leafs', mesh) 
        bpy.context.scene.collection.objects.link(ob)
    
    verts, faces = tree.get_leaf_emitter_data(number, weight, max_radius)
    ob.data.from_pydata(verts, [], faces)
    return ob


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