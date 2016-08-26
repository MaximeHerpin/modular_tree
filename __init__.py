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

bl_info = {
    "name": "Modular trees",
    "author": "Herpin Maxime, Jake Dube",
    "version": (2, 2),
    "blender": (2, 77, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Generates an organic tree with correctly modeled branching.",
    "warning": "May take a long time to generate! Save your file before generating!",
    "wiki_url": "https://github.com/MaximeHerpin/Blender-Modular-tree-addon/wiki",
    "tracker_url": "https://github.com/MaximeHerpin/Blender-Modular-tree-addon/issues/new",
    "category": "Add Mesh"}

from random import randint

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences

from modular_tree.generator_operators import MakeTreeOperator, BatchTreeOperator, MakeTwigOperator, UpdateTreeOperator, UpdateTwigOperator
from modular_tree.presets import TreePresetLoadMenu, TreePresetRemoveMenu, SaveTreePresetOperator, InstallTreePresetOperator, RemoveTreePresetOperator, LoadTreePresetOperator
from modular_tree.logo import display_logo
from modular_tree.wind_setup_utils import WindOperator, MakeControllerOperator, MakeTerrainOperator


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

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, 'always_save_prior')
        row = layout.row()
        row.prop(self, 'save_all_images')
        row = layout.row()
        row.prop(self, 'save_all_texts')

        row = layout.row()
        # website url
        row.operator("wm.url_open", text="Feature Roadmap", icon='QUESTION').url = \
            "https://github.com/MaximeHerpin/Blender-Modular-tree-addon/wiki/Roadmap"
        row.operator("wm.url_open", text="Official Discussion Forum", icon='QUESTION').url = \
            "https://blenderartists.org/forum/showthread.php?405377-Addon-Modular-Tree"

        box = layout.box()
        box.label("Preset Installer")
        box.prop(self, 'preset_file')
        box.operator("mod_tree.install_preset")


class MakeTreePanel(Panel):
    bl_label = "Make Tree"
    bl_idname = "3D_VIEW_PT_layout_MakeTree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.add_tree", icon="WORLD")

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.update_tree", icon="FILE_REFRESH")

        box = layout.box()
        box.label("Basic")
        box.prop(scene, "SeedProp")
        box.prop(scene, "iteration")
        box.prop(scene, 'radius')
        box.prop(scene, 'uv')
        if scene.uv:
            box.prop(scene, 'finish_unwrap')
            if scene.finish_unwrap:
                box.prop(scene, "unwrap_end_iteration")


class BatchTreePanel(Panel):
    bl_label = "Batch Tree Generation"
    bl_idname = "3D_VIEW_PT_layout_BatchTree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.batch_tree", icon="LOGIC")
        box = layout.box()
        box.prop(scene, "tree_number")
        box.prop(scene, "batch_radius_randomness")
        box.prop_search(scene, "batch_group_name", bpy.data, "groups")
        box.prop(scene, "batch_space")
 

class RootsAndTrunksPanel(Panel):
    bl_label = "Roots and Trunk"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeRootsAndTrunks"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        box.label("Roots")
        box.prop(scene, 'create_roots')
        if scene.create_roots:
            box.prop(scene, 'roots_iteration')

        box = layout.box()
        box.label("Trunk")
        box.prop(scene, 'trunk_length')
        box.prop(scene, 'trunk_variation')
        box.prop(scene, 'trunk_space')
        sbox = box.box()
        sbox.prop(scene, 'preserve_trunk')
        if scene.preserve_trunk:
            sbox.prop(scene, 'preserve_end')
            sbox.prop(scene, 'trunk_split_proba')
            sbox.prop(scene, 'trunk_split_angle')


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
        layout = self.layout

        box = layout.box()
        box.label("Branches")
        box.prop(scene, 'break_chance')
        box.prop(scene, 'branch_length')
        box.prop(scene, 'randomangle')
        box.prop(scene, 'split_proba')
        box.prop(scene, 'split_angle')
        box.prop(scene, 'radius_dec')
        col = box.column(align=True)
        col.prop(scene, 'branch_rotate')
        col.prop(scene, 'branch_random_rotate')

        box = layout.box()
        col = box.column(True)
        col.prop(scene, 'gravity_strength')
        col.prop(scene, 'gravity_start')
        col.prop(scene, 'gravity_end')
        box.prop_search(scene, "obstacle", scene, "objects")
        if bpy.data.objects.get(scene.obstacle) is not None:
            box.prop(scene, 'obstacle_strength')


