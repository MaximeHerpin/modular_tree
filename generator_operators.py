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

from mathutils import Vector, Matrix
from random import random, seed, randint
from math import sqrt

import bpy
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences

from .tree_creator import create_tree, add_leaf
from .prep_manager import save_everything
from .logo import display_logo
from .material_tools import build_bark_material, build_leaf_material


class MakeTreeOperator(Operator):
    """Make a tree"""
    bl_idname = "mod_tree.add_tree"
    bl_label = "Make Tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        scene = context.scene

        seed(scene.SeedProp)
        create_tree(bpy.context.scene.cursor_location)

        return {'FINISHED'}


class BatchTreeOperator(Operator):
    """Batch trees"""
    bl_idname = "mod_tree.batch_tree"
    bl_label = "Batch Tree Generation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        scene = context.scene
        trees = []
        save_radius = scene.radius
        space = scene.batch_space
        seeds = []
        if scene.batch_group_name != "":
            if scene.batch_group_name not in bpy.data.groups:
                bpy.ops.group.create(name=scene.batch_group_name)
        for i in range(scene.tree_number):
            new_seed = randint(0, 1000)
            while new_seed in seeds:
                new_seed = randint(0, 1000)
            pointer = int(sqrt(scene.tree_number))
            pos_x = i % pointer
            pos_y = i // pointer
            seed(new_seed)
            scene.radius = save_radius * (1 + scene.batch_radius_randomness * (.5 - random()) * 2)
            create_tree(Vector((-space * pointer / 2, -space * pointer / 2, 0)) + Vector((pos_x, pos_y, 0)) * space)
            trees.append(bpy.context.active_object)
            if scene.batch_group_name != "":
                bpy.ops.object.group_link(group=scene.batch_group_name)
        for tree in trees:
            tree.select = True

        scene.radius = save_radius
        return {'FINISHED'}


class MakeTwigOperator(Operator):
    """Creates a twig"""
    bl_idname = "mod_tree.add_twig"
    bl_label = "Create Twig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        scene = context.scene
        seed(scene.TwigSeedProp)
        save_preserve_trunk = scene.preserve_trunk
        save_trunk_split_angle = scene.split_angle  # This variable is never used! Should it be?
        save_randomangle = scene.randomangle
        save_trunk_variation = scene.trunk_variation
        save_radius = scene.radius
        save_radius_dec = scene.radius_dec
        save_iteration = scene.iteration
        save_preserve_end = scene.preserve_end
        save_trunk_length = scene.trunk_length
        save_trunk_split_proba = scene.trunk_split_proba
        save_trunk_space = scene.trunk_space
        save_split_proba = scene.split_proba
        save_branch_length = scene.branch_length
        save_split_angle = scene.split_angle
        save_gravity_strength = scene.gravity_strength
        save_gravity_start = scene.gravity_start
        save_gravity_end = scene.gravity_end
        save_obstacle = scene.obstacle
        save_obstacle_strength = scene.obstacle_strength
        save_SeedProp = scene.SeedProp
        save_create_armature = scene.create_armature
        save_bones_iterations = scene.bones_iterations
        save_visualize_leafs = scene.visualize_leafs
        save_leafs_iteration_length = scene.leafs_iteration_length
        save_uv = scene.uv
        save_mat = scene.mat
        save_roots_iteration = scene.roots_iteration
        save_create_roots = scene.create_roots
        save_branch_rotate = scene.branch_rotate
        save_branch_random_rotate = scene.branch_random_rotate
        save_particle = scene.particle
        save_number = scene.number
        save_display = scene.display
        save_break_chance = scene.break_chance

        scene.preserve_trunk = False
        scene.trunk_split_angle = 0
        scene.randomangle = .5
        scene.trunk_variation = .1
        scene.radius = .25
        scene.radius_dec = .85
        scene.iteration = scene.twig_iteration
        scene.preserve_end = 40
        scene.trunk_length = 0
        scene.trunk_split_proba = .2
        scene.trunk_space = .1
        scene.split_proba = .7
        scene.branch_length = 3
        scene.split_angle = .2
        scene.gravity_strength = 0
        scene.gravity_start = 0
        scene.gravity_end = 0
        scene.obstacle = ''
        scene.obstacle_strength = 0
        scene.SeedProp = scene.SeedProp
        scene.create_armature = False
        scene.bones_iterations = 10
        scene.visualize_leafs = False
        scene.leafs_iteration_length = 7
        scene.uv = True
        scene.mat = scene.mat
        scene.roots_iteration = 0
        scene.create_roots = False
        scene.branch_rotate = 0
        scene.branch_random_rotate = 15
        scene.particle = False
        scene.number = 0
        scene.display = 0
        scene.break_chance = 0

        if bpy.data.materials.get("twig bark") is None:
            build_bark_material("twig bark")

        if bpy.data.materials.get("twig leaf") is None:
            build_leaf_material("twig leaf")

        twig_leafs = create_tree(bpy.context.scene.cursor_location, is_twig=True)
        twig = bpy.context.active_object
        twig.name = 'twig'
        twig.active_material = bpy.data.materials.get(scene.twig_bark_material)
        for (position, direction, rotation) in twig_leafs:
            for i in range(randint(1, 3)):
                if random() < scene.leaf_chance:
                    add_leaf(position + direction * .5 * random(), direction + Vector((random(), random(), random())),
                             rotation + random() * 5, (1 + random()) * scene.leaf_size)
                    bpy.context.active_object.active_material = bpy.data.materials.get(scene.twig_leaf_material)
                    twig.select = True
                    scene.objects.active = twig
        bpy.ops.object.join()
        bpy.ops.transform.rotate(value=-1.5708, axis=(1, 0, 0))
        bpy.ops.transform.resize(value=(0.25, 0.25, 0.25))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        scene.preserve_trunk = save_preserve_trunk
        scene.trunk_split_angle = save_split_angle
        scene.randomangle = save_randomangle
        scene.trunk_variation = save_trunk_variation
        scene.radius = save_radius
        scene.radius_dec = save_radius_dec
        scene.iteration = save_iteration
        scene.preserve_end = save_preserve_end
        scene.trunk_length = save_trunk_length
        scene.trunk_split_proba = save_trunk_split_proba
        scene.trunk_space = save_trunk_space
        scene.split_proba = save_split_proba
        scene.branch_length = save_branch_length
        scene.split_angle = save_split_angle
        scene.gravity_strength = save_gravity_strength
        scene.gravity_start = save_gravity_start
        scene.gravity_end = save_gravity_end
        scene.obstacle = save_obstacle
        scene.obstacle_strength = save_obstacle_strength
        scene.SeedProp = save_SeedProp
        scene.create_armature = save_create_armature
        scene.bones_iterations = save_bones_iterations
        scene.visualize_leafs = save_visualize_leafs
        scene.leafs_iteration_length = save_leafs_iteration_length
        scene.uv = save_uv
        scene.mat = save_mat
        scene.roots_iteration = save_roots_iteration
        scene.create_roots = save_create_roots
        scene.branch_rotate = save_branch_rotate
        scene.branch_random_rotate = save_branch_random_rotate
        scene.particle = save_particle
        scene.number = save_number
        scene.display = save_display
        scene.break_chance = save_break_chance

        return {'FINISHED'}


