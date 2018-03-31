import os

import bpy
import nodeitems_utils
import time

import bpy
from bpy.app.handlers import persistent

from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty
from nodeitems_utils import NodeCategory, NodeItem
import random
from math import pi, inf

from .grease_pencil import build_tree_from_strokes
from .tree_functions import draw_module, add_splits, grow, add_basic_trunk, add_armature, add_particles_emitter
from .modules import visualize_with_curves


def get_tree_parameters_rec(state_list, node, props_dict):
    if props_dict is None:
        props_dict = {"SplitNode": ['proba', "split_angle", "spin", "head_size", "offset"],
                     "GrowNode": ["limit_method", "branch_length", "split_proba", "randomness", "gravity_strength", "split_angle",
                              "split_deviation", "split_radius", "radius_decrease", "spin", "spin_randomness", "pruning_strength", "shape_factor",
                                  "up_attraction", "iterations", "radius"],
                     "TrunkNode": ["radius", "height", "branch_length", "radius_decrease", "randomness", "up_attraction", "twist"],
                     "GreasePencilNode": ["smooth_iterations", "radius", "radius_decrease", "branch_length"],
                     "BuildTreeNode": ["mesh_type", "resolution_levels", "seed", "auto_update", "scale", "armature", "min_armature_radius", "min_length", "create_particle_emitter",
                                   "dupli_object", "max_radius", "particle_proba", "material"]}
    for prop in props_dict[node.bl_idname]:
        value = getattr(node, prop)
        if type(value) != str:
            value = str(round(value, 3))
        state_list += value + ";"
        # state_list += prop + ' ' + str(round(getattr(node, prop), 3)) + ";"

    state_list += ','
    # else:
    #     state_list += "{};{};{};{};{};{};" str(node.seed) + str(node.mesh_type) + str(node.armature) + str(node.min_length) + ","

    if node.bl_idname == "GreasePencilNode" or node.bl_idname == "TrunkNode":
        return state_list

    try:
        from_node = node.inputs['Tree'].links[0].from_node
    except:
        return state_list

    if from_node is not None:
        return get_tree_parameters_rec(state_list, from_node, props_dict)


def get_change_level(new, old):
    if old == new:
        return "unchanged"

    new = new.split(",")
    old = old.split(",")
    if len(new) != len(old):
        return "gen"

    for i in range(1, len(new)):
        if new[i] != old[i]:
            return "gen"

    new = new[0].split(';')
    old = old[0].split(';')

    for i in range(len(new)):
        if new[i] != old[i]:
            if i < 4:
                return "gen"
            elif i == 4:
                return "scale"
            elif i < 8:
                return "armature"
            elif i < 12:
                return "emitter"
            else:
                return "material"


