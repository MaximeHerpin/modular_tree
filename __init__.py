# Copyright 2016 Maxime Herpin, Jake Dube
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of Modular Tree.
#
# Modular Tree is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Modular Tree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Modular Tree.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####

from random import randint

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty, PointerProperty
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences, PropertyGroup

from .generator_operators import MakeTreeOperator, BatchTreeOperator, MakeTwigOperator, UpdateTreeOperator, UpdateTwigOperator, SetupNodeTreeOperator
from .presets import TreePresetLoadMenu, TreePresetRemoveMenu, SaveTreePresetOperator, InstallTreePresetOperator, RemoveTreePresetOperator, LoadTreePresetOperator
from .logo import display_logo
from .wind_setup_utils import WindOperator, MakeControllerOperator, MakeTerrainOperator
from .addon_name import save_addon_name

from .icons import register_icons, unregister_icons, get_icon
from .nodes import nodes_to_register, node_categories
import nodeitems_utils
import copy


# third party add-on updater
from . import addon_updater_ops

bl_info = {
    "name": "Modular trees",
    "author": "Herpin Maxime, Jake Dube",
    "version": (2, 9, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Generates an organic tree with correctly modeled branching.",
    "warning": "May take a long time to generate! Save your file before generating!",
    "wiki_url": "https://github.com/MaximeHerpin/modular_tree/wiki",
    "tracker_url": "https://github.com/MaximeHerpin/modular_tree/issues/new",
    "category": "Add Mesh"}


class TreeAddonPrefs(AddonPreferences):
    bl_idname = __name__

    always_save_prior = BoolProperty(
        name="Save .blend File",
        default=True,
        description="Always save .blend file before executing " +
                    "time-consuming operations")

    save_all_images = BoolProperty(
        name="Save Images",
        default=True,
        description="Always save images before executing " +
                    "time-consuming operations")

    save_all_texts = BoolProperty(
        name="Save Texts",
        default=True,
        description="Always save texts before executing " +
                    "time-consuming operations")

    preset_file = StringProperty(
        name="Preset File",
        description="Preset File",
        subtype='FILE_PATH')

    # third party add-on updater
    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=True,
    )

    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=14,
        min=0,
    )
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.prop(self, 'always_save_prior')
        col.prop(self, 'save_all_images')
        col.prop(self, 'save_all_texts')

        row = layout.row()
        # website url
        row.operator("wm.url_open", text="Feature Roadmap", icon='QUESTION').url = \
            "https://github.com/MaximeHerpin/modular_tree/wiki/Roadmap"
        row.operator("wm.url_open", text="Official Discussion Forum", icon='QUESTION').url = \
            "https://blenderartists.org/forum/showthread.php?405377-Addon-Modular-Tree"

        box = layout.box()
        box.label("Preset Installer")
        box.prop(self, 'preset_file')
        box.operator("mod_tree.install_preset")

        addon_updater_ops.update_settings_ui(self, context)


class MakeTreePanel(Panel):
    bl_label = "Make Tree"
    bl_idname = "3D_VIEW_PT_layout_MakeTree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.add_tree", icon="WORLD")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.update_tree", icon="FILE_REFRESH")

        box = layout.box()
        box.label("Basic")
        box.prop(mtree_props, 'use_node_workflow')
        if mtree_props.use_node_workflow:
            box.prop_search(mtree_props, "node_tree",bpy.data, "node_groups")
            if mtree_props.node_tree != "":
                if bpy.data.node_groups[mtree_props.node_tree]:
                    node_tree = bpy.data.node_groups[mtree_props.node_tree]
                    if not [i for i in node_tree.nodes]:
                        print('can setup')
                        row = box.row()
                        row.operator("mod_tree.setup_node_tree")



        if not mtree_props.use_node_workflow:
            sbox = box.box()
            sbox.label("UI")
            sbox.prop(mtree_props, 'ui_mode', expand=True)
            box.prop(mtree_props, "SeedProp")
            box.prop(mtree_props, "iteration")
            box.prop(mtree_props, 'radius')
            box.prop(mtree_props, 'uv')

        addon_updater_ops.update_notice_box_ui(self, context)