class AdvancedSettingsPanel(Panel):
    bl_label = "Advanced Settings"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeAdvancedSettings"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        box.prop(scene, 'mat')
        if not scene.mat:
            box.prop_search(scene, "bark_material", bpy.data, "materials")
        box.prop(scene, 'create_armature')
        if scene.create_armature:
            box.prop(scene, 'bones_iterations')
        box.prop(scene, 'visualize_leafs')
        box.prop(scene, 'leafs_iteration_length')
        box.prop(scene, 'particle')
        if scene.particle:
            box.prop(scene, 'number')
            box.prop(scene, 'display')


class WindAnimationPanel(Panel):
    bl_label = "Wind Animation"
    bl_idname = "3D_VIEW_PT_layout_MakeTreeWindAnimation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("mod_tree.animate_wind", icon="FORCE_VORTEX")
        box.operator("mod_tree.make_wind_controller", icon="FORCE_VORTEX")
        box.operator("mod_tree.make_terrain", icon="FORCE_VORTEX")
        box.prop_search(scene, "wind_controller", bpy.data, "objects")
        box.prop_search(scene, "terrain", bpy.data, "objects")
        box.prop(scene, "wind_height_start")
        box.prop(scene, "wind_height_full")
        box.prop(scene, "clear_mods")
        box.prop(scene, "wind_strength")


class MakeTwigPanel(Panel):
    bl_label = "Make Twig"
    bl_idname = "3D_VIEW_PT_layout_MakeTwig"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.add_twig", icon="SCULPTMODE_HLT")
        
        row = layout.row()
        row.scale_y = 1.5
        row.operator("mod_tree.update_twig", icon="FILE_REFRESH")

        box = layout.box()
        box.label("Twig Options")
        box.prop(scene, "leaf_size")
        box.prop(scene, "leaf_chance")
        box.prop(scene, "TwigSeedProp")
        box.prop(scene, "twig_iteration")
        box.prop_search(scene, "twig_bark_material", bpy.data, "materials")
        box.prop_search(scene, "twig_leaf_material", bpy.data, "materials")           


class MakeTreePresetsPanel(Panel):
    bl_label = "Presets"
    bl_idname = "3D_VIEW_PT_layout_MakeTreePresets"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        row = layout.row()
        row.scale_y = 1.25
        row.menu("mod_tree.preset_load_menu")

        row = layout.row(align=True)
        row.prop(scene, "preset_name", text="")
        row.operator("mod_tree.save_preset", icon="SETTINGS")

        row = layout.row()
        row.menu("mod_tree.preset_remove_menu")


# classes to register (panels will be in the UI in the order they are listed here)
classes = [MakeTreeOperator, BatchTreeOperator, MakeTwigOperator, UpdateTreeOperator, UpdateTwigOperator,
           SaveTreePresetOperator, RemoveTreePresetOperator, LoadTreePresetOperator, WindOperator,
           MakeControllerOperator, MakeTerrainOperator,
           MakeTreePanel, BatchTreePanel, RootsAndTrunksPanel, TreeBranchesPanel, AdvancedSettingsPanel,
           MakeTwigPanel, TreePresetLoadMenu, TreePresetRemoveMenu, WindAnimationPanel, MakeTreePresetsPanel,
           InstallTreePresetOperator,
           TreeAddonPrefs]


