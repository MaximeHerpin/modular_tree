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

import os

import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, EnumProperty
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences

import pickle

from .addon_name import get_addon_name


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
        mtree_props = context.scene.mtree_props
        # doing it all by hand is tedious, with this we have something like "[(name1,value1), (name2,value2), ...]"
        props = mtree_props.items()

        # write to file
        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, mtree_props.preset_name + ".mtp")  # mtp stands for modular tree preset

        os.makedirs(os.path.dirname(prset), exist_ok=True)
        with open(prset, 'wb') as p:
            pickle.dump(props, p)

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
        addon_prefs = bpy.context.user_preferences.addons[get_addon_name()].preferences

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
        mtree_props = context.scene.mtree_props

        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, self.filename)  # mtp stands for modular tree preset
        "M"  # mtp stands for modular tree preset
        with open(prset, 'rb') as p:
            presets = pickle.load(p)

        for (name, value) in presets:
            mtree_props[name] = value

        return {'FINISHED'}