def get_last_memory_match(new, old):
    new = new.split(",")
    old = old.split(',')
    level = len(new)
    for i in range(min(len(new), len(old))):
        if new[-(i+1)] != old[-(i+1)]:
            break
        level -= 1
    return level


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

    memory = StringProperty(default="")

    mesh_type = bpy.props.EnumProperty(
        items=[('final', 'Final', ''), ('preview', 'Preview', '')],
        name="visualisation",
        default="preview")
    resolution_levels = IntProperty(min=0, default=1)
    seed = IntProperty(default=42)
    auto_update = BoolProperty(default=False)

    scale = FloatProperty(min=.001, default=1)

    armature = BoolProperty(default=False)
    min_armature_radius = FloatProperty(min=0, default=.3)
    min_length = FloatProperty(min=0, default=1)

    create_particle_emitter = BoolProperty(default=False)
    dupli_object = StringProperty(default="")
    max_radius = FloatProperty(default=.2, min=0)
    particle_proba = FloatProperty(default=.5, min=0, max=1)
    material = StringProperty(default="")

    def init(self, context):

        self.inputs.new("TreeSocketType", "Tree")
        self.memory = get_tree_parameters_rec("", self, None)

    def draw_buttons(self, context, layout):
        layout.prop(self, "mesh_type")
        if self.mesh_type == "final":
            layout.prop(self, "resolution_levels")
        layout.prop(self, "seed")
        layout.prop(self, "scale")
        box = layout.row()
        # row.prop(self, "auto_update")
        if self.auto_update:
            box.label("press ESC to stop")

        else:
            box.operator("object.modal_tree_operator", text='auto_update_tree')
            box.operator("mod_tree.tree_from_nodes", text='create tree')

        box = layout.box()
        box.prop(self, "armature")
        if self.armature:
            box.prop(self, "min_armature_radius")
            box.prop(self, "min_length")

        box = layout.box()
        box.prop(self, "create_particle_emitter")
        if self.create_particle_emitter:
            box.prop(self, "max_radius")
            box.prop(self, "particle_proba")
            layout.prop_search(self, "dupli_object", context.scene, "objects")

        layout.prop_search(self, "material", bpy.data, "materials")

    def execute(self, level="gen", old_tree=None):
        random.seed(self.seed)
        try:
            from_node = self.inputs['Tree'].links[0].from_node
        except:
            return None
        t0 = time.time()
        t1 = time.time()
        rebuild = level == "gen"
        if rebuild:
            tree = from_node.execute()
            if tree is None:
                return None
            t1 = time.time()
            if self.mesh_type == "final":
                draw_module(tree, self.resolution_levels)
            else:
                visualize_with_curves(tree)
        else:
            tree = old_tree

        tree_object = bpy.context.object
        if level in ("gen", "scale"):
            tree_object.scale = tuple([self.scale]*3)

        if self.armature and level in ("armature", "gen"):
            amt = add_armature(tree, self.min_armature_radius, self.min_length)
            tree_object["amt"] = amt.name
            # amt.select = True
            amt.scale = tuple([self.scale] * 3)

        if self.create_particle_emitter and level in ("emitter", "gen"):
            emitter = add_particles_emitter(tree, self.max_radius, self.particle_proba, bpy.context.scene.objects.get(self.dupli_object))
            tree_object["emitter"] = emitter.name
            # emitter.select = True
            emitter.scale = tuple([self.scale] * 3)

        if bpy.data.materials.get(self.material) is not None and level in ("material", "gen"):
            tree_object.active_material = bpy.data.materials.get(self.material)


        t2 = time.time()
        print("creating tree", t1 - t0)
        print("building object", t2 - t1)
        return tree


