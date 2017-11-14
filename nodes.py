import bpy
import nodeitems_utils

from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty
from nodeitems_utils import NodeCategory, NodeItem

from .grease_pencil import build_tree_from_strokes
from .tree_functions import draw_module_rec, add_splits, grow


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

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.operator("mod_tree.tree_from_nodes", text='create tree').node_name = self.name

    def execute(self):
        from_node = self.inputs['Tree'].links[0].from_node
        tree = from_node.execute()
        draw_module_rec(tree)


class GreasePencilNode(Node, ModularTreeNode):
    bl_idname = "GreasePencilNode"
    bl_label = "Grease Pencil"

    smooth_iterations = IntProperty(min=0, default=1)
    radius = FloatProperty(min=0, default=.7)
    branch_length = FloatProperty(min=.001, default=.6)
    radius_decrease = FloatProperty(min=0, max=.999, default=.97)


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
        bpy.ops.mod_tree.connect_strokes(point_dist=self.branch_length, automatic=True, connect_all=True,
                                         child_stroke_index=1, parent_stroke_index=0)
        gp = bpy.context.scene.grease_pencil
        if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(
                gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:
            strokes = [[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]
            root = build_tree_from_strokes(strokes, self.radius, self.radius_decrease)
            return root


class SplitNode(Node, ModularTreeNode):
    bl_idname = "SplitNode"
    bl_label = "Split"

    proba = FloatProperty(min=0, max=1, default=.3)
    split_angle = FloatProperty(min=0, max=180, default=45)
    spin = FloatProperty(min=0, max=7, default=1.57)
    head_size = FloatProperty(min=0.001, max=.999, default=.6)

    def init(self, context):
        self.inputs.new("TreeSocketType", "Tree")
        self.inputs.new("SelectionSocketType", "Selection")
        self.outputs.new("TreeSocketType", "Tree")
        self.outputs.new("SelectionSocketType", "Selection")

    @property
    def selection(self):
        return [self.name]

    def draw_buttons(self, context, layout):
        properties = ['proba', "split_angle", "spin", "head_size"]
        row = col = layout.column()
        for i in properties:
            col.prop(self, i)

    def execute(self):
        from_node = self.inputs['Tree'].links[0].from_node
        tree = from_node.execute()
        selection = self.inputs["Selection"].get_selection()
        add_splits(tree, self.proba, selection, self.selection[0], self.split_angle, self.spin, self.head_size)
        return tree


class GrowNode(Node, ModularTreeNode):
    bl_idname = "GrowNode"
    bl_label = "Grow"

    limit_method = bpy.props.EnumProperty(
        items=[('iterations', 'Iterations', ''), ('radius', 'Radius', '')],
        name="limit method",
        default="radius")

    iterations = IntProperty(min=0, default=5)
    radius = FloatProperty(min=.000001, default=.02)
    branch_length = FloatProperty(min=.001, default=.5)
    split_proba = FloatProperty(min=0, max=1, default=.3)
    split_angle = FloatProperty(min=0, max=180, default=45)
    split_deviation = FloatProperty(min=0, max=7, default=.25)
    split_radius = FloatProperty(min=.01, max=.999, default=.6)
    radius_decrease = FloatProperty(min=0.01, max=.999, default=.97)
    randomness = FloatProperty(default=.1)
    spin = FloatProperty(default=45)
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




