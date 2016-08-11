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


bl_info = {
    "name": "Modular trees",
    "author": "Herpin Maxime, Jake Dube",
    "version": (1, 1),
    "blender": (2, 77, 0),
    "location": "View3D > Tools > Tree > Make Tree",
    "description": "Generates an organic tree with correctly modeled branching.",
    "warning": "May take a long time to generate! Save your file before generating!",
    "wiki_url": "",
    "category": "Add Mesh"}

import os
from mathutils import *
from random import *
from math import *

import bpy
from bpy.props import *
from bpy.types import Operator, Panel, Scene, Menu
import bmesh
from collections import defaultdict


class Module:
    def __init__(self, entree, sortie, verts, faces):
        self.entree = entree
        self.sortie = sortie
        self.verts = verts
        self.faces = faces

    def __repr__(self):
        return 'entry vertices:{} , number of splits:{}'.format(len(self.entree), len(self.sortie))


end_cap = Module(
    [0, 1, 2, 3, 4, 5, 6, 7],
    [],
    [(0.0, 1.0, 0.02), (-0.71, 0.71, 0.02), (-1.0, -0.0, 0.04), (-0.71, -0.71, 0.04), (0.0, -1.0, 0.02),
     (0.71, -0.71, 0.02), (1.0, 0.0, 0.04), (0.71, 0.71, 0.04), (0.0, 0.98, 0.14), (-0.69, 0.69, 0.14),
     (-0.98, -0.0, 0.21), (-0.69, -0.69, 0.21), (0.0, -0.98, 0.14), (0.69, -0.69, 0.14), (0.98, 0.0, 0.21),
     (0.69, 0.69, 0.21), (0.0, 0.88, 0.26), (-0.62, 0.62, 0.26), (-0.88, -0.0, 0.33), (-0.62, -0.62, 0.33),
     (0.0, -0.88, 0.26), (0.62, -0.62, 0.26), (0.88, 0.0, 0.33), (0.62, 0.62, 0.33), (0.0, 0.74, 0.32),
     (-0.52, 0.52, 0.32), (-0.74, -0.0, 0.41), (-0.52, -0.52, 0.41), (0.0, -0.74, 0.32), (0.52, -0.52, 0.32),
     (0.74, 0.0, 0.41), (0.52, 0.52, 0.41), (0.0, 0.33, 0.59), (-0.23, 0.23, 0.59), (-0.26, 0.02, 0.67),
     (-0.16, -0.2, 0.67), (0.0, -0.33, 0.59), (0.23, -0.23, 0.59), (0.26, -0.02, 0.67), (0.16, 0.2, 0.67)],
    [(7, 15, 14, 6), (5, 13, 12, 4), (3, 11, 10, 2), (0, 8, 15, 7), (6, 14, 13, 5), (4, 12, 11, 3), (2, 10, 9, 1),
     (15, 8, 16, 23), (13, 14, 22, 21), (11, 12, 20, 19), (9, 10, 18, 17), (14, 15, 23, 22), (12, 13, 21, 20),
     (10, 11, 19, 18), (8, 9, 17, 16), (18, 19, 27, 26), (16, 17, 25, 24), (23, 16, 24, 31), (21, 22, 30, 29),
     (19, 20, 28, 27), (17, 18, 26, 25), (22, 23, 31, 30), (20, 21, 29, 28), (30, 31, 39, 38), (28, 29, 37, 36),
     (26, 27, 35, 34), (24, 25, 33, 32), (31, 24, 32, 39), (29, 30, 38, 37), (27, 28, 36, 35), (35, 38, 39, 34),
     (39, 32, 33, 34), (35, 36, 37, 38), (1, 9, 8, 0), (25, 26, 34, 33)])


class Split:
    def __init__(self, entree, sortie, verts1, verts2, faces, seams):
        self.entree = entree
        self.sortie = sortie
        self.verts1 = verts1
        self.verts2 = verts2
        self.faces = faces
        self.Seams = seams


def interpolate(verts1, verts2, t):
    return [Vector(verts1[i]) * (1 - t) + Vector(verts2[i]) * t for i in range(len(verts1))]