class UpdateTreeOperator(Operator):
    """Update a tree"""
    bl_idname = "mod_tree.update_tree"
    bl_label = "Update Selected Tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        scene = context.scene

        seed(scene.SeedProp)
        obj = bpy.context.active_object

        try:
            is_tree_prop = obj.get('is_tree')
            has_arm_prop = obj.get('has_armature')
        except AttributeError:
            self.report({'ERROR'}, "No active tree object!")
            return {'CANCELLED'}

        if is_tree_prop:
            pos = obj.location
            scale = obj.scale
            rot = obj.rotation_euler
            create_tree(pos)
            ob = bpy.context.active_object  # this is the new object that has been set active by 'create_tree'
            ob.scale = scale
            ob.rotation_euler = rot
            ob.select = False
            obj.select = True

            if has_arm_prop:
                arm_pos = obj.parent.location
                arm_scale = obj.parent.scale
                arm_rot = obj.parent.rotation_euler
                obj.parent.select = True

                if scene.create_armature:
                    ob.parent.location = arm_pos
                    ob.parent.scale = arm_scale
                    ob.parent.rotation_euler = arm_rot
                else:
                    ob.location = arm_pos
                    ob.scale = arm_scale
                    ob.rotation_euler = arm_rot

            bpy.ops.object.delete(use_global=False)
            ob.select = True

        else:
            self.report({'ERROR'}, "No active tree object!")
            return {'CANCELLED'}

        return {'FINISHED'}


class UpdateTwigOperator(Operator):
    """Update a twig"""
    bl_idname = "mod_tree.update_twig"
    bl_label = "Update Selected Twig"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        scene = context.scene

        seed(scene.SeedProp)
        obj = bpy.context.active_object

        try:
            is_tree_prop = obj.get('is_tree')
        except AttributeError:
            self.report({'ERROR'}, "No active tree object!")
            return {'CANCELLED'}

        if is_tree_prop:
            pos = obj.location
            scale = obj.scale
            rot = obj.rotation_euler
            bpy.ops.mod_tree.add_twig()
            ob = bpy.context.active_object  # this is the new object that has been set active by 'create_tree'
            ob.scale = scale
            ob.rotation_euler = rot
            ob.select = False
            obj.select = True
            bpy.ops.object.delete(use_global=False)
            ob.select = True

        else:
            self.report({'ERROR'}, "No active twig object!")
            return {'CANCELLED'}

        return {'FINISHED'}
