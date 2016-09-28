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

from mathutils import Vector
from random import random, seed, randint
from math import sqrt

import bpy
from bpy.types import Operator

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

        seed(scene.mtree_props.SeedProp)
        create_tree(scene.cursor_location)

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

        mtree_props = context.scene.mtree_props
        trees = []
        save_radius = mtree_props.radius
        space = mtree_props.batch_space
        seeds = []
        if mtree_props.batch_group_name != "":
            if mtree_props.batch_group_name not in bpy.data.groups:
                bpy.ops.group.create(name=mtree_props.batch_group_name)
        for i in range(mtree_props.tree_number):
            new_seed = randint(0, 1000)
            while new_seed in seeds:
                new_seed = randint(0, 1000)
            pointer = int(sqrt(mtree_props.tree_number))
            pos_x = i % pointer
            pos_y = i // pointer
            seed(new_seed)
            mtree_props.radius = save_radius * (1 + mtree_props.batch_radius_randomness * (.5 - random()) * 2)
            create_tree(Vector((-space * pointer / 2, -space * pointer / 2, 0)) + Vector((pos_x, pos_y, 0)) * space)
            trees.append(bpy.context.active_object)
            if mtree_props.batch_group_name != "":
                bpy.ops.object.group_link(group=mtree_props.batch_group_name)
        for tree in trees:
            tree.select = True

        mtree_props.radius = save_radius
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
        mtree_props = scene.mtree_props

        seed(mtree_props.TwigSeedProp)
        save_preserve_trunk = mtree_props.preserve_trunk
        save_trunk_split_angle = mtree_props.split_angle  # This variable is never used! Should it be?
        save_randomangle = mtree_props.randomangle
        save_trunk_variation = mtree_props.trunk_variation
        save_radius = mtree_props.radius
        save_radius_dec = mtree_props.radius_dec
        save_iteration = mtree_props.iteration
        save_preserve_end = mtree_props.preserve_end
        save_trunk_length = mtree_props.trunk_length
        save_trunk_split_proba = mtree_props.trunk_split_proba
        save_trunk_space = mtree_props.trunk_space
        save_split_proba = mtree_props.split_proba
        save_branch_length = mtree_props.branch_length
        save_split_angle = mtree_props.split_angle
        save_gravity_strength = mtree_props.gravity_strength
        save_gravity_start = mtree_props.gravity_start
        save_gravity_end = mtree_props.gravity_end
        save_obstacle = mtree_props.obstacle
        save_obstacle_strength = mtree_props.obstacle_strength
        save_SeedProp = mtree_props.SeedProp
        save_create_armature = mtree_props.create_armature
        save_bones_iterations = mtree_props.bones_iterations
        save_visualize_leafs = mtree_props.visualize_leafs
        save_leafs_iteration_length = mtree_props.leafs_iteration_length
        save_uv = mtree_props.uv
        save_mat = mtree_props.mat
        save_roots_iteration = mtree_props.roots_iteration
        save_create_roots = mtree_props.create_roots
        save_branch_rotate = mtree_props.branch_rotate
        save_branch_random_rotate = mtree_props.branch_random_rotate
        save_particle = mtree_props.particle
        save_number = mtree_props.number
        save_display = mtree_props.display
        save_break_chance = mtree_props.break_chance

        mtree_props.preserve_trunk = False
        mtree_props.trunk_split_angle = 0
        mtree_props.randomangle = .5
        mtree_props.trunk_variation = .1
        mtree_props.radius = .25
        mtree_props.radius_dec = .85
        mtree_props.iteration = mtree_props.twig_iteration
        mtree_props.preserve_end = 40
        mtree_props.trunk_length = 0
        mtree_props.trunk_split_proba = .2
        mtree_props.trunk_space = .1
        mtree_props.split_proba = .7
        mtree_props.branch_length = 3
        mtree_props.split_angle = .2
        mtree_props.gravity_strength = 0
        mtree_props.gravity_start = 0
        mtree_props.gravity_end = 0
        mtree_props.obstacle = ''
        mtree_props.obstacle_strength = 0
        mtree_props.SeedProp = mtree_props.SeedProp
        mtree_props.create_armature = False
        mtree_props.bones_iterations = 10
        mtree_props.visualize_leafs = False
        mtree_props.leafs_iteration_length = 7
        mtree_props.mat = mtree_props.mat
        mtree_props.roots_iteration = 0
        mtree_props.create_roots = False
        mtree_props.branch_rotate = 0
        mtree_props.branch_random_rotate = 15
        mtree_props.particle = False
        mtree_props.number = 0
        mtree_props.display = 0
        mtree_props.break_chance = 0

        if bpy.data.materials.get("twig bark") is None:
            build_bark_material("twig bark")

        if bpy.data.materials.get("twig leaf") is None:
            build_leaf_material("twig leaf")

        twig_leafs = create_tree(scene.cursor_location, is_twig=True)

        twig = bpy.context.active_object
        twig.name = 'twig'
        twig.active_material = bpy.data.materials.get(mtree_props.twig_bark_material)
        for (position, direction, rotation) in twig_leafs:
            for i in range(randint(1, 3)):
                if random() < mtree_props.leaf_chance:
                    add_leaf(position + direction * .5 * random(), direction + Vector((random(), random(), random())),
                             rotation + random() * 5, (1 + random()) * mtree_props.leaf_size)
                    bpy.context.active_object.active_material = bpy.data.materials.get(mtree_props.twig_leaf_material)
                    twig.select = True
                    scene.objects.active = twig

        bpy.ops.object.join()
        bpy.ops.transform.rotate(value=-1.5708, axis=(1, 0, 0))
        bpy.ops.transform.resize(value=(0.25, 0.25, 0.25))
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        mtree_props.preserve_trunk = save_preserve_trunk
        mtree_props.trunk_split_angle = save_split_angle
        mtree_props.randomangle = save_randomangle
        mtree_props.trunk_variation = save_trunk_variation
        mtree_props.radius = save_radius
        mtree_props.radius_dec = save_radius_dec
        mtree_props.iteration = save_iteration
        mtree_props.preserve_end = save_preserve_end
        mtree_props.trunk_length = save_trunk_length
        mtree_props.trunk_split_proba = save_trunk_split_proba
        mtree_props.trunk_space = save_trunk_space
        mtree_props.split_proba = save_split_proba
        mtree_props.branch_length = save_branch_length
        mtree_props.split_angle = save_split_angle
        mtree_props.gravity_strength = save_gravity_strength
        mtree_props.gravity_start = save_gravity_start
        mtree_props.gravity_end = save_gravity_end
        mtree_props.obstacle = save_obstacle
        mtree_props.obstacle_strength = save_obstacle_strength
        mtree_props.SeedProp = save_SeedProp
        mtree_props.create_armature = save_create_armature
        mtree_props.bones_iterations = save_bones_iterations
        mtree_props.visualize_leafs = save_visualize_leafs
        mtree_props.leafs_iteration_length = save_leafs_iteration_length
        mtree_props.uv = save_uv
        mtree_props.mat = save_mat
        mtree_props.roots_iteration = save_roots_iteration
        mtree_props.create_roots = save_create_roots
        mtree_props.branch_rotate = save_branch_rotate
        mtree_props.branch_random_rotate = save_branch_random_rotate
        mtree_props.particle = save_particle
        mtree_props.number = save_number
        mtree_props.display = save_display
        mtree_props.break_chance = save_break_chance

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

        mtree_props = context.scene.mtree_props

        seed(mtree_props.SeedProp)
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
            ob = context.active_object  # this is the new object that has been set active by 'create_tree'
            ob.scale = scale
            ob.rotation_euler = rot
            ob.select = False
            obj.select = True

            if has_arm_prop:
                arm_pos = obj.parent.location
                arm_scale = obj.parent.scale
                arm_rot = obj.parent.rotation_euler
                obj.parent.select = True

                if mtree_props.create_armature:
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

        mtree_props = context.scene.mtree_props

        seed(mtree_props.SeedProp)
        obj = bpy.context.active_object

        try:
            is_tree_prop = obj.get('is_tree')
        except AttributeError:
            self.report({'ERROR'}, "No active tree object!")
            return {'CANCELLED'}

        if is_tree_prop:
            pos = obj.location  # this is never used...should it be?
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