S2 = Split([0, 1, 2, 3, 4, 5, 6, 7], ([8, 9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22, 23]),
           [(-0.0, 1.0, -0.01), (-0.71, 0.71, -0.01), (-1.0, -0.0, -0.01), (-0.71, -0.71, -0.01), (0.0, -1.0, -0.01),
            (0.71, -0.71, -0.01), (1.0, -0.0, -0.02), (0.71, 0.71, -0.02), (-0.98, 0.89, 1.84), (-1.49, 0.74, 1.62),
            (-1.78, 0.24, 1.53), (-1.67, -0.33, 1.64), (-1.23, -0.64, 1.87), (-0.73, -0.51, 2.09), (-0.46, 0.0, 2.18),
            (-0.56, 0.59, 2.07), (0.72, 1.02, 1.8), (1.3, 0.65, 1.8), (1.29, -0.07, 1.93), (0.81, -0.6, 2.07),
            (0.12, -0.57, 2.13), (-0.37, -0.06, 2.17), (-0.46, 0.62, 2.06), (0.03, 1.05, 1.88), (-1.19, -0.63, 0.6),
            (-1.42, -0.01, 0.52), (-0.71, -1.0, 0.98), (-0.39, -0.91, 1.36), (0.63, -0.72, 1.11), (-0.2, -0.73, 1.49),
            (0.85, 0.64, 0.64), (1.12, 0.01, 0.68), (0.28, 0.97, 0.69), (-0.72, 0.91, 0.89), (-1.21, 0.7, 0.6),
            (-0.36, 0.92, 1.36), (-0.43, -1.0, 0.68), (0.13, -1.05, 0.69), (-.42, .09, .90), (.13, .16, .97)],
           [(-0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
            (0.71, -0.71, 0.0), (1.0, -0.0, -0.0), (0.71, 0.71, -0.01), (-1.34, 0.76, 0.99), (-1.43, 0.53, 0.47),
            (-1.47, -0.01, 0.25), (-1.43, -0.56, 0.48), (-1.33, -0.79, 1.0), (-1.24, -0.58, 1.51), (-1.21, -0.03, 1.72),
            (-1.26, 0.57, 1.53), (0.73, 1.02, 1.08), (1.08, 0.65, 0.61), (1.18, -0.07, 0.7), (1.0, -0.6, 1.16),
            (0.63, -0.57, 1.75), (0.35, -0.06, 2.16), (0.21, 0.62, 2.16), (0.38, 1.05, 1.67), (-0.94, -0.63, 0.26),
            (-1.12, -0.01, 0.09), (-0.8, -1.0, 0.78), (-0.59, -0.81, 1.45), (0.75, -0.72, 0.94), (-0.07, -0.51, 1.66),
            (0.84, 0.64, 0.42), (1.12, 0.01, 0.39), (0.31, 0.97, 0.63), (-0.79, 0.91, 0.69), (-0.96, 0.7, 0.25),
            (-0.38, 0.92, 1.37), (-0.43, -1.0, 0.69), (0.13, -1.05, 0.7), (-.98, 0, .16), (.85, .16, .49)],
           [(25, 24, 11, 10), (15, 14, 21, 22), (2, 3, 24, 25), (12, 26, 27, 13), (12, 11, 24, 26), (20, 29, 28, 19),
            (20, 21, 14, 29), (14, 13, 27, 29), (31, 30, 17, 18), (30, 32, 16, 17), (7, 0, 32, 30), (6, 7, 30, 31),
            (18, 19, 28, 31), (8, 33, 34, 9), (9, 34, 25, 10), (1, 2, 25, 34), (15, 35, 33, 8), (23, 35, 15, 22),
            (35, 23, 16, 32), (33, 35, 32, 0), (34, 33, 0, 1), (5, 6, 31, 28), (36, 26, 24, 3), (37, 36, 3, 4),
            (4, 5, 28, 37), (27, 26, 36, 37), (28, 29, 27, 37)],
           [(4, 37), (36, 37), (26, 36), (12, 26), (28, 37), (19, 28), (14, 21)])

S1 = Split([0, 1, 2, 3, 4, 5, 6, 7], ([8, 9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22, 23]),
           [(0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
            (0.71, -0.71, 0.0), (1.0, 0.0, 0.0), (0.71, 0.71, 0.0), (-0.0, -0.17, 1.01), (-0.42, -0.29, 0.88),
            (-0.59, -0.58, 0.58), (-0.42, -0.88, 0.29), (0.0, -1.0, 0.16), (0.42, -0.88, 0.29), (0.59, -0.58, 0.58),
            (0.42, -0.29, 0.88), (-0.0, 1.0, 0.17), (-0.43, 0.88, 0.29), (-0.61, 0.57, 0.6), (-0.43, 0.26, 0.9),
            (0.0, 0.13, 1.02), (0.43, 0.26, 0.9), (0.61, 0.57, 0.6), (0.43, 0.88, 0.29), (0.85, 0.44, 0.37),
            (0.91, -0.38, 0.42), (0.79, 0.04, 0.65), (0.0, -0.02, 1.02), (0.43, -0.02, 0.89), (-0.43, -0.02, 0.89),
            (-0.91, -0.38, 0.41), (-0.82, 0.04, 0.65), (-0.91, 0.44, 0.37), (0, -1, 1), (0, 1, 1)],
           [(0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
            (0.71, -0.71, 0.0), (1.0, 0.0, 0.0), (0.71, 0.71, 0.0), (-0.0, -0.17, 1.01), (-0.42, -0.29, 0.88),
            (-0.59, -0.58, 0.58), (-0.42, -0.88, 0.29), (0.0, -1.0, 0.16), (0.42, -0.88, 0.29), (0.59, -0.58, 0.58),
            (0.42, -0.29, 0.88), (-0.0, 1.0, 0.17), (-0.43, 0.88, 0.29), (-0.61, 0.57, 0.6), (-0.43, 0.26, 0.9),
            (0.0, 0.13, 1.02), (0.43, 0.26, 0.9), (0.61, 0.57, 0.6), (0.43, 0.88, 0.29), (0.85, 0.44, 0.37),
            (0.91, -0.38, 0.42), (0.79, 0.04, 0.65), (0.0, -0.02, 1.02), (0.43, -0.02, 0.89), (-0.43, -0.02, 0.89),
            (-0.91, -0.38, 0.41), (-0.82, 0.04, 0.65), (-0.91, 0.44, 0.37), (0, -1, 1), (0, 1, 1)],
           [(4, 5, 13, 12), (3, 4, 12, 11), (7, 0, 16, 23), (0, 1, 17, 16), (27, 28, 21, 20), (29, 27, 20, 19),
            (25, 13, 5, 6), (6, 7, 23, 24), (22, 26, 24, 23), (14, 13, 25, 26), (24, 26, 25, 6), (9, 8, 27, 29),
            (8, 15, 28, 27), (22, 21, 28, 26), (14, 26, 28, 15), (30, 31, 32, 2), (2, 32, 17, 1), (2, 3, 11, 30),
            (10, 31, 30, 11), (17, 32, 31, 18), (10, 9, 29, 31), (18, 31, 29, 19)],
           [(4, 37), (36, 37), (26, 36), (12, 26), (28, 37), (19, 28), (14, 21)])

Joncts = [S1, S2]

root = Module([], (1, [0, 1, 2, 3, 4, 5, 6, 7]), [Vector((0.0, 0.9928191900253296, 0.9806214570999146)), Vector(
    (-0.7020291090011597, 0.7020291090011597, 0.9806214570999146)), Vector(
    (-0.9928191900253296, -4.3397506033215905e-08, 0.9806214570999146)), Vector(
    (-0.7020291090011597, -0.7020291090011597, 0.9806214570999146)), Vector(
    (8.679501206643181e-08, -0.9928191900253296, 0.9806214570999146)), Vector(
    (0.7020292282104492, -0.7020290493965149, 0.9806214570999146)), Vector(
    (0.9928191900253296, 1.1839250468881346e-08, 0.9806214570999146)), Vector(
    (0.7020292282104492, 0.7020291090011597, 0.9806214570999146)),
                                                    Vector((0.0, 1.0136922597885132, 0.45493215322494507)), Vector(
        (-0.716788649559021, 0.716788649559021, 0.45493215322494507)), Vector(
        (-1.0136922597885132, -4.4309896196637055e-08, 0.45493215322494507)), Vector(
        (-0.716788649559021, -0.716788649559021, 0.45493215322494507)), Vector(
        (8.861979239327411e-08, -1.0136922597885132, 0.45493215322494507)), Vector(
        (0.7167887687683105, -0.7167885303497314, 0.45493215322494507)), Vector(
        (1.0136922597885132, 1.2088158918288627e-08, 0.45493215322494507)), Vector(
        (0.7167887687683105, 0.7167885899543762, 0.45493215322494507)),
                                                    Vector((0.0, 1.1711314916610718, 0.011928796768188477)), Vector(
        (-0.8281149864196777, 0.8281149864196777, 0.011928796768188477)), Vector(
        (-1.1711314916610718, -5.119178325685425e-08, 0.011928796768188477)), Vector(
        (-0.8281149864196777, -0.8281149864196777, 0.011928796768188477)), Vector(
        (1.023835665137085e-07, -1.1711314916610718, 0.011928796768188477)), Vector(
        (0.8281151056289673, -0.8281148672103882, 0.011928796768188477)), Vector(
        (1.1711314916610718, 1.3965602896348628e-08, 0.011928796768188477)), Vector(
        (0.8281151056289673, 0.828114926815033, 0.011928796768188477)),
                                                    Vector((0.0, 1.416882872581482, -0.3086543381214142)), Vector(
        (-1.0018874406814575, 1.0018874406814575, -0.3086543381214142)), Vector(
        (-1.416882872581482, -6.19339104446226e-08, -0.3086543381214142)), Vector(
        (-1.0018874406814575, -1.0018874406814575, -0.3086543381214142)), Vector(
        (1.238678208892452e-07, -1.416882872581482, -0.3086543381214142)), Vector(
        (1.001887559890747, -1.0018872022628784, -0.3086543381214142)), Vector(
        (1.416882872581482, 1.6896155585754968e-08, -0.3086543381214142)), Vector(
        (1.001887559890747, 1.001887321472168, -0.3086543381214142))],
              [(7, 6, 14, 15), (5, 4, 12, 13), (3, 2, 10, 11), (1, 0, 8, 9), (0, 7, 15, 8), (6, 5, 13, 14),
               (4, 3, 11, 12), (2, 1, 9, 10), (9, 8, 16, 17), (8, 15, 23, 16), (14, 13, 21, 22), (12, 11, 19, 20),
               (10, 9, 17, 18), (15, 14, 22, 23), (13, 12, 20, 21), (11, 10, 18, 19), (16, 23, 31, 24),
               (22, 21, 29, 30), (20, 19, 27, 28), (18, 17, 25, 26), (23, 22, 30, 31), (21, 20, 28, 29),
               (19, 18, 26, 27), (17, 16, 24, 25)])

branch = Module([0, 1, 2, 3, 4, 5, 6, 7], (1, [0, 1, 2, 3, 4, 5, 6, 7]),
                [Vector((0.0, 1.0, 0.0)), Vector((-0.7071067690849304, 0.7071067690849304, 0.0)),
                 Vector((-1.0, -4.371138828673793e-08, 0.0)), Vector((-0.7071067690849304, -0.7071067690849304, 0.0)),
                 Vector((8.742277657347586e-08, -1.0, 0.0)), Vector((0.70710688829422, -0.7071066498756409, 0.0)),
                 Vector((1.0, 1.1924880638503055e-08, 0.0)), Vector((0.70710688829422, 0.7071067094802856, 0.0))], [])

trunk = Split(
    [0, 1, 2, 3, 4, 5, 6, 7],
    ([8, 9, 10, 11, 12, 13, 14, 15], [55, 56, 57, 58, 59, 60, 61, 62]),
    [(0.0, 1.0, -0.0), (-0.71, 0.71, -0.0), (-1.0, -0.0, -0.0), (-0.71, -0.71, -0.0), (0.0, -1.0, -0.0),
     (0.71, -0.71, -0.0), (1.0, 0.0, -0.0), (0.71, 0.71, -0.0), (0.0, 0.98, 1.37), (-0.69, 0.69, 1.37),
     (-0.98, -0.0, 1.37), (-0.75, -0.64, 1.38), (0.0, -0.91, 1.4), (0.75, -0.64, 1.38), (0.98, 0.0, 1.37),
     (0.69, 0.69, 1.37), (0.0, -0.95, 1.39), (-0.51, -0.89, 1.21), (-0.64, -1.01, 0.75), (-0.47, -1.22, 0.35),
     (0.0, -1.34, 0.25), (0.47, -1.22, 0.35), (0.64, -1.01, 0.75), (0.51, -0.89, 1.21), (0.99, -0.04, 0.17),
     (0.99, -0.04, 1.07), (0.7, 0.7, 1.07), (0.7, 0.7, 0.17), (0.0, -1.23, 0.15), (0.0, -0.93, 1.38),
     (0.66, -0.74, 1.28), (0.59, -1.03, 0.18), (-0.99, -0.0, 0.17), (-0.99, -0.0, 1.07), (-0.66, -0.74, 1.28),
     (-0.59, -1.03, 0.18), (0.0, 0.99, 0.17), (0.0, 0.99, 1.07), (-0.7, 0.7, 1.07), (-0.7, 0.7, 0.17),
     (0.96, -0.11, 0.62), (0.7, 0.7, 0.62), (0.72, -0.8, 0.63), (-0.96, -0.11, 0.62), (-0.72, -0.8, 0.63),
     (0.0, 0.99, 0.62), (-0.7, 0.7, 0.62), (0.0, -1.0, 1.43), (-0.43, -1.09, 1.3), (-0.6, -1.38, 0.99),
     (-0.41, -1.66, 0.69), (0.0, -1.78, 0.57), (0.41, -1.66, 0.69), (0.6, -1.38, 0.99), (0.43, -1.09, 1.3),
     (0.0, -1.08, 1.49), (-0.42, -1.23, 1.41), (-0.59, -1.6, 1.22), (-0.42, -1.98, 1.03), (0.0, -2.13, 0.95),
     (0.42, -1.98, 1.03), (0.59, -1.6, 1.22), (0.42, -1.23, 1.41), (0, 0, 1), (0, -.35, .59)],
    [(0.0, 1.0, -0.04), (-0.71, 0.71, -0.04), (-1.0, -0.0, -0.04), (-0.71, -0.71, -0.04), (0.0, -0.98, -0.04),
     (0.71, -0.71, -0.04), (1.0, 0.0, -0.04), (0.71, 0.71, -0.04), (0.0, 0.98, 1.31), (-0.69, 0.69, 1.31),
     (-0.98, -0.0, 1.31), (-0.69, -0.69, 1.31), (0.0, -0.95, 1.31), (0.69, -0.69, 1.31), (0.98, 0.0, 1.31),
     (0.69, 0.69, 1.31), (0.0, -1.02, 1.24), (-0.45, -0.95, 1.07), (-0.59, -0.91, 0.63), (-0.46, -0.96, 0.2),
     (0.0, -1.03, 0.02), (0.46, -0.96, 0.2), (0.59, -0.91, 0.63), (0.45, -0.95, 1.07), (0.99, -0.04, 0.17),
     (0.99, -0.04, 1.07), (0.7, 0.7, 1.07), (0.7, 0.7, 0.17), (0.0, -0.99, -0.01), (0.0, -0.99, 1.25),
     (0.59, -0.85, 1.14), (0.6, -0.85, 0.11), (-0.99, -0.0, 0.17), (-0.99, -0.0, 1.07), (-0.59, -0.85, 1.14),
     (-0.6, -0.85, 0.11), (0.0, 0.99, 0.17), (0.0, 0.99, 1.07), (-0.7, 0.7, 1.07), (-0.7, 0.7, 0.17),
     (0.96, -0.11, 0.62), (0.7, 0.7, 0.62), (0.69, -0.75, 0.62), (-0.96, -0.11, 0.62), (-0.69, -0.75, 0.62),
     (0.0, 0.99, 0.62), (-0.7, 0.7, 0.62), (-0.0, -1.11, 1.19), (-0.39, -1.11, 1.03), (-0.55, -1.11, 0.64),
     (-0.39, -1.11, 0.25), (0.0, -1.1, 0.09), (0.39, -1.11, 0.25), (0.55, -1.11, 0.64), (0.39, -1.11, 1.03),
     (0.0, -1.27, 1.18), (-0.38, -1.27, 1.02), (-0.54, -1.26, 0.65), (-0.38, -1.25, 0.27), (0.0, -1.25, 0.11),
     (0.38, -1.25, 0.27), (0.54, -1.26, 0.65), (0.38, -1.27, 1.02), (0, 0, 1), (0, -1, 0)],
    [(26, 15, 14, 25), (30, 13, 12, 29), (34, 11, 10, 33), (38, 9, 8, 37), (37, 8, 15, 26), (25, 14, 13, 30),
     (29, 12, 11, 34), (33, 10, 9, 38), (2, 32, 39, 1), (43, 33, 38, 46), (4, 28, 35, 3), (6, 24, 31, 5),
     (40, 25, 30, 42), (0, 36, 27, 7), (45, 37, 26, 41), (1, 39, 36, 0), (46, 38, 37, 45), (3, 35, 32, 2),
     (44, 34, 33, 43), (5, 31, 28, 4), (7, 27, 24, 6), (41, 26, 25, 40), (27, 41, 40, 24), (35, 44, 43, 32),
     (39, 46, 45, 36), (36, 45, 41, 27), (24, 40, 42, 31), (32, 43, 46, 39), (17, 34, 44, 18), (18, 44, 35, 19),
     (19, 35, 28, 20), (20, 28, 31, 21), (21, 31, 42, 22), (22, 42, 30, 23), (23, 30, 29, 16), (16, 29, 34, 17),
     (16, 47, 54, 23), (23, 54, 53, 22), (22, 53, 52, 21), (21, 52, 51, 20), (20, 51, 50, 19), (19, 50, 49, 18),
     (18, 49, 48, 17), (17, 48, 47, 16), (53, 54, 62, 61), (51, 52, 60, 59), (49, 50, 58, 57), (47, 48, 56, 55),
     (54, 47, 55, 62), (52, 53, 61, 60), (50, 51, 59, 58), (48, 49, 57, 56)],
    [(29, 12), (4, 28), (28, 20), (29, 16), (16, 47), (51, 20), (59, 51), (55, 47)])


class Trunk:
    def __init__(self, roots, stem, verts, faces, Seams):
        self.roots = roots
        self.stem = stem
        self.verts = verts
        self.faces = faces
        self.Seams = Seams


R1 = Trunk(
    [(Vector((-6.293336696217011e-08, -0.6988458633422852, -0.3152722477912903)), .69,
      [110, 111, 112, 113, 114, 115, 116, 117]),
     (Vector((0.6009913086891174, -0.04263520613312721, -0.3981175780296326)), .34, [55, 56, 57, 58, 59, 60, 61, 62]),
     (Vector((0.5693859457969666, 0.49961066246032715, -0.352831494808197)), .34, [47, 48, 49, 50, 51, 52, 53, 54]), (
         Vector((-0.779069721698761, 0.455067813396454, -0.24110554456710815)), .34,
         [63, 64, 65, 66, 67, 68, 69, 70, 101]),
     (Vector((-0.7720233201980591, -0.09697314351797104, -0.3281529068946838)), .56, [71, 72, 73, 74, 75, 76, 77, 78]),
     (
         Vector((-1.859164768802657e-07, 0.2071729600429535, -0.4783042669296265)), .60,
         [39, 40, 41, 42, 43, 44, 45, 46])],
    [0, 1, 2, 3, 4, 5, 6, 7],
    [(0.0, 0.99, 0.98), (-0.7, 0.7, 0.98), (-0.99, -0.0, 0.98), (-0.7, -0.7, 0.98), (0.0, -0.99, 0.98),
     (0.7, -0.7, 0.98), (0.99, 0.0, 0.98), (0.7, 0.7, 0.98), (0.01, 1.07, 0.58), (-0.74, 0.76, 0.57),
     (-1.06, 0.0, 0.58), (-0.75, -0.75, 0.58), (0.01, -1.07, 0.58), (0.76, -0.75, 0.58), (1.08, 0.0, 0.58),
     (0.76, 0.76, 0.58), (0.01, 1.23, 0.08), (-0.82, 0.88, 0.09), (-1.21, 0.01, 0.08), (-0.86, -0.86, 0.09),
     (0.01, -1.22, 0.09), (0.88, -0.86, 0.09), (1.23, 0.0, 0.09), (0.88, 0.87, 0.09), (0.1, 1.47, -0.3),
     (-0.87, 1.07, -0.26), (-1.43, 0.05, -0.28), (-1.05, -1.0, -0.29), (0.01, -1.58, -0.29), (1.01, -1.04, -0.3),
     (1.44, -0.02, -0.34), (1.02, 1.06, -0.29), (0.01, -0.62, -1.31), (-0.5, -0.77, -1.17), (-0.7, -1.14, -0.84),
     (-0.5, -1.52, -0.5), (0.51, -1.52, -0.5), (0.72, -1.14, -0.84), (0.51, -0.77, -1.17), (0.01, 0.98, -1.09),
     (-0.41, 0.81, -1.12), (-0.58, 0.41, -1.21), (-0.41, 0.01, -1.29), (0.01, -0.16, -1.33), (0.42, 0.01, -1.29),
     (0.59, 0.41, -1.21), (0.42, 0.81, -1.12), (0.73, 1.52, -0.51), (0.51, 1.5, -0.72), (0.43, 1.3, -0.94),
     (0.55, 1.03, -1.04), (0.79, 0.86, -0.96), (1.01, 0.88, -0.75), (1.09, 1.08, -0.53), (0.97, 1.35, -0.43),
     (1.12, 0.28, -0.89), (0.9, 0.21, -1.05), (0.78, -0.03, -1.13), (0.83, -0.3, -1.08), (1.02, -0.44, -0.93),
     (1.24, -0.37, -0.77), (1.36, -0.13, -0.69), (1.31, 0.14, -0.74), (-1.49, 0.49, -0.65), (-1.41, 0.74, -0.54),
     (-1.25, 0.95, -0.62), (-1.09, 1.0, -0.84), (-1.03, 0.86, -1.08), (-1.11, 0.62, -1.19), (-1.27, 0.41, -1.11),
     (-1.43, 0.36, -0.88), (-1.36, -0.85, -0.84), (-1.55, -0.51, -0.66), (-1.55, -0.1, -0.73), (-1.35, 0.16, -1.01),
     (-1.08, 0.11, -1.33), (-0.89, -0.23, -1.51), (-0.9, -0.65, -1.44), (-1.09, -0.91, -1.16), (0.06, 1.52, -0.6),
     (0.03, 1.37, -0.82), (1.22, 0.55, -0.74), (1.42, 0.42, -0.55), (1.0, 0.57, -0.9), (-0.8, 0.67, -1.11),
     (-0.7, 0.94, -0.97), (-0.31, 1.18, -0.88), (-0.42, 1.31, -0.58), (-0.78, 1.14, -0.65), (-1.07, 1.01, -0.44),
     (1.27, -0.5, -0.55), (1.08, -0.92, -0.53), (0.94, -0.96, -0.67), (0.83, -1.26, -0.5), (-0.97, -1.23, -0.5),
     (-1.09, -1.06, -0.66), (-1.36, -0.73, -0.48), (-1.56, -0.12, -0.5), (-1.51, 0.28, -0.56), (-1.39, 0.53, -0.45),
     (-1.51, 0.19, -0.75), (-1.46, 0.42, -0.77), (-0.91, -0.98, -1.01), (-0.72, -0.67, -1.28), (-0.68, -0.14, -1.37),
     (-0.84, 0.26, -1.27), (-1.21, -0.94, -0.76), (-1.45, -0.6, -0.59), (-1.56, -0.12, -0.62), (-1.52, 0.22, -0.66),
     (0.03, -0.95, -1.39), (-0.37, -1.06, -1.27), (-0.54, -1.33, -0.97), (-0.37, -1.6, -0.67), (0.03, -1.71, -0.55),
     (0.43, -1.6, -0.67), (0.6, -1.33, -0.97), (0.43, -1.06, -1.27)],
    [(7, 6, 14, 15), (5, 4, 12, 13), (3, 2, 10, 11), (1, 0, 8, 9), (0, 7, 15, 8), (6, 5, 13, 14), (4, 3, 11, 12),
     (2, 1, 9, 10), (9, 8, 16, 17), (8, 15, 23, 16), (14, 13, 21, 22), (12, 11, 19, 20), (10, 9, 17, 18),
     (15, 14, 22, 23), (13, 12, 20, 21), (11, 10, 18, 19), (16, 23, 31, 24), (22, 21, 29, 30), (20, 19, 27, 28),
     (18, 17, 25, 26), (23, 22, 30, 31), (21, 20, 28, 29), (19, 18, 26, 27), (17, 16, 24, 25), (32, 43, 44, 38),
     (33, 42, 43, 32), (103, 102, 78, 77), (104, 42, 33, 103), (105, 104, 76, 75), (45, 56, 57, 44), (57, 58, 38, 44),
     (46, 50, 51, 45), (49, 50, 46, 39), (31, 54, 47, 24), (48, 49, 80, 79), (48, 79, 24, 47), (62, 55, 81, 82),
     (53, 82, 81, 52), (61, 62, 82, 30), (38, 58, 59, 37), (56, 45, 51, 83), (81, 55, 56, 83), (53, 54, 31),
     (52, 81, 83, 51), (30, 82, 53, 31), (40, 41, 84, 85), (85, 84, 68, 67), (86, 80, 49, 39), (39, 40, 85, 86),
     (79, 80, 86, 87), (25, 24, 79, 87), (66, 88, 85, 67), (85, 88, 87, 86), (89, 25, 87, 88), (65, 89, 88, 66),
     (60, 61, 30, 90), (29, 91, 90, 30), (92, 60, 90, 91), (60, 92, 37, 59), (36, 37, 92, 93), (29, 93, 92, 91),
     (29, 28, 36, 93), (27, 94, 35, 28), (106, 71, 78, 102), (34, 35, 94, 95), (107, 72, 71, 106), (96, 95, 94, 27),
     (26, 97, 96, 27), (108, 107, 96, 97), (70, 69, 75, 74), (73, 100, 70, 74), (97, 26, 99, 98), (98, 99, 64, 63),
     (26, 25, 89, 99), (64, 99, 89, 65), (109, 108, 97, 98), (101, 109, 98, 63), (70, 100, 109, 101),
     (100, 73, 108, 109), (73, 72, 107, 108), (96, 107, 106, 95), (95, 106, 102, 34), (41, 42, 104, 105),
     (76, 104, 103, 77), (33, 34, 102, 103), (68, 105, 75, 69), (41, 105, 68, 84), (36, 115, 116, 37),
     (114, 115, 36, 28), (35, 113, 114, 28), (34, 112, 113, 35), (111, 112, 34, 33), (32, 110, 111, 33),
     (38, 117, 110, 32), (37, 116, 117, 38)],
    [(0, 8), (8, 16), (24, 16), (80, 79), (24, 79), (39, 86), (80, 86), (40, 39), (41, 40), (42, 41), (43, 42),
     (44, 43), (45, 44), (46, 45), (39, 46), (48, 47), (49, 48), (50, 49), (51, 50), (52, 51), (53, 52), (54, 53),
     (47, 54), (56, 55), (57, 56), (58, 57), (59, 58), (60, 59), (61, 60), (62, 61), (55, 62), (64, 63), (65, 64),
     (66, 65), (67, 66), (68, 67), (69, 68), (70, 69), (101, 70), (72, 71), (73, 72), (74, 73), (75, 74), (76, 75),
     (77, 76), (78, 77), (71, 78), (63, 101), (111, 110), (112, 111), (113, 112), (114, 113), (115, 114), (116, 115),
     (117, 116), (110, 117)])

# Material node_tree
Nodes, Links = (
    [('NodeReroute', Vector((-580.0, 460.0)), 'Reroute', ''), ('NodeReroute', Vector((20.0, -20.0)), 'Reroute.001', ''),
     ('ShaderNodeInvert', Vector((540.0, 300.0)), 'Invert', ''),
     ('NodeReroute', Vector((620.0, -20.0)), 'Reroute.002', ''),
     ('NodeReroute', Vector((-60.0, 140.0)), 'Reroute.003', ''),
     ('ShaderNodeOutputMaterial', Vector((1240.0, 440.0)), 'Material Output', ''),
     ('ShaderNodeTexImage', Vector((-220.0, 440.0)), 'Bark texture', 'Bark texture'),
     ('ShaderNodeMapping', Vector((-560.0, 440.0)), 'Mapping', ''),
     ('ShaderNodeSeparateXYZ', Vector((-560.0, 140.0)), 'Separate XYZ', ''),
     ('ShaderNodeMixRGB', Vector((-380.0, 140.0)), 'Mix', ''),
     ('ShaderNodeMixRGB', Vector((-40.0, 300.0)), 'Mix.002', ''),
     ('ShaderNodeValToRGB', Vector((280.0, 300.0)), 'moss height', 'moss height'),
     ('ShaderNodeTexNoise', Vector((540.0, 540.0)), 'Noise Texture.001', ''),
     ('ShaderNodeTexNoise', Vector((-560.0, 0.0)), 'Noise Texture', ''),
     ('ShaderNodeMath', Vector((120.0, 300.0)), 'Math.001', ''),
     ('ShaderNodeMixRGB', Vector((700.0, 300.0)), 'moss color', 'moss color'),
     ('ShaderNodeMixRGB', Vector((900.0, 440.0)), 'color variation', 'color variation'),
     ('ShaderNodeTexCoord', Vector((-940.0, 200.0)), 'Texture Coordinate', ''),
     ('ShaderNodeVectorMath', Vector((-740.0, 0.0)), 'Vector Math', ''),
     ('ShaderNodeBrightContrast', Vector((720.0, 540.0)), 'Bright/Contrast', ''),
     ('ShaderNodeBsdfDiffuse', Vector((1060.0, 440.0)), 'Diffuse BSDF', ''),
     ('ShaderNodeObjectInfo', Vector((-940.0, -140.0)), 'Object Info', '')],
    [([17, 'Generated'], [8, 'Vector']), ([8, 'Z'], [9, 'Color1']), ([13, 'Fac'], [9, 'Color2']),
     ([11, 'Color'], [2, 'Color']), ([2, 'Color'], [15, 'Fac']), ([3, 'Output'], [15, 'Color1']),
     ([14, 'Value'], [11, 'Fac']), ([9, 'Color'], [10, 'Color1']), ([10, 'Color'], [14, 'Value']),
     ([4, 'Output'], [10, 'Color2']), ([0, 'Output'], [12, 'Vector']), ([16, 'Color'], [20, 'Color']),
     ([15, 'Color'], [16, 'Color1']), ([12, 'Fac'], [19, 'Color']), ([19, 'Color'], [16, 'Fac']),
     ([4, 'Output'], [1, 'Input']), ([1, 'Output'], [3, 'Input']), ([6, 'Color'], [4, 'Input']),
     ([17, 'UV'], [7, 'Vector']), ([7, 'Vector'], [6, 'Vector']), ([17, 'Object'], [18, 'Vector']),
     ([18, 'Vector'], [13, 'Vector']), ([18, 'Vector'], [0, 'Input']), ([20, 'BSDF'], [5, 'Surface']),
     ([21, 'Location'], [18, 'Vector'])])


# This part is heavilly inspired by the "UV Align\Distribute" addon made by Rebellion (Luca Carella)
def initbmesh():
    global bm
    global uvlayer
    bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
    uvlayer = bm.loops.layers.uv.active


def b_box_center(island):
    min_x = +1000
    min_y = +1000
    max_x = -1000
    max_y = -1000

    # for island in islands:
    for face_id in island:
        face = bm.faces[face_id]
        for loop in face.loops:
            min_x = min(loop[uvlayer].uv.x, min_x)
            min_y = min(loop[uvlayer].uv.y, min_y)
            max_x = max(loop[uvlayer].uv.x, max_x)
            max_y = max(loop[uvlayer].uv.y, max_y)

    return (Vector((min_x, min_y)) + Vector((max_x, max_y))) / 2


def rotate_island(island, angle):
    rad = radians(angle)
    center = b_box_center(island)
    for face_id in island:
        face = bm.faces[face_id]
        for loop in face.loops:
            x = loop[bm.loops.layers.uv.active].uv.x
            y = loop[bm.loops.layers.uv.active].uv.y
            xt = x - center.x
            yt = y - center.y
            xr = (xt * cos(rad)) - (yt * sin(rad))
            yr = (xt * sin(rad)) + (yt * cos(rad))
            loop[bm.loops.layers.uv.active].uv.x = xr + center.x
            loop[bm.loops.layers.uv.active].uv.y = yr + center.y


class MakeIslands:
    def __init__(self):
        initbmesh()
        global bm
        global uvlayer
        self.face_to_verts = defaultdict(set)
        self.vert_to_faces = defaultdict(set)
        self.selectedIsland = set()
        for face in bm.faces:
            for loop in face.loops:
                ind = '{0[0]:.5} {0[1]:.5} {1}'.format(loop[uvlayer].uv, loop.vert.index)
                self.face_to_verts[face.index].add(ind)
                self.vert_to_faces[ind].add(face.index)
                if face.select:
                    if loop[uvlayer].select:
                        self.selectedIsland.add(face.index)

    def add_to_island(self, face_id):
        if face_id in self.faces_left:
            # add the face itself
            self.current_island.append(face_id)
            self.faces_left.remove(face_id)

            # and add all faces that share uvs with this face
            verts = self.face_to_verts[face_id]
            for vert in verts:
                connected_faces = self.vert_to_faces[vert]
                if connected_faces:
                    for face in connected_faces:
                        self.add_to_island(face)

    def get_islands(self):
        self.islands = []  # instance attribute defined outside of __init__!
        self.faces_left = set(self.face_to_verts.keys())  # instance attribute defined outside of __init__!
        while len(self.faces_left) > 0:
            face_id = list(self.faces_left)[0]
            self.current_island = []  # instance attribute defined outside of __init__!
            self.add_to_island(face_id)
            self.islands.append(self.current_island)
        return self.islands

    def active_island(self):
        for island in self.islands:
            try:
                if bm.faces.active.index in island:
                    return island
            except:  # broad try-except...what are you trying to catch here?
                return None

    def selected_islands(self):
        _selectedIslands = []
        for island in self.islands:
            if not self.selectedIsland.isdisjoint(island):
                _selectedIslands.append(island)
        return _selectedIslands


def create_system(ob, number, display, vertex_group):
    # get the vertex group
    g = vertex_group

    # customize the particle system
    leaf = ob.modifiers.new("psys name", 'PARTICLE_SYSTEM')
    part = ob.particle_systems[0]
    part.vertex_group_density = g.name
    set = leaf.particle_system.settings
    set.name = "leaf"
    set.type = "HAIR"
    set.use_advanced_hair = True
    set.draw_percentage = 100 * display / number
    set.count = number
    set.distribution = "RAND"
    set.normal_factor = .250
    set.factor_random = .7
    set.use_rotations = True
    set.phase_factor = 1
    set.phase_factor_random = 1
    set.particle_size = .015
    set.size_random = .25
    set.brownian_factor = 1
    set.render_type = "OBJECT"


def rotate():
    bpy.ops.object.editmode_toggle()
    make_islands = MakeIslands()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    islands = make_islands.get_islands()  # islands is not used...does get_islands need to return anything?
    sel_islands = make_islands.selected_islands()
    act_island = make_islands.active_island()

    if not act_island:
        self.report({"ERROR"}, "No active face")  # self is not defined, will raise an error!
        return {"CANCELLED"}

    for island in sel_islands:

        f0 = bm.faces[island[0]]
        index = f0.index
        f1 = bm.faces[island[0]]
        for i in range(len(island)):
            f1 = bm.faces[island[i]]
            if f1.index == index + 1:
                break

        x1, y1, x2, y2 = (0, 0, 0, 0)
        for i in range(4):
            x1 += .25 * f0.loops[i][bm.loops.layers.uv.active].uv.x
            x2 += .25 * f1.loops[i][bm.loops.layers.uv.active].uv.x
            y1 += .25 * f0.loops[i][bm.loops.layers.uv.active].uv.y
            y2 += .25 * f1.loops[i][bm.loops.layers.uv.active].uv.y

        if (abs(x2 - x1) < abs(y2 - y1)) and (len(island) % 8 == 0):
            rotate_island(island, 90)

    bpy.ops.uv.pack_islands(rotate=False, margin=0.001)
    bpy.ops.object.editmode_toggle()


# ....................................................................................................................................


def add_tuple(t, x):
    return tuple([x + i for i in t])


def rot_scale(v_co, scale, directions, rot_z):
    (x, y, z) = directions
    directions = Vector((-x, -y, z))
    c = rot_z
    q = Vector((0, 0, 1)).rotation_difference(directions)
    mat_rot = q.to_matrix()
    mat_rot.resize_4x4()
    mc = Matrix.Rotation(c, 4, 'Z')
    v_co = [((v * scale) * mc) * mat_rot for v in v_co]
    return v_co


def joindre(verts, faces, v1_i, v2_i):
    v1 = verts[v1_i[0]]
    n = len(v2_i)
    d = float('inf')
    decalage = 0
    for i in range(n):
        d1 = (verts[v2_i[i]] - v1).length
        if d1 < d:
            d = d1
            decalage = i
    v2 = verts[v1_i[1]]
    k = 1
    if (verts[v2_i[(decalage + 1) % n]] - v2).length > (verts[v2_i[(decalage - 1) % n]] - v2).length:
        k = -1
    for i in range(n):
        faces.append([v1_i[i], v2_i[(decalage + i * k) % n], v2_i[(decalage + (i + 1) * k) % n], v1_i[(i + 1) % n]])


def join(verts, faces, indexes, object_verts, object_faces, scale, i1, i2, entree, directions, branch_length, s_index, seams,
         jonc_seams, random_angle, branch_rotation):
    random1 = random_angle * (random() - .5)
    random2 = random_angle * (random() - .5)
    random3 = random_angle * (random() - .5)

    rand_x = Matrix.Rotation(random1, 4, 'X')
    rand_y = Matrix.Rotation(random2, 4, 'Y')
    rand_z = Matrix.Rotation(random3, 4, 'Z')

    directions = (((directions * rand_x) * rand_y) * rand_z)
    barycentre = Vector((0, 0, 0))
    for i in indexes:
        barycentre += verts[i]
    barycentre /= len(indexes)

    directions.normalize()
    barycentre += directions * branch_length
    r1 = (object_verts[i1[0]] - object_verts[i1[4]]).length / 2
    r2 = (object_verts[i2[0]] - object_verts[i2[4]]).length / 2
    v = rot_scale(object_verts, scale, directions, radians(branch_rotation))
    d2 = v[-1]
    d1 = v[-2]

    n = len(verts)
    nentree = [n + i for i in entree]
    add_seams(nentree, seams)
    seams += [add_tuple(f, n) for f in jonc_seams]
    faces += [add_tuple(f, n) for f in object_faces]
    verts += [barycentre + i for i in v]
    joindre(verts, faces, indexes, nentree)

    i1 = [n + i for i in i1]
    i2 = [n + i for i in i2]
    add_seams(i1, seams)
    add_seams(i2, seams)

    dist = 1000
    ns_index = 0
    for i in nentree:
        length = (verts[s_index] - verts[i]).length
        if length < dist:
            dist = length
            ns_index = i
    seams.append((s_index, ns_index))
    return i1, i2, d1, d2, r1, r2, i1[0], i2[0]


def join_branch(verts, faces, indexes, scale, branch_length, branch_verts, direction, rand, s_index, Seams):
    barycentre = Vector((0, 0, 0))
    random1 = rand * (random() - .5)
    random2 = rand * (random() - .5)
    random3 = rand * (random() - .5)
    for i in indexes:
        barycentre += verts[i]
    barycentre /= len(indexes)

    direction.normalized()
    rand_x = Matrix.Rotation(random1, 4, 'X')
    rand_y = Matrix.Rotation(random2, 4, 'Y')
    rand_z = Matrix.Rotation(random3, 4, 'Z')

    direction = (((direction * rand_x) * rand_y) * rand_z)
    barycentre += direction * branch_length
    n = len(verts)
    v = rot_scale(branch_verts, scale, direction, ((random() + 27) / 28) * randint(0, 8) / 8 * 2 * pi)
    nentree = [n + i for i in range(8)]
    verts += [ve + barycentre for ve in v]
    joindre(verts, faces, indexes, nentree)

    ns_index = 0
    dist = 1000
    for i in nentree:
        length = (verts[s_index] - verts[i]).length
        if length < dist:
            dist = length
            ns_index = i
    Seams.append((s_index, ns_index))

    return nentree, direction, ns_index


def gravity(dir, gravity_strength):
    v = Vector((0, 0, -1))
    norm = dir.length
    factor = (dir.cross(v)).length / norm / 100 * gravity_strength
    return dir + v * factor


def add_seams(indexes, seams):
    n = len(indexes)
    for i in range(n):
        seams.append((indexes[i], indexes[(i + 1) % n]))


def create_tree(position):
    for select_ob in bpy.context.selected_objects:
        select_ob.select = False
    scene = bpy.context.scene

    make_roots = scene.create_roots
    trunk2 = scene.preserve_trunk
    radius = scene.radius
    bones = []
    leafs_start_index = 0
    big_j = S1
    seams2 = [s for s in R1.Seams]
    entree = [i for i in big_j.entree]

    last_bone = (1, Vector((0, 0, 1)))

    if not make_roots:
        verts = [Vector(v) * radius for v in root.verts]
        faces = [f for f in root.faces]
        extr = [i for i in root.sortie[1]]
    else:
        verts = [Vector(v) * radius for v in R1.verts]
        faces = [f for f in R1.faces]
        extr = [i for i in R1.stem]
        roots = [(i[2], i[1], i[0], i[2][0]) for i in R1.roots]
        roots_variations = .5
        roots_length = 1.4
        roots_rad_dec = .7

        for i in range(scene.roots_iteration):
            next_roots = []
            for E in roots:
                indexes, radius, direction, s_index = E

                big_j = Joncts[1]
                i1 = [i for i in big_j.sortie[0]]
                i2 = [i for i in big_j.sortie[1]]
                jonct_seams = [s for s in big_j.Seams]
                inter_fact = (i / (1.4 * max(1, i))) ** 3 * random()
                jonct_verts = interpolate(big_j.verts1, big_j.verts2, inter_fact)
                barycentre = Vector((0, 0, 0))

                for k in indexes:
                    barycentre += verts[k]
                barycentre /= len(indexes)

                if i > 2:
                    direction += .7 * Vector((0, 0, -1)) / (max(1, 20 * abs(barycentre.z)))
                ni1, ni2, dir1, dir2, r1, r2, nsi1, nsi2 = join(verts, faces, indexes, jonct_verts, big_j.faces,
                                                                radius * roots_rad_dec, i1, i2, entree, direction,
                                                                roots_length, s_index, seams2, jonct_seams,
                                                                roots_variations,
                                                                ((random() + 27) / 28) * randint(0, 8) / 8 * 2 * pi)
                dir1 = gravity(dir1, -2)
                dir2 = gravity(dir2, -2)
                next_roots.append((ni1, radius * roots_rad_dec * r1, dir1, nsi1))
                next_roots.append((ni2, radius * roots_rad_dec * r2, dir2, nsi2))
            roots = next_roots

    radius = scene.radius
    extremites = [(extr, radius, Vector((0, 0, 1)), extr[0], last_bone, trunk2, 0)]

    for i in range(scene.iteration + scene.trunk_length):
        if i == scene.iteration + scene.trunk_length - scene.leafs_iteration_length:
            leafs_start_index = len(verts)

        nextremites = []

        for E in extremites:
            indexes, radius, direction, s_index, Lb, trunk2, curr_rotation = E
            new_rotation = (curr_rotation + scene.branch_rotate + 2 * (1 - random()) * scene.branch_random_rotate) % 360

            if i > scene.preserve_end:
                trunk2 = False
            pos = Vector((0, 0, 0))

            for k in indexes:
                pos += verts[k]
            pos /= len(indexes)
            direction.normalize()
            end = pos + direction * 10

            if bpy.data.objects.get(scene.obstacle) is not None:
                obs = scene.objects[scene.obstacle]
                bpy.context.scene.update()

                result, hit_pos, face_normal, face_index = obs.ray_cast(pos, end)
                if result:
                    force = abs(min(direction.dot(face_normal), 0)) * scene.obstacle_strength / (
                        (hit_pos - pos).length + 1) * 2
                    direction += face_normal * force

            split_probability = scene.trunk_split_proba if trunk2 else scene.split_proba

            if i <= scene.trunk_length:
                branch_verts = [v for v in branch.verts]
                ni, direction, nsi = join_branch(verts, faces, indexes, radius, scene.trunk_space, branch_verts,
                                                 direction,
                                                 scene.trunk_variation, s_index, seams2)
                sortie = pos + direction * scene.branch_length

                if i <= scene.bones_iterations:
                    bones.append((Lb[0], len(bones) + 2, Lb[1], sortie))

                nb = (len(bones) + 1, sortie)
                nextremites.append((ni, radius * .98, direction, nsi, nb, trunk2, curr_rotation))

            elif i == scene.iteration + scene.trunk_length - 1 or random() < scene.break_chance:
                end_verts = [Vector(v) for v in end_cap.verts]
                end_faces = [f for f in end_cap.faces]
                n = len(verts)
                # ni, direction, and nsi are not used...does join_branch need to return anything?
                ni, direction, nsi = join_branch(verts, faces, indexes, radius, scene.trunk_space, end_verts, direction,
                                                 scene.trunk_variation,
                                                 s_index, seams2)
                faces += [add_tuple(f, n) for f in end_faces]
                end_seams = [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4), (6, 5), (7, 6), (0, 7)]
                seams2 += [add_tuple(f, n) for f in end_seams]

            elif i < scene.iteration + scene.trunk_length - 1 and i == scene.trunk_length + 1 or random() < split_probability:
                variation = scene.trunk_variation if trunk2 else scene.randomangle
                rand_j = 1
                big_j = Joncts[rand_j] if (not trunk2) else trunk
                i1 = [i for i in big_j.sortie[0]]
                i2 = [i for i in big_j.sortie[1]]
                jonct_seams = [s for s in big_j.Seams]

                inter_fact = scene.trunk_split_angle if trunk2 else scene.split_angle
                jonct_verts = interpolate(big_j.verts1, big_j.verts2, inter_fact)
                length = scene.trunk_space if trunk2 else scene.branch_length
                ni1, ni2, dir1, dir2, r1, r2, nsi1, nsi2 = join(verts, faces, indexes, jonct_verts, big_j.faces,
                                                                radius * (1 + scene.radius_dec) / 2, i1, i2, entree,
                                                                direction,
                                                                length, s_index, seams2, jonct_seams, variation,
                                                                new_rotation)
                sortie1 = (verts[ni1[0]] + verts[ni1[4]]) / 2
                sortie2 = (verts[ni2[0]] + verts[ni2[4]]) / 2
                nb = len(bones)

                if i <= scene.bones_iterations:
                    bones.append((Lb[0], nb + 2, Lb[1], sortie1))
                    bones.append((Lb[0], nb + 3, Lb[1], sortie2))

                nb1 = (nb + 2, sortie1)
                nb2 = (nb + 3, sortie2)
                if scene.gravity_start <= i <= scene.gravity_end:
                    dir1 = gravity(dir1, scene.gravity_strength)
                    dir2 = gravity(dir2, scene.gravity_strength)

                nextremites.append((ni1, radius * scene.radius_dec * r1, dir1, nsi1, nb1, trunk2, new_rotation))
                nextremites.append((ni2, radius * scene.radius_dec * r2, dir2, nsi2, nb2, False, new_rotation))

            else:
                branch_verts = [v for v in branch.verts]
                variation = scene.trunk_variation if trunk2 else scene.randomangle
                length = scene.trunk_space if trunk2 else scene.branch_length
                ni, direction, nsi = join_branch(verts, faces, indexes, radius, length, branch_verts, direction,
                                                 variation, s_index,
                                                 seams2)
                sortie = pos + direction * scene.branch_length

                if i <= scene.bones_iterations:
                    bones.append((Lb[0], len(bones) + 2, Lb[1], sortie))

                nb = (len(bones) + 1, sortie)
                if scene.gravity_start <= i <= scene.gravity_end:
                    direction = gravity(direction, scene.gravity_strength)
                nextremites.append((ni, radius * scene.radius_dec, direction, nsi, nb, trunk2, curr_rotation))

        extremites = nextremites

    mesh = bpy.data.meshes.new("tree")

    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=False)
    obj = bpy.data.objects.new("tree", mesh)
    obj.location = position
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    obj.select = True
    bpy.ops.object.shade_smooth()
    obj.select = False
    g = obj.vertex_groups.new("leaf")
    vgroups = obj.vertex_groups
    vgroups.active_index = vgroups["leaf"].index
    g.add([i for i in range(leafs_start_index, len(verts))], 1.0, "ADD")
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.object.editmode_toggle()

    if obj.data.polygons[0].normal.x < 0:
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.editmode_toggle()

    if scene.particle:
        create_system(obj, scene.number, scene.display, vgroups["leaf"])

    if scene.uv:
        test = [[False, []] for i in range(len(verts))]
        for (a, b) in seams2:
            a, b = min(a, b), max(a, b)
            test[a][0] = True
            test[b][0] = True
            test[a][1].append(b)
            test[b][1].append(a)

        for edge in mesh.edges:
            v0, v1 = edge.vertices[0], edge.vertices[1]
            if test[v0][0] and v1 in test[v0][1]:
                edge.select = True

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
        bpy.ops.object.editmode_toggle()
        rotate()

    if scene.mat:
        if not bpy.context.scene.render.engine == 'CYCLES':
            bpy.context.scene.render.engine = 'CYCLES'

        mat = bpy.data.materials.new(name="Tree")
        mat.diffuse_color = (0.214035, 0.0490235, 0.0163952)
        mat.specular_color = (0.0469617, 0.0469617, 0.0469617)
        mat.specular_hardness = 10
        mat.use_nodes = True
        mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Diffuse BSDF'))
        mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Material Output'))

        for (n_type, loc, name, label) in Nodes:
            new_node = mat.node_tree.nodes.new(n_type)
            new_node.location = loc
            new_node.name = name
            new_node.label = label

        nodes = mat.node_tree.nodes
        nodes['Mapping'].scale = (15, 15, 15)
        nodes["Noise Texture"].inputs[1].default_value = 2
        nodes["Noise Texture"].inputs[2].default_value = 10
        nodes["Mix"].blend_type = 'MULTIPLY'
        nodes["Mix.002"].blend_type = 'MULTIPLY'
        nodes["Mix.002"].inputs[0].default_value = .95
        nodes["Math.001"].operation = 'MULTIPLY'
        nodes["Math.001"].inputs[1].default_value = 30
        nodes["moss height"].color_ramp.elements[0].position = .3
        nodes["moss height"].color_ramp.elements[1].position = .5
        nodes["Noise Texture.001"].inputs[1].default_value = .7
        nodes["Noise Texture.001"].inputs[2].default_value = 10
        nodes["Bright/Contrast"].inputs[2].default_value = 5
        nodes["moss color"].blend_type = 'MULTIPLY'
        nodes["moss color"].inputs[2].default_value = [0.342, 0.526, 0.353, 1.0]
        nodes["color variation"].blend_type = 'OVERLAY'
        nodes["color variation"].inputs[2].default_value = [0.610, 0.648, 0.462, 1.0]

        mat.node_tree.links.new(nodes["Texture Coordinate"].outputs[3], nodes["Vector Math"].inputs[1])
        links = mat.node_tree.links
        for (f, t) in Links:
            from_node = mat.node_tree.nodes[f[0]]
            to_node = mat.node_tree.nodes[t[0]]
            links.new(from_node.outputs[f[1]], to_node.inputs[t[1]])
        obj.active_material = mat

    elif bpy.data.materials.get(scene.bark_material) is not None:
        obj.active_material = bpy.data.materials.get(scene.bark_material)

    if scene.create_armature:
        bpy.ops.object.add(
            type='ARMATURE',
            enter_editmode=True,
            location=Vector((0, 0, 0)))
        arm = bpy.context.object
        arm.show_x_ray = True
        amt = arm.data
        arm.data.draw_type = 'STICK'
        bone = amt.edit_bones.new('1')
        bone.head = Vector((0, 0, 0))
        bone.tail = Vector((0, 0, 1))

        for (pname, name, h, t) in bones:
            bone = amt.edit_bones.new(str(name))
            bone.parent = arm.data.edit_bones[str(pname)]
            bone.use_connect = True
            bone.head = h
            bone.tail = t

        bpy.ops.object.editmode_toggle()
        bpy.ops.object.select_all(action='DESELECT')
        obj.select = True
        arm.select = True
        bpy.context.scene.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        bpy.ops.object.select_all(action='DESELECT')

    if scene.visualize_leafs:
        bpy.context.scene.objects.active = obj
        vgroups.active_index = vgroups["leaf"].index
        bpy.ops.paint.weight_paint_toggle()

    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.wm.properties_add(data_path="object")
    obj["prop"] = "is_tree"
    bpy.ops.wm.properties_add(data_path="object")
    obj["prop1"] = "armature" if scene.create_armature else "no_armature"


class MakeTreeOperator(Operator):
    """Make a tree"""
    bl_idname = "mod_tree.add_tree"
    bl_label = "Make Tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        seed(scene.SeedProp)
        create_tree(bpy.context.scene.cursor_location)

        return {'FINISHED'}


class UpdateTreeOperator(Operator):
    """Update a tree"""
    bl_idname = "mod_tree.update_tree"
    bl_label = "Update Selected Tree"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        seed(scene.SeedProp)
        obj = bpy.context.active_object

        try:
            prop_name = obj.get('prop')
        except AttributeError:
            self.report({'ERROR'}, "No active tree object!")
            return {'CANCELLED'}

        if prop_name == "is_tree":
            pos = obj.location
            scale = obj.scale
            rot = obj.rotation_euler

            create_tree(pos)
            ob = bpy.context.active_object
            ob.scale = scale
            ob.rotation_euler = rot
            ob.select = False
            obj.select = True

            if obj.get('prop1') == 'armature':
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


class SaveTreePresetOperator(Operator):
    """Save Tree Preset"""
    bl_idname = "mod_tree.save_preset"
    bl_label = "Save Preset"
    bl_description = "Saves current settings as a preset"
    bl_options = {"REGISTER"}

    def execute(self, context):
        scene = context.scene

        preset = ("preserve_trunk:{}\n"
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
                  "mat:{}\n"
                  "roots_iteration:{}\n"
                  "create_roots:{}\n"
                  "branch_rotate:{}\n"
                  "branch_random_rotate:{}\n"
                  "particle:{}\n"
                  "number:{}\n"
                  "display:{}\n".format(
                    # bools can't be stored as "True" or "False" b/c bool(x) will evaluate to
                    # True if x = "True" or if x = "False"...the fix is to do an int() conversion
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
                    int(scene.mat),
                    scene.roots_iteration,
                    int(scene.create_roots),
                    scene.branch_rotate,
                    scene.branch_random_rotate,
                    int(scene.particle),
                    scene.number,
                    scene.display))

        # write to file
        prsets_directory = os.path.join(os.path.dirname(__file__), "mod_tree_presets")
        prset = os.path.join(prsets_directory, scene.preset_name + ".mtp")  # mtp stands for modular tree preset

        os.makedirs(os.path.dirname(prset), exist_ok=True)
        with open(prset, 'w') as p:
            print(preset, file=p, flush=True)

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
            preset = p.readlines()

        for line in preset:
            if ":" in line:
                setting, value = line.split(":")
                if setting == "preserve_trunk":
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
                    scene.obstacle = value
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

        return {'FINISHED'}


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
        box.prop(scene, 'mat')
        box.prop(scene, 'uv')


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
        box.prop(scene, 'radius_dec')
        col = box.column(True)
        col.prop(scene, 'branch_rotate')
        col.prop(scene, 'branch_random_rotate')
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


# classes to register
classes = [MakeTreeOperator, UpdateTreeOperator, SaveTreePresetOperator, RemoveTreePresetOperator,
           LoadTreePresetOperator,
           MakeTreePanel, RootsAndTrunksPanel, TreeBranchesPanel, AdvancedSettingsPanel,
           TreePresetLoadMenu, TreePresetRemoveMenu, MakeTreePresetsPanel]


def register():
    # register all classes
    for i in classes:
        bpy.utils.register_class(i)

    # register props
    Scene.preset_name = StringProperty(name="Preset Name", default="MyPreset")

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
        min=1,
        default=20)

    Scene.preserve_end = IntProperty(
        name="Trunk End",
        min=0,
        default=25,
        description="iteration on which trunk preservation will end")

    Scene.trunk_length = IntProperty(
        name="Trunk Iterations",
        min=0,
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
        name="Unwrap",
        default=False,
        description="unwrap tree. WARNING: takes time, check last")

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


def unregister():
    # unregister all classes
    for i in classes:
        bpy.utils.unregister_class(i)

    # unregister props
    del Scene.preset_name
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
    del Scene.mat
    del Scene.roots_iteration
    del Scene.create_roots
    del Scene.branch_rotate
    del Scene.branch_random_rotate
    del Scene.particle
    del Scene.number
    del Scene.display


if __name__ == "__main__":
    register()
