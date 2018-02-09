import bpy
import nodeitems_utils
import time

import bpy
from bpy.app.handlers import persistent

from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from nodeitems_utils import NodeCategory, NodeItem
import random
from math import pi

from .grease_pencil import build_tree_from_strokes
from .tree_functions import draw_module, add_splits, grow, add_armature
from .modules import visualize_with_curves
from .wind import wind


def get_tree_parameters_rec(state_list, node):
    if node.bl_idname != "BuildTreeNode":
        state_list += str(node.items())

    else:
        state_list += str(node.seed) + str(node.mesh_type)

    if node.bl_idname == "GreasePencilNode":
        return state_list

    try:
        from_node = node.inputs['Tree'].links[0].from_node
    except:
        return state_list

    if from_node is not None:
        return get_tree_parameters_rec(state_list, from_node)


class ModularTree(NodeTree):
    '''Modular tree Node workflow'''
    bl_idname = 'ModularTreeType'
    bl_label = 'Modular Tree Node Tree'
    bl_icon = 'NODETREE'


class TreeSocket(NodeSocket):
    """Tree socket type"""
    bl_idname = "TreeSocketType"
    bl_label = "Tree Socket"

    default_value = None

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return .125, .571, .125, 1


class SelectionSocket(NodeSocket):
    """Selection socket type"""
    bl_idname = "SelectionSocketType"
    bl_label = "Selection Socket"

    default_value = []

    def draw(self, context, layout, node, text):
        layout.label(text)

    def draw_color(self, context, node):
        return .8, .8, .8, 1

    def get_selection(self):
        if self.is_output:
            return self.node.selection

        if not self.is_linked:
            return []
        else:
            return self.links[0].from_socket.get_selection()


class ModularTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ModularTreeType'


class BuildTreeNode(Node, ModularTreeNode):
    bl_idname = "BuildTreeNode"
    bl_label = "BuildTree"

    mesh_type = bpy.props.EnumProperty(
        items=[('final', 'Final', ''), ('preview', 'Preview', '')],
        name="visualisation",
        default="preview")
    auto_update = BoolProperty(default=False)
    memory = StringProperty(default="")
    seed = IntProperty(default=42)
    armature = BoolProperty(default=False)
    animation = BoolProperty(default=False)
    min_armature_radius = FloatProperty(min=0, default=.3)

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.memory = get_tree_parameters_rec("", self)


    def draw_buttons(self, context, layout):
        layout.prop(self, "mesh_type")
        layout.prop(self, "seed")
        row = layout.row()
        row.prop(self, "auto_update")
        if not self.auto_update:
            row.operator("mod_tree.tree_from_nodes", text='create tree').node_name = self.name

        box = layout.box()
        box.prop(self, "armature")
        if self.armature:
            box.prop(self, "min_armature_radius")
            box.prop(self, "animation")

    def execute(self):
        random.seed(self.seed)
        from_node = self.inputs['Tree'].links[0].from_node
        t0 = time.time()
        tree = from_node.execute()
        t1 = time.time()
        if self.mesh_type == "final":
            draw_module(tree)
        else:
            visualize_with_curves(tree)

        if self.armature:
            amt = add_armature(tree, self.min_armature_radius)
            if self.animation:
                wind(amt)

        t2 = time.time()
        print("creating tree", t1 - t0)
        print("building object", t2 - t1)