class BatchTreePanel(Panel):
    bl_label = "Batch Tree Generation"
    bl_idname = "3D_VIEW_PT_layout_BatchTree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5

        if not mtree_props.use_grease_pencil:
            box = layout.box()
            row.operator("mod_tree.batch_tree", icon_value=get_icon("BATCH_TREE"))
            box.prop(mtree_props, 'tree_number')
     
            

class RootsAndTrunksPanel(Panel):
    bl_label = "Roots and Trunk"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeRootsAndTrunks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        if not mtree_props.use_node_workflow:
            layout = self.layout

            if mtree_props.ui_mode == 'COMPLETE':
                box = layout.box()
                box.label("Roots")
                sbox = box.box()
                # sbox.prop(mtree_props, 'create_roots')
                if mtree_props.create_roots:
                    sbox.prop(mtree_props, 'roots_iteration')
                    sbox.prop(mtree_props, 'roots_split_proba')
                    sbox.prop(mtree_props, 'roots_length')
                    sbox.prop(mtree_props, 'roots_stay_under_ground')
                    if mtree_props.roots_stay_under_ground:
                        sbox.prop(mtree_props, 'roots_ground_height')

                box = layout.box()
                box.label("Trunk")
                sbox = box.box()
                sbox.prop(mtree_props, 'use_grease_pencil')
                if mtree_props.use_grease_pencil:
                    sbox.prop(mtree_props, 'smooth_stroke')
                    sbox.prop(mtree_props, 'stroke_step_size')
                box.prop(mtree_props, 'trunk_length')
                box.prop(mtree_props, 'trunk_variation')
                box.prop(mtree_props, 'trunk_space')
                sbox = box.box()
                sbox.prop(mtree_props, 'preserve_trunk')
                if mtree_props.preserve_trunk:
                    sbox.prop(mtree_props, 'preserve_end')
                    sbox.prop(mtree_props, 'trunk_split_proba')
                    sbox.prop(mtree_props, 'trunk_split_angle')
            else:
                box = layout.box()
                box.prop(mtree_props, 'use_grease_pencil')
                box.prop(mtree_props, 'trunk_length')
                box.prop(mtree_props, 'preserve_trunk')


class TreeBranchesPanel(Panel):
    bl_label = "Branches"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeBranches"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        mtree_props = scene.mtree_props
        if not mtree_props.use_node_workflow:
            layout = self.layout

            if mtree_props.ui_mode == 'COMPLETE':

                box = layout.box()
                box.label("Branches")
                box.prop(mtree_props, 'break_chance')
                box.prop(mtree_props, 'dont_break_trunk')
                box.prop(mtree_props, 'branch_length')
                box.prop(mtree_props, 'randomangle')
                box.prop(mtree_props, 'split_proba')
                box.prop(mtree_props, 'split_angle')
                box.prop(mtree_props, 'radius_dec')
                box.prop(mtree_props, 'branch_min_radius')
                col = box.column(align=True)
                col.prop(mtree_props, 'branch_rotate')
                col.prop(mtree_props, 'branch_random_rotate')

                box = layout.box()
                col = box.column(True)
                col.prop(mtree_props, 'gravity_strength')
                col.prop(mtree_props, 'gravity_start')
                col.prop(mtree_props, 'gravity_end')
                sbox = box.box()
                sbox.prop_search(mtree_props, "obstacle", scene, "objects")
                if bpy.data.objects.get(mtree_props.obstacle) is not None:
                    sbox.prop(mtree_props, 'obstacle_strength')
                    sbox.prop(mtree_props, 'obstacle_flip_normals')
                    sbox.prop(mtree_props, 'obstacle_kill')
                sbox = box.box()
                col1 = sbox.column()
                col1.prop(mtree_props, 'use_force_field')
                if mtree_props.use_force_field:
                    col1.prop(mtree_props, 'fields_point_strength')
                    col1.prop(mtree_props, 'fields_wind_strength')
                    col1.prop(mtree_props, 'fields_strength_limit')
                    col1.prop(mtree_props, 'fields_radius_factor')
            else:
                box = layout.box()
                box.prop(mtree_props, 'branch_length')
                box.prop(mtree_props, 'split_angle')
                box.prop(mtree_props, 'split_proba')
                box.prop(mtree_props, 'gravity_strength')
                box.prop(mtree_props, 'use_force_field')
                sbox = box.box()
                sbox.prop_search(mtree_props, "obstacle", scene, "objects")
                if bpy.data.objects.get(mtree_props.obstacle) is not None:
                    sbox.prop(mtree_props, 'obstacle_strength')
                    sbox.prop(mtree_props, 'obstacle_kill')