def register():
    # register all classes
    for i in classes:
        bpy.utils.register_class(i)

    # register props
    Scene.preset_name = StringProperty(name="Preset Name", default="MyPreset")

    Scene.finish_unwrap = BoolProperty(name="Unwrap",
                                       description="Run 'Unwrap' operator. WARNING: slow, enable for final only",
                                       default=True)

    Scene.preserve_trunk = BoolProperty(
        name="Preserve Trunk", default=False,
        description="preserves the trunk growth, check and see.")

    Scene.trunk_split_angle = FloatProperty(
        name="Trunk Split Angle",
        min=0.0,
        max=1,
        default=0,
        description="how wide is the angle in a split if this split comes from the trunk")

    Scene.randomangle = FloatProperty(
        name="Branch Variations",
        default=.5)

    Scene.trunk_variation = FloatProperty(
        name="Trunk Variation",
        default=.1)

    Scene.radius = FloatProperty(
        name="Radius",
        min=0.01,
        default=1)

    Scene.radius_dec = FloatProperty(
        name="Radius Decrease",
        min=0.01,
        max=1.0,
        default=0.95,
        description="Relative radius after each iteration, low value means fast radius decrease")

    Scene.iteration = IntProperty(
        name="Branch Iterations",
        min=2,
        soft_max=30,
        default=20)

    Scene.preserve_end = IntProperty(
        name="Trunk End",
        min=0,
        default=25,
        description="iteration on which trunk preservation will end")

    Scene.trunk_length = IntProperty(
        name="Trunk Iterations",
        min=5,
        default=9,
        description="Iteration from from which first split occurs")

    Scene.trunk_split_proba = FloatProperty(
        name="Trunk Split Probability",
        min=0.0,
        max=1.0,
        default=0.5,
        description="probability for a branch to split. WARNING : sensitive")

    Scene.split_proba = FloatProperty(
        name="Split Probability",
        min=0.0,
        max=1.0,
        default=0.25,
        description="Probability for a branch to split. \nWARNING : sensitive")

    Scene.trunk_space = FloatProperty(
        name="Trunk Length",
        min=0.01,
        default=.7,
        description="Length of the trunk")

    Scene.branch_length = FloatProperty(
        name="Branch Length",
        min=0.01,
        default=.55,
        description="Branch length")

    Scene.split_angle = FloatProperty(
        name="Split Angle",
        min=0.0,
        max=1,
        default=.2,
        description="Width of the angle in a split")

    Scene.gravity_strength = FloatProperty(
        name="Gravity Strength",
        default=0.0)

    Scene.gravity_start = IntProperty(
        name="Gravity Start Iteration",
        default=0)

    Scene.gravity_end = IntProperty(
        name="Gravity End Iteration",
        default=40)

    Scene.obstacle = StringProperty(
        name='Obstacle',
        default='',
        description="Obstacle to avoid. \nWARNING: location,rotaion and scale must be applied. Check the normals.")

    Scene.obstacle_strength = FloatProperty(
        name="Obstacle Strength",
        description='Strength with which to avoid obstacles',
        default=1)

    Scene.SeedProp = IntProperty(
        name="Seed",
        default=randint(0, 1000))

    Scene.create_armature = BoolProperty(
        name='Create Armature',
        default=False)

    Scene.bones_iterations = IntProperty(
        name='Bones Iterations',
        default=8)

    Scene.visualize_leafs = BoolProperty(
        name='Visualize Particle Weights',
        default=False)

    Scene.leafs_iteration_length = IntProperty(
        name='Leafs Group Length',
        default=4,
        description="The number of branches iterations where leafs will appear")

    Scene.uv = BoolProperty(
        name="Create UV Seams",
        default=False,
        description="Create uv seams for tree (enable unwrap to auto unwrap)")
    
    Scene.unwrap_end_iteration = IntProperty(
        name="Last Unwrapped Iteration",
        min=1,
        soft_max=20,
        default=8)

    Scene.mat = BoolProperty(
        name="Create New Material",
        default=False,
        description="NEEDS UV, create tree material")

    Scene.roots_iteration = IntProperty(
        name="Roots Iterations",
        default=4)

    Scene.create_roots = BoolProperty(
        name="Create Roots",
        default=False)

    Scene.branch_rotate = FloatProperty(
        name="Branches Rotation Angle",
        default=90,
        min=0,
        max=360,
        description="angle between new split and previous split")

    Scene.branch_random_rotate = FloatProperty(
        name="Branches Random Rotation Angle",
        default=5,
        min=0,
        max=360,
        description="randomize the rotation of branches angle")

    Scene.particle = BoolProperty(
        name="Configure Particle System",
        default=False)

    Scene.number = IntProperty(
        name="Number of Leaves",
        default=10000)

    Scene.display = IntProperty(
        name="Particles in Viewport",
        default=500)

    Scene.break_chance = FloatProperty(
        name="Break Chance",
        default=0.02)

    Scene.bark_material = StringProperty(
        name="Bark Material")
    
    Scene.leaf_size = FloatProperty(
        name="Leaf Size",
        min=0,
        default=1)
    
    Scene.leaf_chance = FloatProperty(
        name="Leaf Generation Probability",
        min=0,
        default=.5)
    
    Scene.twig_leaf_material = StringProperty(
        name="Leaf Material")
    
    Scene.twig_bark_material = StringProperty(
        name="Twig Bark Material")
    
    Scene.TwigSeedProp = IntProperty(
        name="Twig Seed",
        default=randint(0, 1000))
    
    Scene.twig_iteration = IntProperty(
        name="Twig Iteration",
        min=3,
        soft_max=10,
        default=9)
    
    Scene.tree_number = IntProperty(
        name="Tree Number",
        min=2,
        default=5)
    
    Scene.batch_radius_randomness = FloatProperty(
        name="Radius Randomness",
        min=0,
        max=1,
        default=.5)
    
    Scene.batch_group_name = StringProperty(
        name="Group")
    
    Scene.batch_space = FloatProperty(
        name="Grid Size",
        min=0,
        default=10,
        description="The distance between the trees")

    Scene.wind_controller = StringProperty(
        name="Control Object")

    Scene.terrain = StringProperty(
        name="Terrain")

    Scene.wind_height_start = FloatProperty(
        name="Start Height",
        min=0,
        default=0,
        description="The distance from the terrain that the wind effect starts affecting tree")

    Scene.wind_height_full = FloatProperty(
        name="Full Height",
        min=0,
        default=10,
        description="The distance from the terrain that the wind effect is at its highest")

    Scene.clear_mods = BoolProperty(name="Clear Modifiers", default=True)

    Scene.wind_strength = FloatProperty(name="Wind Strength", default=1)