class GreasePencilNode(Node, ModularTreeNode):
    bl_idname = "GreasePencilNode"
    bl_label = "Grease_Pencil"

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
        # bpy.ops.mod_tree.connect_strokes(point_dist=self.branch_length, automatic=True, connect_all=True,
        #                                  child_stroke_index=1, parent_stroke_index=0,
        #                                  smooth_iterations=self.smooth_iterations)

        op_props = layout.operator("mod_tree.connect_strokes", text='update strokes')
        op_props.point_dist = self.branch_length
        op_props.connect_all = True
        op_props.child_stroke_index = 1
        op_props.parent_stroke_index = 0
        op_props.smooth_iterations = self.smooth_iterations
        for i in properties:
            layout.prop(self, i)

    def execute(self):

        gp = bpy.context.scene.grease_pencil
        if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(
                gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:

            strokes = [[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]
            root = build_tree_from_strokes(strokes, self.radius, self.radius_decrease)
            return root


class SplitNode(Node, ModularTreeNode):
    bl_idname = "SplitNode"
    bl_label = "Split"

    proba = FloatProperty(min=0, max=1, default=.3, description="Probability of replacing a branch by a split")
    split_angle = FloatProperty(min=0, max=180, default=45, description="Angle between the branch branch direction and the secondary split direction")
    spin = FloatProperty(min=0, max=360, default=45, description="Rotation between each split")
    head_size = FloatProperty(min=0.001, max=.999, default=.6, description="Size of the secondary branch compared to the main one")
    offset = IntProperty(min=0, default=0, description="Number of branches that wont be split before the first split occurs")

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
        try:
            from_node = self.inputs['Tree'].links[0].from_node
        except:
            return None
        tree = from_node.execute()
        if tree is None:
            return None

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
    advanced_settings = BoolProperty(default=False, description="Show advanced settings")
    iterations = IntProperty(min=0, default=5, description="Number of branches iterations")
    radius = FloatProperty(min=.0005, default=.2, description="The radius at which branches stop growing")
    branch_length = FloatProperty(min=.001, default=.9, description="The length of each branch iteration")
    split_proba = FloatProperty(min=0, max=1, default=.3, description="The probability for a branch to fork")
    split_angle = FloatProperty(min=0, max=180, default=45, description="When a branch is splitting, the angle between the branches of the split")
    split_deviation = FloatProperty(min=0, max=7, default=.25, description="When a branch is splitting, the angle between the split and the previous branch")
    split_radius = FloatProperty(min=.01, max=.999, default=.6, description="When a branch is splitting, the radius of the secondary branch of the fork")
    radius_decrease = FloatProperty(min=0.01, max=.999, default=.97, description="The radius of each branch iteration compared to the previous one")
    randomness = FloatProperty(default=.1, description="Noise affecting the direction of each branch")
    spin = FloatProperty(default=135, description="Relative rotation of a split compared to the previous split in the branch")
    spin_randomness = FloatProperty(min=0, max=7, default=.1, description="Randomness of the spin")
    gravity_strength = FloatProperty(default=.1, description="Amount of downward attraction")
    pruning_strength = FloatProperty(default=1, description="Decrease the probability of branching when the density of branches is high")
    shape_factor = FloatProperty(default=1, min=0, description="Decrease of branching probability when the branch is far from the axis of the tree")
    up_attraction = FloatProperty(default=.5, description="Favor branches going up")

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")


    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        layout.prop(self, "advanced_settings")
        layout.prop(self, "limit_method")
        box = layout.box()
        box.prop(self, self.limit_method)

        box = layout.box()
        box.prop(self, "branch_length")
        box.prop(self, "randomness")
        if self.advanced_settings:
            box.prop(self, "radius_decrease")
        box.prop(self, "gravity_strength")

        box = layout.box()
        box.prop(self, "split_proba")
        if self.advanced_settings:
            box.prop(self, "split_angle")
            box.prop(self, "split_deviation")
            box.prop(self, "split_radius")

            box = layout.box()
            box.prop(self, "spin")
            box.prop(self, "spin_randomness")

        box = layout.box()
        if self.advanced_settings:
            box.prop(self, "pruning_strength")
        box.prop(self, "shape_factor")
        box.prop(self, "up_attraction")

    def execute(self):
        try:
            from_node = self.inputs['Tree'].links[0].from_node
        except:
            return None

        tree = from_node.execute()
        if tree is None:
            return None

        selection = self.inputs["Selection"].get_selection()
        grow(tree, self.iterations, self.radius, self.limit_method, self.branch_length, self.split_proba,
             self.split_angle, self.split_deviation, self.split_radius, self.radius_decrease, self.randomness,
             self.spin, self.spin_randomness, self.selection[0], selection, self.gravity_strength, self.pruning_strength,
             self.shape_factor, self.up_attraction)
        return tree


class TrunkNode(Node, ModularTreeNode):
    bl_idname = "TrunkNode"
    bl_label = "Trunk"

    height = FloatProperty(min=0, default=10)
    radius = FloatProperty(min=.0005, default=.8)
    branch_length = FloatProperty(min=.002, default=.9)
    radius_decrease = FloatProperty(min=0.01, max=.999, default=.97)
    randomness = FloatProperty(default=.1)
    up_attraction = FloatProperty(default=.7)
    twist = FloatProperty(default=0)

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")

    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        properties = ["radius", "height", "branch_length", "radius_decrease", "randomness", "up_attraction", "twist"]
        col = layout.column()
        for i in properties:
            col.prop(self, i)

    def execute(self):
        tree = add_basic_trunk(self.radius, self.radius_decrease, self.randomness, self.up_attraction, self.twist, self.height, self.branch_length)
        return tree


class ModularTreeNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ModularTreeType'


inputs = [GreasePencilNode, TrunkNode]
tree_functions = [SplitNode, GrowNode]
outputs = [BuildTreeNode]

node_categories = [ModularTreeNodeCategory("inputs", "inputs", items=[NodeItem(i.bl_idname) for i in inputs]),
                   ModularTreeNodeCategory("tree_functions", "tree functions", items=[NodeItem(i.bl_idname) for i in tree_functions]),
                   ModularTreeNodeCategory("outputs", "outputs", items=[NodeItem(i.bl_idname) for i in outputs])]

node_classes_to_register = [ModularTree, TreeSocket, BuildTreeNode, GreasePencilNode, SplitNode, GrowNode, TrunkNode]


# @persistent
# def has_nodes_changed(dummy):
#     node = bpy.context.active_node.id_data.nodes.get("BuildTree")
#     new_memory = get_tree_parameters_rec("", node)
#     # new_memory = "coucou"
#     # condition = True
#     if node.auto_update and new_memory != node.memory:
#         bpy.ops.object.delete(use_global=False)
#         node.execute()
#         # bpy.ops.mod_tree.tree_from_nodes()
#
#         node.memory = new_memory
#         # node.execute()
#
#
# bpy.app.handlers.frame_change_pre.append(has_nodes_changed)