class AdvancedSettingsPanel(Panel):
    bl_label = "Advanced Settings"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeAdvancedSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        if not mtree_props.use_node_workflow:
            layout = self.layout
            scene = context.scene

            if mtree_props.ui_mode == 'COMPLETE':

                box = layout.box()
                box.prop(mtree_props, 'mat')
                if not mtree_props.mat:
                    box.prop_search(mtree_props, "bark_material", bpy.data, "materials")
                box.prop(mtree_props, 'create_armature')
                if mtree_props.create_armature:
                    box.prop(mtree_props, 'bones_iterations')
                box.prop(mtree_props, 'leafs_iteration_length')
                box.prop(mtree_props, 'particle')
                if mtree_props.particle:
                    box.prop(mtree_props, 'create_particle_emitter')
                    box.prop(mtree_props, 'number')
                    box.prop(mtree_props, 'display')
                    box.prop_search(mtree_props, "twig_particle", scene, "objects")
                    box.prop(mtree_props, 'particle_size')
                box = layout.box()
                box.prop(mtree_props, 'pruning')
                if mtree_props.pruning:
                    box.prop(mtree_props, 'pruning_intensity')
                    box.prop(mtree_props, 'pruning_resolution')
            else:
                box = layout.box()
                box.prop(mtree_props, 'mat')
                if not mtree_props.mat:
                    box.prop_search(mtree_props, "bark_material", bpy.data, "materials")
                box.prop(mtree_props, 'particle')
                if mtree_props.particle:
                    box.prop(mtree_props, 'number')
                    box.prop_search(mtree_props, "twig_particle", scene, "objects")
                box.prop(mtree_props, 'pruning')
                if mtree_props.pruning:
                    box.prop(mtree_props, 'pruning_intensity')


class WindAnimationPanel(Panel):
    bl_label = "Wind Animation"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeWindAnimation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("mod_tree.animate_wind", icon="FORCE_VORTEX")
        box.operator("mod_tree.make_wind_controller", icon="FORCE_VORTEX")
        box.operator("mod_tree.make_terrain", icon="FORCE_VORTEX")
        box.prop_search(mtree_props, "wind_controller", bpy.data, "objects")
        box.prop_search(mtree_props, "terrain", bpy.data, "objects")
        box.prop(mtree_props, "wind_height_start")
        box.prop(mtree_props, "wind_height_full")
        box.prop(mtree_props, "clear_mods")
        box.prop(mtree_props, "wind_strength")