def unregister():
    # unregister all classes
    for i in classes:
        bpy.utils.unregister_class(i)

    # unregister props
    del Scene.preset_name
    del Scene.finish_unwrap
    del Scene.preserve_trunk
    del Scene.trunk_split_angle
    del Scene.randomangle
    del Scene.trunk_variation
    del Scene.radius
    del Scene.radius_dec
    del Scene.iteration
    del Scene.preserve_end
    del Scene.trunk_length
    del Scene.trunk_split_proba
    del Scene.split_proba
    del Scene.trunk_space
    del Scene.branch_length
    del Scene.split_angle
    del Scene.gravity_strength
    del Scene.gravity_start
    del Scene.gravity_end
    del Scene.obstacle
    del Scene.obstacle_strength
    del Scene.SeedProp
    del Scene.create_armature
    del Scene.bones_iterations
    del Scene.visualize_leafs
    del Scene.leafs_iteration_length
    del Scene.uv
    del Scene.unwrap_end_iteration
    del Scene.mat
    del Scene.roots_iteration
    del Scene.create_roots
    del Scene.branch_rotate
    del Scene.branch_random_rotate
    del Scene.particle
    del Scene.number
    del Scene.display
    del Scene.leaf_size
    del Scene.leaf_chance
    del Scene.twig_leaf_material
    del Scene.twig_bark_material
    del Scene.TwigSeedProp
    del Scene.twig_iteration
    del Scene.tree_number
    del Scene.batch_radius_randomness
    del Scene.batch_group_name
    del Scene.batch_space
    del Scene.wind_controller
    del Scene.terrain
    del Scene.wind_height_start
    del Scene.wind_height_full
    del Scene.clear_mods
    del Scene.wind_strength


if __name__ == "__main__":
    display_logo()

    # register addon
    register()
