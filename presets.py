# ##### BEGIN GPL LICENSE BLOCK ######
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences


class TreePresetLoadMenu(Menu):
    bl_idname = "mod_tree.preset_load_menu"
    bl_label = "Load Preset"

    def draw(self, context):
        # get file names
        presets = os.listdir(os.path.join(os.path.dirname(__file__), "mod_tree_presets"))
        presets = [a for a in presets if a[-4:] == ".mtp"]  # limit to only file ending with .mtp

        layout = self.layout
        for preset in presets:
            # this adds a button to the menu for the preset
            # the preset display name has the .mtp sliced off
            # the full preset name is passed the the filename prop of the loader
            layout.operator("mod_tree.load_preset", text=preset[:-4]).filename = preset


class TreePresetRemoveMenu(Menu):
    bl_idname = "mod_tree.preset_remove_menu"
    bl_label = "Remove Preset"

    def draw(self, context):
        # get file names
        presets = os.listdir(os.path.join(os.path.dirname(__file__), "mod_tree_presets"))
        presets = [a for a in presets if a[-4:] == ".mtp"]  # limit to only file ending with .mtp

        layout = self.layout
        for preset in presets:
            # this adds a button to the menu for the preset
            # the preset display name has the .mtp sliced off
            # the full preset name is passed the the filename prop of the loader
            layout.operator("mod_tree.remove_preset", text=preset[:-4]).filename = preset


class SaveTreePresetOperator(Operator):
    """Save Tree Preset"""
    bl_idname = "mod_tree.save_preset"
    bl_label = "Save Preset"
    bl_description = "Saves current settings as a preset"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene = context.scene

        preset = ("finish_unwrap:{}\n"
                  "preserve_trunk:{}\n"
                  "trunk_split_angle:{}\n"
                  "randomangle:{}\n"
                  "trunk_variation:{}\n"
                  "radius:{}\n"
                  "radius_dec:{}\n"
                  "iteration:{}\n"
                  "preserve_end:{}\n"
                  "trunk_length:{}\n"
                  "trunk_split_proba:{}\n"
                  "split_proba:{}\n"
                  "trunk_space:{}\n"
                  "branch_length:{}\n"
                  "split_angle:{}\n"
                  "gravity_strength:{}\n"
                  "gravity_start:{}\n"
                  "gravity_end:{}\n"
                  "obstacle:{}\n"
                  "obstacle_strength:{}\n"
                  "SeedProp:{}\n"
                  "create_armature:{}\n"
                  "bones_iterations:{}\n"
                  "visualize_leafs:{}\n"
                  "leafs_iteration_length:{}\n"
                  "uv:{}\n"
                  "unwrap_end_iteration:{}\n"
                  "mat:{}\n"
                  "roots_iteration:{}\n"
                  "create_roots:{}\n"
                  "branch_rotate:{}\n"
                  "branch_random_rotate:{}\n"
                  "particle:{}\n"
                  "number:{}\n"
                  "display:{}\n"
                  "leaf_size:{}\n"
                  "leaf_chance:{}\n"
                  "twig_leaf_material:{}\n"
                  "twig_bark_material:{}\n"
                  "TwigSeedProp:{}\n"
                  "twig_iteration:{}\n"
                  "tree_number:{}\n"
                  "batch_radius_randomness:{}\n"
                  "batch_group_name:{}\n"
                  "batch_space:{}\n".format(
                    # bools can't be stored as "True" or "False" b/c bool(x) will evaluate to
                    # True if x = "True" or if x = "False"...the fix is to do an int() conversion
                    int(scene.finish_unwrap),
                    int(scene.preserve_trunk),
                    scene.trunk_split_angle,
                    scene.randomangle,
                    scene.trunk_variation,
                    scene.radius,
                    scene.radius_dec,
                    scene.iteration,
                    scene.preserve_end,
                    scene.trunk_length,
                    scene.trunk_split_proba,
                    scene.split_proba,
                    scene.trunk_space,
                    scene.branch_length,
                    scene.split_angle,
                    scene.gravity_strength,
                    scene.gravity_start,
                    scene.gravity_end,
                    scene.obstacle,
                    scene.obstacle_strength,
                    scene.SeedProp,
                    int(scene.create_armature),
                    scene.bones_iterations,
                    int(scene.visualize_leafs),
                    scene.leafs_iteration_length,
                    int(scene.uv),
                    int(scene.unwrap_end_iteration),
                    int(scene.mat),
                    scene.roots_iteration,
                    int(scene.create_roots),
                    scene.branch_rotate,
                    scene.branch_random_rotate,
                    int(scene.particle),
                    scene.number,
                    scene.display,
                    scene.leaf_size,
                    scene.leaf_chance,
                    scene.twig_leaf_material,
                    scene.twig_bark_material,
                    scene.TwigSeedProp,
                    scene.twig_iteration,
                    scene.tree_number,
                    scene.batch_radius_randomness,
                    scene.batch_group_name,
                    scene.batch_space))

        # write to file
        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, scene.preset_name + ".mtp")  # mtp stands for modular tree preset

        os.makedirs(os.path.dirname(prset), exist_ok=True)
        with open(prset, 'w') as p:
            print(preset, file=p, flush=True)

        return {'FINISHED'}


