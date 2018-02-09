from collections import  deque

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty

from .modules import Root, Split, Branch, draw_module, directions_to_spin

from math import cos, inf, pi
from random import random


def distribute_evenly_along_curve(s, p_dist):
    new_set = list()
    new_set.append(s[0])
    i = 1
    while i < len(s):
        n_dist = (s[i] - new_set[-1]).length
        if n_dist >= p_dist:
            new_set.append(new_set[-1] + p_dist / n_dist * (s[i] - new_set[-1]))
        else:
            i += 1
    new_set.append(s[-1])
    return new_set


def smooth_stroke(iterations, smooth, points):
    for i in range(iterations):
        new_points = list()
        new_points.append(points[0])
        for j in range(1, len(points) - 1):
            new_points.append(smooth / 2 * (points[j - 1] + points[j + 1]) + (1 - smooth) * points[j])
        new_points.append(points[-1])
        points = new_points
    return points


def smooth_distribute_gp_layer(gp_layer, dist, smooth_iterations):
    strokes = [[i.co for i in j.points] for j in gp_layer.strokes]
    for i, stroke in enumerate(strokes):
        new_locations = smooth_stroke(smooth_iterations, .3, distribute_evenly_along_curve(stroke, dist))
        points = gp_layer.strokes[i].points
        for k in range(len(new_locations), len(stroke)):
            points.pop()

        for k in range(len(stroke), len(new_locations)):
            points.add()
        # for k in range(len(points)):
        #     points.pop()
        # print(len(points))
        # points.add(len(new_locations))
        for j, point in enumerate(gp_layer.strokes[i].points):
            point.co = new_locations[j]


def find_splits(strokes):
    """ Return a list of (parent_stroke, point_index, child_stroke) representing splits """
    splits = []
    for i in range(len(strokes)):
        point = strokes[i][0]
        for j in range(len(strokes)):
            dist = inf
            dist_index = 0
            if j != i:
                for k, new_point in enumerate(strokes[j]):
                    new_dist = (point - new_point).length
                    if new_dist < dist:
                        dist = new_dist
                        dist_index = k
            if dist < .001:
                splits.append((j, dist_index, i))
    # print(splits)
    return splits


def connect_strokes(moving_stroke, parent_stroke):
    point = moving_stroke[0]
    segment = min([(i - point) for i in parent_stroke]) + point
    projection = segment - point
    return [i + projection for i in moving_stroke]


class ConnectStrokes(Operator):
    """translate a stroke onto another"""
    bl_idname = "mod_tree.connect_strokes"
    bl_label = "connect strokes"
    bl_options = {"REGISTER", "UNDO"}

    point_dist = FloatProperty(min=0.001, default=.8)
    smooth_iterations = IntProperty(min=0, default=1)
    automatic = BoolProperty(default=True)
    connect_all = BoolProperty(default=True)
    child_stroke_index = IntProperty(
        default=-1)
    parent_stroke_index = IntProperty(
        default=0)

    def execute(self, context):
        gp = bpy.context.scene.grease_pencil
        if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(
                 gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:

            smooth_distribute_gp_layer(gp.layers.active.active_frame, self.point_dist, self.smooth_iterations)

            if self.connect_all:
                moving_range = list(range(1, len(gp.layers.active.active_frame.strokes)))
            else:
                moving_range = [self.child_stroke_index]

            for self.child_stroke_index in moving_range:

                moving_stroke = [i.co for i in gp.layers.active.active_frame.strokes[self.child_stroke_index].points]
                if self.automatic:
                    pos = gp.layers.active.active_frame.strokes[self.child_stroke_index].points[0].co
                    min_dist = 10
                    min_index = 500
                    for index, stroke in enumerate(gp.layers.active.active_frame.strokes):
                        if index != self.child_stroke_index % len(gp.layers.active.active_frame.strokes):
                            dist = min([(i.co - pos).length for i in stroke.points])
                            if dist < min_dist:
                                min_index = index
                                min_dist = dist
                    # print(min_index)
                    self.parent_stroke_index = min_index
                parent_stroke = [i.co for i in gp.layers.active.active_frame.strokes[self.parent_stroke_index].points]
                new_locations = connect_strokes(moving_stroke, parent_stroke)
                for i, point in enumerate(gp.layers.active.active_frame.strokes[self.child_stroke_index].points):
                    point.co = new_locations[i]

        return {'FINISHED'}


def build_tree_from_strokes(strokes, radius, radius_dec):
    modules_splits = [None for i in strokes]
    splits = find_splits(strokes)
    tree_pos = strokes[0][0]
    tree_dir = (strokes[0][1] - tree_pos).normalized()
    root = Root(position=tree_pos, direction=tree_dir, radius=radius, resolution=0)
    root.creator = "gp_trunk"
    stroke = deque(strokes[0])
    build_tree_from_strokes_rec(stroke, root, 0, 0, 0, splits, strokes, radius_dec)

    # curr_branch = root
    # for j in range(1, len(stroke)-1):
    #     pos = stroke[j]
    #     dir = stroke[j+1] - pos
    #     module = Branch(pos, dir.normalized(), curr_branch.base_radius, dir.length, 1, resolution=0)
    #     curr_branch.head_module_1 = module
    #     curr_branch = module

    # print(root)
    return root


def build_tree_from_strokes_rec(points, module, head, curr_index, curr_stroke, splits, strokes, radius_dec):
    if len(points)>1:
        pos = points.popleft()
        direction = points[0]-pos
        choice = 'branch'
        radius = module.head_1_radius if head == 0 else module.head_2_radius

        for parent_stroke, point_index, child_stroke in splits:
            if curr_stroke == parent_stroke and point_index == curr_index:
                child_points = deque(strokes[child_stroke])
                child_points.popleft()
                child_points.popleft()
                child_direction = (child_points[0] - pos)
                child_length = child_direction.length
                if child_length < 1.5*radius:
                    for i in range(int(1.5*radius/child_length)):
                        if len(child_points)>1:
                            child_points.popleft()
                child_direction = (child_points[0] - pos)
                child_length = child_direction.length
                child_direction.normalize()
                spin = directions_to_spin(direction, child_direction)
                choice = 'split'
                break
        if choice == 'branch':
            new_module = Branch(pos, direction.normalized(), radius, direction.length, head_radius=radius_dec,
                                resolution=0, spin=module.spin)
        elif choice == 'split':
            new_module = Split(pos, direction.normalized(), radius, 0, 0, spin, head_2_length=child_length)
            if direction.length < radius*.6:
                number_to_pop = int(radius*.6/direction.length)
                for i in range(number_to_pop):
                    if len(points)>1:
                        points.popleft()
                direction = points[0] - pos
            new_module.head_1_length = direction.length
            new_module.head_2_direction = child_direction
            new_module.secondary_angle = direction.angle(child_direction)

        if head == 0:
            module.head_module_1 = new_module
        else:
            module.head_module_2 = new_module
        new_module.creator = "gp_trunk" if curr_stroke == 0 else "gp_branch"
        build_tree_from_strokes_rec(points, new_module, 0, curr_index+1, curr_stroke, splits, strokes, radius_dec)
        if choice == 'split':
            build_tree_from_strokes_rec(child_points, new_module, 1, 2, child_stroke, splits, strokes, radius_dec)

#
# def register():
#     bpy.utils.register_class(ConnectStrokes)
#
#
# def unregister():
#     bpy.utils.unregister_class(ConnectStrokes)
#
# if __name__ == "__main__":
#     register()