class MakeTwigPanel(Panel):
    bl_label = "Make Twig"
    bl_idname = "3D_VIEW_PT_layout_MakeTwig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        layout = self.layout
        scene = context.scene

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.add_twig", icon="SCULPTMODE_HLT")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.update_twig", icon="FILE_REFRESH")

        box = layout.box()
        box.label("Twig Options")
        sbox = box.box()
        sbox.label("UI")
        sbox.prop(mtree_props, 'ui_mode', expand=True)
        if mtree_props.ui_mode == 'COMPLETE':
            box.prop(mtree_props, "leaf_size")
            box.prop_search(mtree_props, "leaf_object", scene, "objects")
            box.prop(mtree_props, "leaf_chance")
            box.prop(mtree_props, "leaf_weight")
            box.prop(mtree_props, "TwigSeedProp")
            box.prop(mtree_props, "twig_iteration")
            box.prop_search(mtree_props, "twig_bark_material", bpy.data, "materials")
        else:
            box.prop(mtree_props, 'leaf_size')
            box.prop(mtree_props, 'TwigSeedProp')
            box.prop_search(mtree_props, "twig_bark_material", bpy.data, "materials")


class MakeTreePresetsPanel(Panel):
    bl_label = "Presets"
    bl_idname = "3D_VIEW_PT_layout_MakeTreePresets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        mtree_props = context.scene.mtree_props
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.25
        row.menu("mod_tree.preset_load_menu")

        row = layout.row(align=True)
        row.prop(mtree_props, "preset_name", text="")
        row.operator("mod_tree.save_preset", icon="SETTINGS")

        row = layout.row()
        row.menu("mod_tree.preset_remove_menu")


