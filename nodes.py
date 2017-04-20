import bpy
from bpy.types import NodeTree, Node, NodeSocket
from bpy.props import *
import time
from .icons import get_icon
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

helperMaterialName = "Helper Material for Modular Tree"


class FloatSocket(NodeSocket):
    # Description string
    '''Custom float socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'FloatSocket'
    # Label for nice name display
    bl_label = 'Custom Float Socket'

    default_value = bpy.props.FloatProperty(name="value", default=0, min=0, soft_max=1)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "default_value", text=text)

    # Socket color
    def draw_color(self, context, node):
        return .06, 0.2, 0.5, 0.5


class FreeFloatSocket(NodeSocket):
    # Description string
    '''Custom float socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'FreeFloatSocket'
    # Label for nice name display
    bl_label = 'Custom Float Socket with no nim or max'

    default_value = bpy.props.FloatProperty(name="value", default=0, soft_min=-5, soft_max=5)

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text)
        else:
            layout.prop(self, "default_value", text=text)

    # Socket color
    def draw_color(self, context, node):
        return .06, 0.2, 0.5, 0.5




class ModularTreeNodeTree(NodeTree):
    # Description string
    '''Modular tree Node workflow'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'ModularTreeNodeType'
    # Label for nice name display
    bl_label = 'Modular Tree Node Tree'
    # Icon identifier
    bl_icon = 'NODETREE'

    time_lap = 0

    def update(self):
        for node in self.nodes:
            node.update()


def update_all_trees(scene):
    trees = [n for n in bpy.data.node_groups if n.bl_idname == 'ModularTreeNodeType']
    for t in trees:
        if time.time() - t.time_lap > 1:
            t.update()


class ModularTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ModularTreeNodeType'


class ModularTreeNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'ModularTreeNodeType'


class RootNode(Node, ModularTreeNodeTree):
    ''' Roots configuration Node '''
    bl_idname = 'RootNode'
    bl_label = 'Roots'
    bl_width_default = 190

    iterations = bpy.props.IntProperty(default=0)
    stay_under_ground = bpy.props.BoolProperty(default=True)

    def init(self, context):
        scene = bpy.context.scene
        mtree_props = scene.mtree_props

        self.outputs.new('NodeSocketShader', "Trunk")

    def update(self):
        scene = bpy.context.scene
        mtree_props = scene.mtree_props
        if self.iterations == 0 and len(self.inputs.items()) >0:
            for s in self.inputs:
                self.inputs.remove(s)
        elif self.iterations > 0 and len(self.inputs.items()) == 0:
            self.inputs.new('FloatSocket', "Length").default_value = mtree_props.roots_length
            self.inputs.new('FloatSocket', "split_proba").default_value = mtree_props.roots_split_proba
            self.inputs.new('FreeFloatSocket', "ground_height").default_value = mtree_props.roots_ground_height



    def draw_buttons(self, context, layout):
        layout.prop(self, "iterations")
        if self.iterations >0:
            layout.prop(self, "stay_under_ground")




class TrunkNode(Node, ModularTreeNodeTree):
    ''' Trunk configuration Node '''
    bl_idname = 'TrunkNode'
    bl_label = 'Trunk'
    bl_width_default = 200

    preserve_trunk = bpy.props.BoolProperty(default=True)
    use_grease_pencil = bpy.props.BoolProperty(default=False)
    trunk_iterations = bpy.props.IntProperty(default=6, min=0)
    trunk_end = bpy.props.IntProperty(default=35, min=0)

    def init(self, context):
        scene = bpy.context.scene
        mtree_props = scene.mtree_props

        self.inputs.new('NodeSocketShader', "Roots")
        self.inputs.new('FloatSocket', "Trunk_length")
        self.inputs.new('FloatSocket', "split_proba")
        self.inputs.new('FloatSocket', "split_angle")
        self.inputs.new('FreeFloatSocket', "randomness")
        self.inputs.new('FloatSocket', "Radius_Shape")

        # self.inputs["Trunk_length"].default_value = mtree_props.trunk_space
        self.inputs["split_proba"].default_value = mtree_props.trunk_split_proba
        self.inputs["randomness"].default_value = mtree_props.trunk_variation
        self.inputs["split_angle"].default_value = mtree_props.trunk_split_angle

        self.outputs.new('NodeSocketShader', "Tree")

    def draw_buttons(self, context, layout):
        layout.prop(self, "preserve_trunk")
        layout.prop(self, "use_grease_pencil")
        layout.prop(self, "trunk_iterations")
        layout.prop(self, "trunk_end")

    def update(self):
        pass


class BranchNode(Node, ModularTreeNodeTree):
    ''' Branch configuration Node '''
    bl_idname = 'BranchNode'
    bl_label = 'Branches'
    bl_width_default = 170

    iterations = bpy.props.IntProperty(default=25)

    # radius_decrease = bpy.props.IntProperty(default = mtree_props.radius_dec)

    def init(self, context):
        scene = bpy.context.scene
        mtree_props = scene.mtree_props

        self.inputs.new('NodeSocketShader', "Trunk")
        self.inputs.new('FloatSocket', "length")
        self.inputs.new('FreeFloatSocket', "variations")
        self.inputs.new('FloatSocket', "split_proba")
        self.inputs.new('FloatSocket', "split_angle")
        self.inputs.new('FloatSocket', "break_chance")
        self.inputs.new('FloatSocket', "radius_decrease")
        self.inputs.new('FloatSocket', "min_radius")


        self.inputs["length"].default_value = mtree_props.branch_length
        self.inputs["variations"].default_value = mtree_props.randomangle
        self.inputs["split_proba"].default_value = mtree_props.split_proba
        self.inputs["split_angle"].default_value = mtree_props.split_angle
        self.inputs["break_chance"].default_value = mtree_props.break_chance
        self.inputs["radius_decrease"].default_value = mtree_props.radius_dec
        self.inputs["min_radius"].default_value = mtree_props.branch_min_radius
        self.outputs.new('NodeSocketShader', "Tree")


    def draw_buttons(self, context, layout):
        layout.prop(self, "iterations")
        # layout.prop(self, "radius_decrease")

    def update(self):
        pass


class TreeOutput(Node, ModularTreeNodeTree):
    ''' Tree configuration Node '''
    bl_idname = 'TreeOutput'
    bl_label = 'Tree_Output'
    bl_width_default = 170


    Seed = bpy.props.IntProperty(default=42)
    uv = bpy.props.BoolProperty(default=True)
    create_material = bpy.props.BoolProperty(default=False)
    material = bpy.props.StringProperty(default="")

    def init(self, context):

        self.use_custom_color = True
        self.color = (0.0236563, 0.0913065, 0.173356)
        self.inputs.new('NodeSocketShader', "Tree")

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.add_tree", icon_value=get_icon("TREE"))
        layout.prop(self, "Seed")
        layout.prop(self, "uv")
        layout.prop(self, "create_material")

    def update(self):
        pass


def get_node_group():
    if 'curve_node_group' not in bpy.data.node_groups:
        print('creating group')
        node_group = bpy.data.node_groups.new('curve_node_group', 'ShaderNodeTree')
        # node_group.use_fake_user = True
    return bpy.data.node_groups['curve_node_group'].nodes


curve_node_mapping = {}


def CurveData(name):
    if name not in curve_node_mapping:
        curve_node = get_node_group().new('ShaderNodeRGBCurve')
        curve_node_mapping[name] = curve_node.name
    return get_node_group()[curve_node_mapping[name]]


class CurveNode(Node, ModularTreeNodeTree):
    ''' Curve node to map values '''

    bl_idname = 'CurveNode'
    bl_label = 'Curve_Mapping'
    bl_width_default = 200

    min = bpy.props.FloatProperty(default=0)
    max = bpy.props.FloatProperty(default=1)

    drivers = [
        ("ITERATION", "Iteration", "The current iteration of the branch"),
        ("RADIUS", "Radius", "The current radius of the branch"),
    ]
    driver = bpy.props.EnumProperty(name="input", description="The X axis of the curve", items=drivers, default='ITERATION')

    def init(self, context):
        self.outputs.new('FreeFloatSocket', "value")

    def draw_buttons(self,context, layout):
        layout.prop(self, 'driver')
        layout.template_curve_mapping(self.node, "mapping")
        layout.prop(self, "min")
        layout.prop(self, "max")

    def update(self):
        pass



    @property
    def node(self):
        n = CurveData(self.name)
        return n


nodes_to_register = [ModularTreeNodeTree,RootNode, TrunkNode, BranchNode, TreeOutput, CurveNode, FloatSocket, FreeFloatSocket]


bpy.app.handlers.scene_update_post.append(update_all_trees)


node_categories = [
    # identifier, label, items list
    ModularTreeNodeCategory("Tree", "Tree Nodes",
                            items=[NodeItem("RootNode"), NodeItem("TrunkNode"), NodeItem("BranchNode"),
                                   NodeItem("TreeOutput")]),
    ModularTreeNodeCategory("Input", "Input", items=[NodeItem("CurveNode")]),
    ModularTreeNodeCategory("Modifiers", "Modifiers", items=[]),
]
