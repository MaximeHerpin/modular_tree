from random import random, randint
from math import pi
from mathutils import Vector

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty

from .modules import Root, Split, Branch, draw_module_rec
from .grease_pencil import build_tree_from_strokes


def grow(root, iterations, min_radius, limit_method, branch_length, split_proba, split_angle, split_deviation,
         split_radius, radius_decrease, randomness, spin, spin_randomnessn, creator, selection):
    extremities = []
    root.get_extremities_rec(extremities, selection)
    iteration = 0
    if limit_method == "iterations":
        condition = iteration < iterations
    elif limit_method == "radius":
        print('radius')
        condition = root.base_radius < min_radius
        print(root.base_radius)
        condition = True
    else:
        condition = False

    print(condition)

    while condition:
        iteration += 1
        print(iteration, iterations)

        new_extremities = []
        for module, head in extremities:
            radius = module.head_1_radius if head == 0 else module.head_2_radius
            if not (limit_method == "radius" and radius < min_radius):
                position = module.get_head_pos(head)
                direction = module.get_head_direction(head)
                choice = random()
                if choice < split_proba:
                    new_module = Split(position, direction + Vector((random()-.5, random()-.5, random()-.5))*randomness,
                                       radius, resolution=0, head_2_length=radius,
                                       spin=module.spin + spin*pi/180)
                    new_module.primary_angle = split_deviation
                    new_module.secondary_angle = split_angle*pi/180
                    new_module.head_1_radius = radius_decrease * radius
                    new_module.head_2_radius = split_radius * radius
                else:
                    new_module = Branch(position, direction + Vector((random()-.5, random()-.5, random()-.5))*randomness,
                                        radius, branch_length, radius_decrease, resolution=0,
                                        spin=module.spin + (random()-.5) * spin_randomness)

                if head == 0:
                    module.head_module_1 = new_module
                else:
                    module.head_module_2 = new_module
                new_module.creator = creator
                new_extremities.append((new_module, 0))
                if new_module.type == 'split':
                    new_extremities.append((new_module, 1))

        if iteration > iterations and limit_method == 'iterations':
            condition = False

        extremities = new_extremities

        if len(extremities) == 0:
            condition = False


def create_tree(iterations):
    gp = bpy.context.scene.grease_pencil
    if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(
            gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:

        strokes = [[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]
        root = build_tree_from_strokes(strokes)
        add_splits(root, .3)
        # grow(root, iterations)
        draw_module_rec(root)


def add_splits(root, proba, selection):
    add_splits_rec(root.head_module_1, root, 0, proba, selection)


def add_splits_rec(module, parent_module, head, proba, selection):
    if module is not None:
        is_selected = selection == [] or module.creator in selection
        if module.type == 'branch' and random() < proba and is_selected:
            split = Split(module.position, module.direction, module.base_radius, module.resolution,
                          module.starting_index, randint(0, 4)*2*pi, head_2_length=module.base_radius*2)
            split.head_module_1 = module.head_module_1
            if head == 0:
                parent_module.head_module_1 = split
            else:
                parent_module.head_module_2 = split
            module = split
        add_splits_rec(module.head_module_1, module, 0, proba)
        if module.type == 'split':
            pass
            add_splits_rec(module.head_module_2, module, 1, proba)


# class CreateTree(Operator):
#     """creates a tree"""
#     bl_idname = "mod_tree.create_tree"
#     bl_label = "create tree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     iterations = IntProperty(default=5)
#
#     def execute(self, context):
#         create_tree(self.iterations)
#         return {'FINISHED'}