class ModularTreePropertyGroup(PropertyGroup):
    """This is the set of all of the properties for modular tree."""
    preset_name = StringProperty(name="Preset Name", default="MyPreset")

    ui_mode = EnumProperty(
        name="UI Mode",
        items=(
            ('SIMPLE', 'Simple', "", 0),
            ('COMPLETE', 'Complete', "", 1)))

    preserve_trunk = BoolProperty(
        name="Preserve Trunk", default=False,
        description="preserves the trunk growth, check and see.")

    finish_trunk = BoolProperty(
        name="generate branches after trunk",
        default=False,
        description='wait for the entire trunk to be generated before starting branches')

    trunk_split_angle = FloatProperty(
        name="Trunk Split Angle",
        min=0.0,
        max=1,
        default=0,
        description="how wide is the angle in a split if this split comes from the trunk")

    randomangle = FloatProperty(
        name="Branch Variations",
        default=.5)

    trunk_variation = FloatProperty(
        name="Trunk Variation",
        default=.1)

    radius = FloatProperty(
        name="Radius",
        min=0.01,
        default=1)

    radius_dec = FloatProperty(
        name="Radius Decrease",
        min=0.01,
        max=1.0,
        default=0.95,
        description="Relative radius after each iteration, low value means fast radius decrease")

    iteration = IntProperty(
        name="Branch Iterations",
        min=2,
        soft_max=50,
        default=20)

    preserve_end = IntProperty(
        name="Trunk End",
        min=0,
        default=25,
        description="iteration on which trunk preservation will end")

    trunk_length = IntProperty(
        name="Trunk Iterations",
        min=1,
        default=9,
        description="Iteration from from which first split occurs")

    trunk_split_proba = FloatProperty(
        name="Trunk Split Probability",
        min=0.0,
        max=1.0,
        default=0.5,
        description="probability for a branch to split. WARNING : sensitive")

    split_proba = FloatProperty(
        name="Split Probability",
        min=0.0,
        max=1.0,
        default=0.25,
        description="Probability for a branch to split. \nWARNING : sensitive")

    trunk_space = FloatProperty(
        name="Trunk Length",
        min=0.01,
        default=.7,
        description="Length of the trunk")

    trunk_radius_dec = FloatProperty(
        name='Trunk_radius_decrease',
        default=.975,
        min=0.00001)

    branch_length = FloatProperty(
        name="Branch Length",
        min=0.01,
        default=.55,
        description="Branch length")

    split_angle = FloatProperty(
        name="Split Angle",
        min=0.0,
        max=1,
        default=.2,
        description="Width of the angle in a split")

    gravity_strength = FloatProperty(
        name="Gravity Strength",
        default=0.0)

    gravity_start = IntProperty(
        name="Gravity Start Iteration",
        default=0)

    gravity_end = IntProperty(
        name="Gravity End Iteration",
        default=100)

    obstacle = StringProperty(
        name='Obstacle',
        default='',
        description="Obstacle to avoid. \nWARNING: location,rotaion and scale must be applied. Check the normals.")

    obstacle_strength = FloatProperty(
        name="Obstacle Strength",
        description='Strength with which to avoid obstacles',
        default=1)

    obstacle_flip_normals = BoolProperty(
        name="Flip Normals",
        default=False)

    obstacle_kill = BoolProperty(
        name="Kill Branches",
        default=False,
        description='does not repel branches near the domain object, but ends them')

    SeedProp = IntProperty(
        name="Seed",
        default=randint(0, 1000))

    create_armature = BoolProperty(
        name='Create Armature',
        default=False)

    bones_iterations = IntProperty(
        name='Bones Iterations',
        default=8)

    leafs_iteration_length = IntProperty(
        name='Leafs Group Length',
        default=4,
        description="The number of branches iterations where leafs will appear")

    uv = BoolProperty(
        name="Unwrap",
        default=False,
        description="Unwrap tree")

    mat = BoolProperty(
        name="Create New Material",
        default=False,
        description="NEEDS UV, create tree material")

    roots_iteration = IntProperty(
        name="Roots Iterations",
        default=4)

    roots_split_proba = FloatProperty(
        name="Roots Split Probability",
        default=.25,
        min=0,
        max=1)

    roots_ground_height = FloatProperty(
        name="Ground Height",
        default=0)

    roots_stay_under_ground = BoolProperty(
        name="Stay Under The Ground",
        default=True)

    roots_length = FloatProperty(
        name="Roots Length",
        default=.5,
        min=.005)

    create_roots = BoolProperty(
        name="Create Roots",
        default=True)

    branch_rotate = FloatProperty(
        name="Branches Rotation Angle",
        default=90,
        min=0,
        max=360,
        description="angle between new split and previous split")

    branch_random_rotate = FloatProperty(
        name="Branches Random Rotation Angle",
        default=5,
        min=0,
        max=360,
        description="randomize the rotation of branches angle")

    branch_min_radius = FloatProperty(
        name="Branches minimum radius",
        default=.04,
        min=0,
        description="radius at which a branch breaks for being to small")

    particle = BoolProperty(
        name="Configure Particle System",
        default=False)

    create_particle_emitter = BoolProperty(
        name='create particle emitter',
        default=True)

    number = IntProperty(
        name="Number of Leaves",
        default=10000)

    display = IntProperty(
        name="Particles in Viewport",
        default=500)

    twig_particle = StringProperty(
        name='twig or leaf object',
        default='')

    particle_size = FloatProperty(
        name="twig/leaf size",
        min=0,
        default=1.5)

    break_chance = FloatProperty(
        name="Break Chance",
        default=0.02)

    dont_break_trunk = BoolProperty(
        name="Don't Break Trunk",
        default=True)

    bark_material = StringProperty(
        name="Bark Material")

    leaf_size = FloatProperty(
        name="Leaf Size",
        min=0,
        default=1)

    leaf_chance = FloatProperty(
        name="Leaf Generation Probability",
        min=0,
        default=.5)

    leaf_weight = FloatProperty(
        name="Leaf Weight",
        min=0,
        max=1,
        default=.2)

    twig_bark_material = StringProperty(
        name="Twig Bark Material")

    TwigSeedProp = IntProperty(
        name="Twig Seed",
        default=randint(0, 1000))

    twig_iteration = IntProperty(
        name="Twig Iteration",
        min=3,
        soft_max=10,
        default=9)

    leaf_object = StringProperty(
        name="leaf object",
        default="",
        description="The object used for the leaves.  \nThe leaf must be on Y axis and the rotation must be applied")

    tree_number = IntProperty(
        name="Tree Number",
        min=2,
        default=5)

    batch_radius_randomness = FloatProperty(
        name="Radius Randomness",
        min=0,
        max=1,
        default=.5)

    batch_group_name = StringProperty(
        name="Group")

    batch_space = FloatProperty(
        name="Grid Size",
        min=0,
        default=15,
        description="The distance between the trees")

    wind_controller = StringProperty(
        name="Control Object")

    terrain = StringProperty(
        name="Terrain")

    wind_height_start = FloatProperty(
        name="Start Height",
        min=0,
        default=0,
        description="The distance from the terrain that the wind effect starts affecting tree")

    wind_height_full = FloatProperty(
        name="Full Height",
        min=0,
        default=10,
        description="The distance from the terrain that the wind effect is at its highest")
    
    use_grease_pencil = BoolProperty(
        name="Use Grease Pencil",
        default=False)

    smooth_stroke = FloatProperty(
        name="Smooth Iterations",
        min=0.0,
        max=1,
        default=.2)

    stroke_step_size = FloatProperty(
        name="Step Size",
        min=0,
        default=.5)

    use_force_field = BoolProperty(
        name="Use Force Field",
        default=False)

    fields_point_strength = FloatProperty(
        name="Point Force Strength",
        min=0.0,
        default=1)

    fields_wind_strength = FloatProperty(
        name="Wind Force Strength",
        min=0.0,
        default=1)

    fields_strength_limit = FloatProperty(
        name="Strength Limit",
        min=0,
        default=10,
        description="limits the force so that it can't approaches infinity")

    fields_radius_factor = FloatProperty(
        name="Radius Factor",
        min=0,
        max=1,
        default=.5,
        description="How the branch radius affects the force strength. "
                    "\n0 means big branches are as affected as small ones.")

    pruning = BoolProperty(
        name='pruning',
        default=False)

    pruning_intensity = FloatProperty(
        name="Pruning intensity",
        min=0,
        default=1)

    pruning_resolution = IntProperty(
        name="voxel size",
        min=1,
        default=2)


    use_node_workflow = BoolProperty(
        name="use node workflow",
        default=True)

    node_tree = StringProperty(
        name="node tree",
        default="")

    create_leaf_vertex_group = BoolProperty(
        name='create vertex group for leafs',
        default=True)

    create_vertex_paint = BoolProperty(
        name='create vertex paint layer',
        default=True)



    clear_mods = BoolProperty(name="Clear Modifiers", default=True)

    wind_strength = FloatProperty(name="Wind Strength", default=1)


