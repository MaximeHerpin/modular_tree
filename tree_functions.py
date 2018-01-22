from random import random, randint
from math import pi
from mathutils import Vector

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty

from .modules import Root, Split, Branch, draw_module_rec
from .grease_pencil import build_tree_from_strokes


def grow(root, iterations, min_radius, limit_method, branch_length, split_proba, split_angle, split_deviation,
         split_radius, radius_decrease, randomness, spin, spin_randomness, creator, selection, gravity_strength):
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

    while condition:
        iteration += 1
        print(iteration, iterations)

        new_extremities = []
        for module, head in extremities:
            radius = module.head_1_radius if head == 0 else module.head_2_radius
            if not (limit_method == "radius" and radius < min_radius):
                position = module.get_head_pos(head)
                direction = module.get_head_direction(head) + Vector((random()-.5, random()-.5, random()-.5))*randomness
                direction.normalize()
                if gravity_strength !=0:
                    direction += Vector((0, 0, -1)) * gravity_strength
                    direction.normalize()
                choice = random()
                if choice < split_proba:
                    new_module = Split(position, direction,
                                       radius, resolution=0, head_2_length=radius*3, spin=module.spin + spin*pi/180)
                    new_module.head_1_length = branch_length
                    new_module.primary_angle = split_deviation
                    new_module.secondary_angle = split_angle*pi/180
                    new_module.head_1_radius = radius_decrease * radius
                    new_module.head_2_radius = split_radius * radius
                else:
                    new_module = Branch(position, direction,
                                        radius, branch_length, radius_decrease, resolution=0,
                                        spin=module.spin + (random()-.5) * spin_randomness)

                new_module.creator = creator

                if head == 0:
                    module.head_module_1 = new_module
                else:
                    module.head_module_2 = new_module
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


def add_splits(root, proba, selection, creator, split_angle, spin, head_size, offset):
    add_splits_rec(root.head_module_1, root, 0, proba, selection, creator, split_angle, spin, root.spin, head_size, offset)


def add_splits_rec(module, parent_module, head, proba, selection, creator, split_angle, spin, curr_spin, head_size, offset):
    if module is not None:
        is_selected = offset <= 0 and (selection == [] or module.creator in selection)
        if module.type == 'branch' and parent_module.head_module_1 is not None and random() < proba and is_selected:
            curr_spin += spin
            split = Split(module.position, module.direction, module.base_radius, module.resolution,
                          module.starting_index, curr_spin, head_2_length=module.base_radius*2,
                          head_2_radius=head_size)
            split.primary_angle = 0
            split.secondary_angle = split_angle*pi/180
            split.head_1_length = module.length
            split.head_module_1 = module.head_module_1
            split.creator = creator
            if head == 0:
                parent_module.head_module_1 = split
            else:
                parent_module.head_module_2 = split
        add_splits_rec(module.head_module_1, module, 0, proba, selection, creator, split_angle, spin, curr_spin, head_size, max(0, offset-1))
        if module.type == 'split':
            add_splits_rec(module.head_module_2, module, 1, proba, selection, creator, split_angle, spin, curr_spin, head_size, max(0, offset-1))