class GreasePencilNode(Node, ModularTreeNode):
    bl_idname = "GreasePencilNode"
    bl_label = "Grease Pencil"

    smooth_iterations = IntProperty(min=0, default=1)
    radius = FloatProperty(min=0, default=.7)
    branch_length = FloatProperty(min=.001, default=.6)
    radius_decrease = FloatProperty(min=0, max=.999, default=.97)
    grease_pencil_memory = StringProperty(default="")

    def init(self, context):
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")

    @property
    def selection(self):
        return ["gp_branch"]

    def draw_buttons(self, context, layout):
        properties = ["smooth_iterations", "radius", "radius_decrease", "branch_length"]
        for i in properties:
            layout.prop(self, i)

    def execute(self):

        gp = bpy.context.scene.grease_pencil
        if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(
                gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:

            new_memory = str([[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]) + str(self.smooth_iterations) + str(self.branch_length)
            if self.grease_pencil_memory != new_memory:
                print("updating strokes")
                bpy.ops.mod_tree.connect_strokes(point_dist=self.branch_length, automatic=True, connect_all=True,
                                                 child_stroke_index=1, parent_stroke_index=0, smooth_iterations=self.smooth_iterations)
                self.grease_pencil_memory = str([[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]) + str(self.smooth_iterations) + str(self.branch_length)

            strokes = [[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]
            root = build_tree_from_strokes(strokes, self.radius, self.radius_decrease)
            return root


class SplitNode(Node, ModularTreeNode):
    bl_idname = "SplitNode"
    bl_label = "Split"

    proba = FloatProperty(min=0, max=1, default=.3)
    split_angle = FloatProperty(min=0, max=180, default=45)
    spin = FloatProperty(min=0, max=360, default=45)
    head_size = FloatProperty(min=0.001, max=.999, default=.6)
    offset = IntProperty(min=0, default=0)

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")

    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        properties = ['proba', "split_angle", "spin", "head_size", "offset"]
        row = col = layout.column()
        for i in properties:
            col.prop(self, i)

    def execute(self):
        from_node = self.inputs['Tree'].links[0].from_node
        tree = from_node.execute()
        selection = self.inputs["Selection"].get_selection()
        add_splits(tree, self.proba, selection, self.selection[0], self.split_angle, self.spin/180*pi, self.head_size, self.offset)
        return tree


class GrowNode(Node, ModularTreeNode):
    bl_idname = "GrowNode"
    bl_label = "Grow"

    limit_method = bpy.props.EnumProperty(
        items=[('iterations', 'Iterations', ''), ('radius', 'Radius', '')],
        name="limit method",
        default="radius")

    iterations = IntProperty(min=0, default=5)
    radius = FloatProperty(min=.0005, default=.2)
    branch_length = FloatProperty(min=.001, default=.9)
    split_proba = FloatProperty(min=0, max=1, default=.3)
    split_angle = FloatProperty(min=0, max=180, default=45)
    split_deviation = FloatProperty(min=0, max=7, default=.25)
    split_radius = FloatProperty(min=.01, max=.999, default=.6)
    radius_decrease = FloatProperty(min=0.01, max=.999, default=.97)
    randomness = FloatProperty(default=.1)
    spin = FloatProperty(default=135)
    spin_randomness = FloatProperty(min=0, max=7, default=.1)
    gravity_strength = FloatProperty(default=.1)

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")

    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        properties = ['limit_method', self.limit_method, "branch_length", "split_proba", "split_angle",
                      "split_deviation", "split_radius", "radius_decrease", "randomness", "spin", "spin_randomness",
                      "gravity_strength"]
        row = col = layout.column()
        # layout.prop(self, 'limit_method')
        for i in properties:
            col.prop(self, i)

    def execute(self):
        from_node = self.inputs['Tree'].links[0].from_node
        tree = from_node.execute()
        selection = self.inputs["Selection"].get_selection()
        grow(tree, self.iterations, self.radius, self.limit_method, self.branch_length, self.split_proba,
             self.split_angle, self.split_deviation, self.split_radius, self.radius_decrease, self.randomness,
             self.spin, self.spin_randomness, self.selection[0], selection, self.gravity_strength)
        return tree


class ModularTreeNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ModularTreeType'


inputs = [GreasePencilNode]
tree_functions = [SplitNode, GrowNode]
outputs = [BuildTreeNode]

node_categories = [ModularTreeNodeCategory("inputs", "inputs", items=[NodeItem(i.bl_idname) for i in inputs]),
                   ModularTreeNodeCategory("tree_functions", "tree functions", items=[NodeItem(i.bl_idname) for i in tree_functions]),
                   ModularTreeNodeCategory("outputs", "outputs", items=[NodeItem(i.bl_idname) for i in outputs])]

node_classes_to_register = [ModularTree, TreeSocket, BuildTreeNode, GreasePencilNode, SplitNode, GrowNode]


@persistent
def has_nodes_changed(dummy):
    node = bpy.context.active_node.id_data.nodes.get("BuildTree")
    new_memory = get_tree_parameters_rec("", node)
    # new_memory = "coucou"
    # condition = True
    if node.auto_update and new_memory != node.memory:
        bpy.ops.object.delete(use_global=False)
        node.execute()
        # bpy.ops.mod_tree.tree_from_nodes()

        node.memory = new_memory
        # node.execute()


bpy.app.handlers.frame_change_pre.append(has_nodes_changed)