# classes to register (panels will be in the UI in the order they are listed here)
classes = [MakeTreeOperator, BatchTreeOperator, MakeTwigOperator, UpdateTreeOperator, UpdateTwigOperator,
           SaveTreePresetOperator, RemoveTreePresetOperator, LoadTreePresetOperator, WindOperator,
           MakeControllerOperator, MakeTerrainOperator, SetupNodeTreeOperator,
           MakeTreePanel, BatchTreePanel, RootsAndTrunksPanel, TreeBranchesPanel, AdvancedSettingsPanel,
           MakeTwigPanel, TreePresetLoadMenu, TreePresetRemoveMenu, WindAnimationPanel, MakeTreePresetsPanel,
           InstallTreePresetOperator, TreeAddonPrefs, ModularTreePropertyGroup]
classes += nodes_to_register

prefix = "https://github.com/MaximeHerpin/modular_tree/wiki/"
documentation_mapping = (
    # make tree panel
    ("bpy.ops.mod_tree.add_tree", "Make-Tree-Panel#make-tree"),
    ("bpy.ops.mod_tree.update_tree", "Make-Tree-Panel#update-tree"),
    ("bpy.types.ModularTreePropertyGroup.SeedProp", "Make-Tree-Panel#seed"),
    ("bpy.types.ModularTreePropertyGroup.iteration", "Make-Tree-Panel#branch-iterations"),
    ("bpy.types.ModularTreePropertyGroup.radius", "Make-Tree-Panel#radius"),
    ("bpy.types.ModularTreePropertyGroup.uv", "Make-Tree-Panel#create-uv-seams"),
    # roots and trunk
    ("bpy.types.ModularTreePropertyGroup.create_roots", "Roots-and-Trunk#create-roots"),
    ("bpy.types.ModularTreePropertyGroup.roots_iteration", "Roots-and-Trunk#roots-iterations"),
    ("bpy.types.ModularTreePropertyGroup.trunk_length", "Roots-and-Trunk#trunk-iterations"),
    ("bpy.types.ModularTreePropertyGroup.trunk_variation", "Roots-and-Trunk#trunk-variation"),
    ("bpy.types.ModularTreePropertyGroup.trunk_space", "Roots-and-Trunk#trunk-length"),
    ("bpy.types.ModularTreePropertyGroup.preserve_trunk", "Roots-and-Trunk#preserve-trunk"),
    ("bpy.types.ModularTreePropertyGroup.preserve_end", "Roots-and-Trunk#trunk-end"),
    ("bpy.types.ModularTreePropertyGroup.trunk_split_proba", "Roots-and-Trunk#trunk-split-probability"),
    ("bpy.types.ModularTreePropertyGroup.trunk_split_angle", "Roots-and-Trunk#trunk-split-angle"),
    # branches
    ("bpy.types.ModularTreePropertyGroup.break_chance", "Branches#break-chance"),
    ("bpy.types.ModularTreePropertyGroup.branch_length", "Branches#branch-length"),
    ("bpy.types.ModularTreePropertyGroup.randomangle", "Branches#branch-variations"),
    ("bpy.types.ModularTreePropertyGroup.split_proba", "Branches#split-probability"),
    ("bpy.types.ModularTreePropertyGroup.split_angle", "Branches#split-angle"),
    ("bpy.types.ModularTreePropertyGroup.radius_dec", "Branches#radius-decrease"),
    ("bpy.types.ModularTreePropertyGroup.branch_rotate", "Branches#branches-rotation-angle"),
    ("bpy.types.ModularTreePropertyGroup.branch_random_rotate", "Branches#branches-random-rotation-angle"),
    ("bpy.types.ModularTreePropertyGroup.gravity_strength", "Branches#gravity-strength"),
    ("bpy.types.ModularTreePropertyGroup.gravity_start", "Branches#gravity-start"),
    ("bpy.types.ModularTreePropertyGroup.gravity_end", "Branches#gravity-end"),
    ("bpy.types.ModularTreePropertyGroup.obstacle", "Branches#obstacle"),
    ("bpy.types.ModularTreePropertyGroup.obstacle_strength", "Branches#obstacle-strength"),
    # advanced settings
    ("bpy.types.ModularTreePropertyGroup.mat", "Advanced-Settings#create-new-material"),
    ("bpy.types.ModularTreePropertyGroup.bark_material", "Advanced-Settings#bark-material"),
    ("bpy.types.ModularTreePropertyGroup.create_armature", "Advanced-Settings#create-armature"),
    ("bpy.types.ModularTreePropertyGroup.bones_iterations", "Advanced-Settings#bones-iterations"),
    ("bpy.types.ModularTreePropertyGroup.leafs_iteration_length", "Advanced-Settings#leafs-group-length"),
    ("bpy.types.ModularTreePropertyGroup.particle", "Advanced-Settings#configure-particle-system"),
    ("bpy.types.ModularTreePropertyGroup.number", "Advanced-Settings#number-of-leaves"),
    ("bpy.types.ModularTreePropertyGroup.display", "Advanced-Settings#particles-in-viewport"),
    # batch tree generation
    ("bpy.ops.mod_tree.batch_tree", "Batch-Tree-Generation#batch-tree-generation"),
    ("bpy.types.ModularTreePropertyGroup.tree_number", "Batch-Tree-Generation#tree-number"),
    ("bpy.types.ModularTreePropertyGroup.batch_radius_randomness", "Batch-Tree-Generation#radius-randomness"),
    ("bpy.types.ModularTreePropertyGroup.batch_group_name", "Batch-Tree-Generation#group"),
    ("bpy.types.ModularTreePropertyGroup.batch_space", "Batch-Tree-Generation#grid-size"),
    # make twig
    ("bpy.ops.mod_tree.add_twig", "Make-Twig#create-twig"),
    ("bpy.ops.mod_tree.update_twig", "Make-Twig#update-selected-twig"),
    ("bpy.types.ModularTreePropertyGroup.leaf_size", "Make-Twig#leaf-size"),
    ("bpy.types.ModularTreePropertyGroup.leaf_chance", "Make-Twig#leaf-generation-probability"),
    ("bpy.types.ModularTreePropertyGroup.TwigSeedProp", "Make-Twig#twig-seed"),
    ("bpy.types.ModularTreePropertyGroup.twig_iteration", "Make-Twig#twig-iteration"),
    ("bpy.types.ModularTreePropertyGroup.twig_bark_material", "Make-Twig#twig-bark-material"),
    # wind animation
    ("bpy.ops.mod_tree.animate_wind", "Wind-Animation#animate-wind"),
    ("bpy.ops.mod_tree.make_wind_controller", "Wind-Animation#make-wind-controller"),
    ("bpy.ops.mod_tree.make_terrain", "Wind-Animation#make-terrain"),
    ("bpy.types.ModularTreePropertyGroup.wind_controller", "Wind-Animation#control-object"),
    ("bpy.types.ModularTreePropertyGroup.terrain", "Wind-Animation#terrain-object"),
    ("bpy.types.ModularTreePropertyGroup.wind_height_start", "Wind-Animation#start-height"),
    ("bpy.types.ModularTreePropertyGroup.wind_height_full", "Wind-Animation#full-height"),
    ("bpy.types.ModularTreePropertyGroup.clear_mods", "Wind-Animation#clear-modifiers"),
    ("bpy.types.ModularTreePropertyGroup.wind_strength", "Wind-Animation#wind-strength"),
    # addon preferences
    ("bpy.ops.mod_tree.check_for_updates", "Addon-Preferences#save-blend-file"),
    ("bpy.ops.mod_tree.install_preset", "Addon-Preferences#save-images"),
    ("bpy.types.TreeAddonPrefs.always_save_prior", "Addon-Preferences#save-texts"),
    ("bpy.types.TreeAddonPrefs.save_all_images", "Addon-Preferences#check-for-updates"),
    ("bpy.types.TreeAddonPrefs.save_all_texts", "Addon-Preferences#preset-file"),
    ("bpy.types.TreeAddonPrefs.preset_file", "Addon-Preferences#install-preset"),
    # presets - TODO
)


def doc_map():
    dm = (prefix, documentation_mapping)
    return dm


def register():
    nodeitems_utils.register_node_categories("MOD_TREE_NODES", node_categories)
    register_icons()

    save_addon_name(__name__)

    addon_updater_ops.register(bl_info)

    # register all classes
    for i in classes:
        bpy.utils.register_class(i)

    # register custom manual for add-on documentation
    bpy.utils.register_manual_map(doc_map)

    # register props
    Scene.mtree_props = PointerProperty(type=ModularTreePropertyGroup)


def unregister():

    nodeitems_utils.unregister_node_categories("MOD_TREE_NODES")
    unregister_icons()
    

    addon_updater_ops.unregister()

    # unregister all classes
    for i in classes:
        bpy.utils.unregister_class(i)

    # unregister custom manual for add-on documentation
    bpy.utils.unregister_manual_map(doc_map)

    # unregister props
    del Scene.mtree_props


if __name__ == "__main__":
    display_logo()

    # register addon
    register()