class InstallTreePresetOperator(Operator):
    """Install a tree preset from file"""
    bl_idname = "mod_tree.install_preset"
    bl_label = "Install Preset"
    bl_description = "Installs preset"
    bl_options = {"REGISTER"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        addon_prefs = bpy.context.user_preferences.addons[__name__].preferences

        if not os.path.isfile(addon_prefs.preset_file) or addon_prefs.preset_file[-4:] != ".mtp":
            self.report({'ERROR'}, "Not a valid preset file!")
            return {'CANCELLED'}

        with open(addon_prefs.preset_file, 'r') as p:
            content = p.read()

        # write to file
        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        preset_name = os.path.basename(addon_prefs.preset_file)[:-4]
        prset = os.path.join(prsets_directory, preset_name + ".mtp")  # mtp stands for modular tree preset

        os.makedirs(os.path.dirname(prset), exist_ok=True)
        with open(prset, 'w') as p:
            print(content, file=p, flush=True)

        return {'FINISHED'}


class RemoveTreePresetOperator(Operator):
    """Remove a tree preset"""
    bl_idname = "mod_tree.remove_preset"
    bl_label = "Remove Preset"
    bl_description = "Removes preset"
    bl_options = {"REGISTER"}

    filename = StringProperty(name="File Name")

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, self.filename)  # mtp stands for modular tree preset
        os.remove(prset)

        return {'FINISHED'}


class LoadTreePresetOperator(Operator):
    """Load a tree preset"""
    bl_idname = "mod_tree.load_preset"
    bl_label = "Load Preset"
    bl_description = "Loads preset"
    bl_options = {"REGISTER", "UNDO"}

    filename = StringProperty(name="File Name")

    def execute(self, context):
        scene = context.scene

        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, self.filename)  # mtp stands for modular tree preset
        with open(prset, 'r') as p:
            preset = p.readlines()  # readlines will make a list ie. "a\nb\nc\nd\n" is ["a", "b", "c", "d"]

        # each line should be a preset
        for line in preset:
            # verify that a colon is in the line to avoid an error with line.split(":")
            if ":" in line:
                setting, value = line.split(":")
                if setting == 'finish_unwrap':
                    scene.finish_unwrap = bool(int(value))
                elif setting == "preserve_trunk":
                    scene.preserve_trunk = bool(int(value))  # bools have to be converted to int first (stored as 0/1)
                elif setting == "trunk_split_angle":
                    scene.trunk_split_angle = float(value)
                elif setting == "randomangle":
                    scene.randomangle = float(value)
                elif setting == "trunk_variation":
                    scene.trunk_variation = float(value)
                elif setting == "radius":
                    scene.radius = float(value)
                elif setting == "radius_dec":
                    scene.radius_dec = float(value)
                elif setting == "iteration":
                    scene.iteration = int(value)
                elif setting == "preserve_end":
                    scene.preserve_end = int(value)
                elif setting == "trunk_length":
                    scene.trunk_length = int(value)
                elif setting == "trunk_split_proba":
                    scene.trunk_split_proba = float(value)
                elif setting == "split_proba":
                    scene.split_proba = float(value)
                elif setting == "trunk_space":
                    scene.trunk_space = float(value)
                elif setting == "branch_length":
                    scene.branch_length = float(value)
                elif setting == "split_angle":
                    scene.split_angle = float(value)
                elif setting == "gravity_strength":
                    scene.gravity_strength = float(value)
                elif setting == "gravity_start":
                    scene.gravity_start = int(value)
                elif setting == "gravity_end":
                    scene.gravity_end = int(value)
                elif setting == "obstacle":
                    scene.obstacle = value.replace("\n", "")
                elif setting == "obstacle_strength":
                    scene.obstacle_strength = float(value)
                elif setting == "SeedProp":
                    scene.SeedProp = int(value)
                elif setting == "create_armature":
                    scene.create_armature = bool(int(value))
                elif setting == "bones_iterations":
                    scene.bones_iterations = int(value)
                elif setting == "visualize_leafs":
                    scene.visualize_leafs = bool(int(value))
                elif setting == "leafs_iteration_length":
                    scene.leafs_iteration_length = int(value)
                elif setting == "uv":
                    scene.uv = bool(int(value))
                elif setting == "unwrap_end_iteration":
                    scene.unwrap_end_iteration = int(value)
                elif setting == "mat":
                    scene.mat = bool(int(value))
                elif setting == "roots_iteration":
                    scene.roots_iteration = int(value)
                elif setting == "create_roots":
                    scene.create_roots = bool(int(value))
                elif setting == "branch_rotate":
                    scene.branch_rotate = float(value)
                elif setting == "branch_random_rotate":
                    scene.branch_random_rotate = float(value)
                elif setting == "particle":
                    scene.particle = bool(int(value))
                elif setting == "number":
                    scene.number = int(value)
                elif setting == "display":
                    scene.display = int(value)
                elif setting == "leaf_size":
                    scene.leaf_size = float(value)
                elif setting == "leaf_chance":
                    scene.leaf_chance = float(value)
                elif setting == "twig_leaf_material":
                    scene.twig_leaf_material = value.replace("\n", "")
                elif setting == "twig_bark_material":
                    scene.twig_bark_material = value.replace("\n", "")
                elif setting == "TwigSeedProp":
                    scene.TwigSeedProp = int(value)
                elif setting == "twig_iteration":
                    scene.twig_iteration = int(value)
                elif setting == "tree_number":
                    scene.tree_number = int(value)
                elif setting == "batch_radius_randomness":
                    scene.batch_radius_randomness = float(value)
                elif setting == "batch_group_name":
                    scene.batch_group_name = value.replace("\n", "")
                elif setting == "batch_space":
                    scene.batch_space = float(value)

        return {'FINISHED'}