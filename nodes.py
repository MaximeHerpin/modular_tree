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


def get_tree_parameters_rec(state_list, node):
    if node.bl_idname != "BuildTreeNode":
        state_list += str(node.items()) + ","

    else:
        state_list += str(node.seed) + str(node.mesh_type) + str(node.armature) + str(node.min_length) + ","

    if node.bl_idname == "GreasePencilNode" or node.bl_idname == "TrunkNode":
        return state_list

    try:
        from_node = node.inputs['Tree'].links[0].from_node
    except:
        return state_list

    if from_node is not None:
        return get_tree_parameters_rec(state_list, from_node)


def get_last_memory_match(new, old):
    new = new.split(",")
    old = old.split(',')
    level = len(new)
    for i in range(min(len(new), len(old))):
        if new[-(i+1)] != old[-(i+1)]:
            break
        level -= 1
    return level


class ModalModularTreedOperator(bpy.types.Operator):
    """real time tree tweaking"""
    bl_idname = "object.modal_tree_operator"
    bl_label = "Modal Tree Operator"


    _timer = None

    node = None
    tree = None

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            self.node.auto_update = False
            return {'CANCELLED'}

        if event.type == 'TIMER':

            new_memory = get_tree_parameters_rec("", self.node)
            level = get_last_memory_match(new_memory, self.node.memory)
            if level > 0:
            # if new_memory != self.node.memory:
                bpy.ops.object.delete(use_global=False)
                self.node.memory = new_memory
                self.tree = self.node.execute()

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        self.node.auto_update = True
        # self.tree = self.node.execute()
        # self.node = bpy.context.active_node.id_data.nodes.get("BuildTree")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


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
    auto_update = BoolProperty(default=False)
    seed = IntProperty(default=42)

    armature = BoolProperty(default=False)
    min_armature_radius = FloatProperty(min=0, default=.3)
    min_length = FloatProperty(min=0, default=1)

    create_particle_emitter = BoolProperty(default=False)
    dupli_object = StringProperty(default="")
    max_radius = FloatProperty(default=.2, min=0)
    particle_proba = FloatProperty(default=.5, min=0, max=1)


    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.memory = get_tree_parameters_rec("", self)


    def draw_buttons(self, context, layout):
        layout.prop(self, "mesh_type")
        if self.mesh_type == "final":
            layout.prop(self, "resolution_levels")
        layout.prop(self, "seed")
        row = layout.row()
        row.operator("object.modal_tree_operator", text='auto_update_tree')
        # row.prop(self, "auto_update")
        if not self.auto_update:
            row.operator("mod_tree.tree_from_nodes", text='create tree').node_name = self.name

        box = layout.box()
        box.prop(self, "armature")
        if self.armature:
            box.prop(self, "min_armature_radius")
            box.prop(self, "min_length")

        box = layout.box()
        box.prop(self, "create_particle_emitter")
        if self.create_particle_emitter:
            box.prop(self, "max_radius")


    def execute(self, rebuild=True, old_tree=None):
        print("build_node")
        random.seed(self.seed)
        from_node = self.inputs['Tree'].links[0].from_node
        t0 = time.time()
        if rebuild:
            tree = from_node.execute()
        else:
            tree = old_tree
        t1 = time.time()
        if rebuild:
            if self.mesh_type == "final":
                draw_module(tree, self.resolution_levels)
            else:
                visualize_with_curves(tree)

        if self.armature:
            amt = add_armature(tree, self.min_armature_radius, self.min_length)
            amt.select = True

        if self.create_particle_emitter:
            add_particles_emitter(tree, self.max_radius, self.particle_proba)
        t2 = time.time()
        print("creating tree", t1 - t0)
        print("building object", t2 - t1)
        return tree


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
        print("split_node", level)
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
    spin = FloatProperty(default=135, description="relative rotation of a split compared to the previous split in the branch")
    spin_randomness = FloatProperty(min=0, max=7, default=.1, description="The randomness of the spin")
    gravity_strength = FloatProperty(default=.1, description="Amount of downward attraction")
    pruning_strength = FloatProperty(default=1, description="Decrease the probability of branching when the density of branches is high")
    shape_factor = FloatProperty(default=1, min=0, description="Decrease of branching probability when the branch is far from the axis of the tree")

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")

    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        properties = ["advanced_settings", "limit_method", self.limit_method, "branch_length", "split_proba", "randomness", "gravity_strength"]
        advanced_properties = ["split_angle", "split_deviation", "split_radius", "radius_decrease", "spin", "spin_randomness", "pruning_strength", "shape_factor"]
        col = layout.column()
        for i in properties:
            col.prop(self, i)

        if self.advanced_settings:
            for i in advanced_properties:
                col.prop(self, i)

    def execute(self):
        from_node = self.inputs['Tree'].links[0].from_node

        tree = from_node.execute()

        selection = self.inputs["Selection"].get_selection()
        grow(tree, self.iterations, self.radius, self.limit_method, self.branch_length, self.split_proba,
             self.split_angle, self.split_deviation, self.split_radius, self.radius_decrease, self.randomness,
             self.spin, self.spin_randomness, self.selection[0], selection, self.gravity_strength, self.pruning_strength, self.shape_factor)
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
        print("trunk_node")
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
