from collections import  deque

import bpy
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty, FloatProperty
from mathutils.geometry import intersect_point_line
from mathutils import Vector

from math import cos, inf, pi
from random import random

from.geometry import to_array


def distribute_evenly_along_curve(s, p_dist):
    new_set = []
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


class ConnectStrokes(Operator):
    """move grease pencil strokes so that they are connected to one another"""
    bl_idname = "mtree.connect_strokes"
    bl_label = "connect strokes"
    bl_options = {"REGISTER", "UNDO"}

    point_dist = FloatProperty(min=0.001, default=.8)
    
    def execute(self, context):
        process_gp_layer(self.point_dist)
        return {'FINISHED'}


def find_closest_point(p, s):
    min_dist = inf
    min_index = 0
    for i, p1 in enumerate(s): # finding closest point to p in s
        dist = (p1 - p).length_squared
        if dist < min_dist:
            min_dist = dist
            min_index = i
    p1 = s[min_index]
    if (s[min_index - 1] - p).length_squared < (s[(min_index + 1)%len(s)] - p).length_squared: # finding which one of the neigbours of p1 are closer to p
        p2 = s[min_index - 1]
    else:
        p2 = s[min_index + 1]
    closest_point, percent = intersect_point_line(p, p1, p2) # returns the point closest to p in the line p1 p2
    if not (0 < percent < 1):
        closest_point = p1

    return closest_point, (closest_point - p).length_squared, min_index

def connect_all_strokes(strokes):
    displaced_strokes = [strokes[0]]
    splits = [] # list of (parent_stroke, point_index, child_stroke) used for building tree from gp strokes
    for child_index, s in enumerate(strokes[1:]): # assuming first stroke is the trunk one
        displaced_s = []
        min_dist = inf
        min_p = None
        min_parent_index = 0
        min_point_index = 0
        for parent_index, s1 in enumerate(displaced_strokes): # find closest stroke to s in displaced strokes
            p, dist, point_index = find_closest_point(s[0], s1)
            if dist < min_dist:
                min_dist = dist
                min_p = p
                min_parent_index = parent_index
                min_point_index = point_index
        first_point = s[0]
        displaced_s = [p + (min_p-first_point) for p in s]
        displaced_strokes.append(displaced_s)
        splits.append((min_parent_index, min_point_index, child_index + 1))
    return displaced_strokes, splits

def process_gp_layer(p_dist):
    gp = bpy.context.scene.grease_pencil
    if gp is not None and gp.layers.active is not None and gp.layers.active.active_frame is not None and len(gp.layers.active.active_frame.strokes) > 0 and len(gp.layers.active.active_frame.strokes[0].points) > 1:
        strokes = [[i.co for i in j.points] for j in gp.layers.active.active_frame.strokes]
        for i in range(len(strokes)):
            strokes[i] = distribute_evenly_along_curve(strokes[i], p_dist)
        
        strokes, splits = connect_all_strokes(strokes)

        frame = gp.layers.active.active_frame
        for stroke, s in zip(strokes, frame.strokes):
            for i in range(len(s.points)-len(stroke)):
                s.points.pop()
            s.points.add(len(stroke) - len(s.points))

            for i, p in enumerate(stroke):
                s.points[i].co = p

        return strokes, splits 
