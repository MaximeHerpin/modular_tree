import bpy
import os
from bpy.types import Node, Operator
import bmesh
from mathutils import Vector, Matrix
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty, PointerProperty
from .base_node import BaseNode
from .tree_parameters_node import generate_tree_object
from ..tree import MTree
from random import random, seed

class MtreeTwig(Node, BaseNode):
    bl_label = "Twig Node"
    
    seed = IntProperty(default=1)
    length = FloatProperty(min=.01, default=3)
    radius = FloatProperty(min=0.001, default=.15)
    branch_number = IntProperty(min=0, default=6)
    randomness = FloatProperty(default=.7, min=0)
    resolution = FloatProperty(min=.1, default=8)
    gravity_strength = FloatProperty(default=4)
    flatten = FloatProperty(min=0, max=1, default=.6)
    leaf_object = PointerProperty(type=bpy.types.Object)
    leaf_type = EnumProperty(
        items=[('palmate', 'Palmate', ''), ('serrate', 'Serrate', ''), ('palmatisate', 'Palmatisate', ''), ('custom', 'Custom', '')],
        name="leaf type",
        default="palmate")
    leaf_size = FloatProperty(min=0, default=1)

    def init(self, context):
        self.name = MtreeTwig.bl_label

    def draw_buttons(self, context, layout):
        op = layout.operator("object.mtree_twig", text='execute') # will call TwigOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator
        op.node_name = self.name

        layout.prop(self, "seed")
        layout.prop(self, "length")
        layout.prop(self, "radius")
        layout.prop(self, "branch_number")
        layout.prop(self, "randomness")
        layout.prop(self, "resolution")
        layout.prop(self, "gravity_strength")
        layout.prop(self, "flatten")
        layout.prop(self, "leaf_type")
        if self.leaf_type == "custom":
            layout.prop(self, "leaf_object")
        layout.prop(self, "leaf_size")

    def execute(self):
        addon_path = os.path.join( os.path.dirname( __file__ ), '..' )
        leaf_path = addon_path + "/resources/materials.blend\\Object\\"
        material_path = addon_path + "/resources/materials.blend\\Material\\"

        seed(self.seed)

        if bpy.data.materials.get("twig") is None:
            bpy.ops.wm.append(filename="twig", directory=material_path)

        if self.leaf_type != "custom":
            bpy.ops.wm.append(filename=self.leaf_type, directory=leaf_path)
            self.leaf_object = bpy.context.view_layer.objects.selected[-1]

        tree = MTree()
        leaf_candidates = tree.twig(self.radius, self.length, self.branch_number, self.randomness, self.resolution, self.gravity_strength, self.flatten)
        twig_ob = bpy.context.object
        if twig_ob is not None and twig_ob.get("is_twig") is None:
            twig_ob = None
        twig_ob = generate_tree_object(twig_ob, tree, 8, "is_twig")
        twig_ob.active_material = bpy.data.materials.get("twig")
        scatter_object(leaf_candidates, twig_ob, self.leaf_object, self.leaf_size)
        if self.leaf_type != "custom" and self.leaf_object is not None:
            bpy.data.objects.remove(self.leaf_object, do_unlink=True) # delete leaf object


class TwigOperator(Operator):
    """create a branch with leafs"""
    bl_idname = "object.mtree_twig"
    bl_label = " Make Twig"
    bl_options = {"REGISTER", "UNDO"}
 
    node_group_name = StringProperty()
    node_name = StringProperty()

    def execute(self, context):        
        node = bpy.data.node_groups[self.node_group_name].nodes[self.node_name]
        node.execute()
        return {'FINISHED'}


def scatter_object(leaf_candidates, ob, dupli_object, leaf_size):
    if dupli_object == None: # return when leaf object is not specified
        return
    leafs = [] # container for all created leafs
    collection = bpy.context.scene.collection # get scene collection
    for position, direction, length, radius, is_end in leaf_candidates:
        new_leaf = dupli_object.copy() # copy leaf object
        new_leaf.data = new_leaf.data.copy()
        dir_rot = Vector((1,0,0)).rotation_difference(direction) # rotation of new leaf
        
        loc, rot, scale = new_leaf.matrix_world.decompose()
        mat_scale = Matrix() # scale of new leaf
        random_scale = 1 + ((random()-.5) * .4)
        for i in range(3):
            mat_scale[i][i] = scale[i] * random_scale
        new_leaf.matrix_world = (Matrix.Translation(position) @ dir_rot.to_matrix().to_4x4() @ mat_scale)
        c =random()
        color_vertices(new_leaf, (c,c,c,c))
        leafs.append(new_leaf)
        collection.objects.link(new_leaf)
    
    bpy.ops.object.select_all(action='DESELECT') # deselecting everything so no unwanted object will be joined as a leaf
    for leaf in leafs:
        leaf.select_set(state=True) # selecting all leafs
    ob.select_set(state=True) # selecting twig
    bpy.context.view_layer.objects.active = ob # make twig the active object so that leafs are joined to it
    bpy.ops.object.join() # join leafs to twig


def color_vertices(ob, color):
    """paints all vertices of ob to color"""
    mesh = ob.data
    if mesh.vertex_colors:
        vcol_layer = mesh.vertex_colors.active
    else:
        vcol_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            vcol_layer.data[loop_index].color = color
