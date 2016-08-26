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

from mathutils import Vector, Matrix
from random import random, randint
from math import pi, radians

import bpy

from modular_tree.clock import Clock
from modular_tree.uv_tools import rotate, add_seams
from modular_tree.particle_configurator import create_system
from modular_tree.material_tools import build_bark_material, build_leaf_material


class Module:
    """This is used to represent a branch

    Methods:
        __init__ - Initialises the variables
        __repr__ - How the Module is represented
    """

    def __init__(self, entree, sortie, verts, faces):
        """Initialises the variables

        Args:
            entree - (list of int) The indexes of the entry vertices
            sortie - (list of int) The indexes of the exit vertices
            verts - (list of vector) The vertices of the Module
            faces - (list of (int, int, int, int)) The faces of the Module
        """
        self.entree = entree
        self.sortie = sortie
        self.verts = verts
        self.faces = faces

    def __repr__(self):
        return 'entry vertices:{} , number of splits:{}'.format(len(self.entree), len(self.sortie))


end_cap = Module(
    # entree
    [0, 1, 2, 3, 4, 5, 6, 7],
    # sortie
    [],
    # verts
    [(0.0, 1.0, 0.02), (-0.71, 0.71, 0.02), (-1.0, -0.0, 0.04), (-0.71, -0.71, 0.04), (0.0, -1.0, 0.02),
     (0.71, -0.71, 0.02), (1.0, 0.0, 0.04), (0.71, 0.71, 0.04), (0.0, 0.98, 0.14), (-0.69, 0.69, 0.14),
     (-0.98, -0.0, 0.21), (-0.69, -0.69, 0.21), (0.0, -0.98, 0.14), (0.69, -0.69, 0.14), (0.98, 0.0, 0.21),
     (0.69, 0.69, 0.21), (0.0, 0.88, 0.26), (-0.62, 0.62, 0.26), (-0.88, -0.0, 0.33), (-0.62, -0.62, 0.33),
     (0.0, -0.88, 0.26), (0.62, -0.62, 0.26), (0.88, 0.0, 0.33), (0.62, 0.62, 0.33), (0.0, 0.74, 0.32),
     (-0.52, 0.52, 0.32), (-0.74, -0.0, 0.41), (-0.52, -0.52, 0.41), (0.0, -0.74, 0.32), (0.52, -0.52, 0.32),
     (0.74, 0.0, 0.41), (0.52, 0.52, 0.41), (0.0, 0.33, 0.59), (-0.23, 0.23, 0.59), (-0.26, 0.02, 0.67),
     (-0.16, -0.2, 0.67), (0.0, -0.33, 0.59), (0.23, -0.23, 0.59), (0.26, -0.02, 0.67), (0.16, 0.2, 0.67)],
    # faces
    [(7, 15, 14, 6), (5, 13, 12, 4), (3, 11, 10, 2), (0, 8, 15, 7), (6, 14, 13, 5), (4, 12, 11, 3), (2, 10, 9, 1),
     (15, 8, 16, 23), (13, 14, 22, 21), (11, 12, 20, 19), (9, 10, 18, 17), (14, 15, 23, 22), (12, 13, 21, 20),
     (10, 11, 19, 18), (8, 9, 17, 16), (18, 19, 27, 26), (16, 17, 25, 24), (23, 16, 24, 31), (21, 22, 30, 29),
     (19, 20, 28, 27), (17, 18, 26, 25), (22, 23, 31, 30), (20, 21, 29, 28), (30, 31, 39, 38), (28, 29, 37, 36),
     (26, 27, 35, 34), (24, 25, 33, 32), (31, 24, 32, 39), (29, 30, 38, 37), (27, 28, 36, 35), (35, 38, 39, 34),
     (39, 32, 33, 34), (35, 36, 37, 38), (1, 9, 8, 0), (25, 26, 34, 33)])


class Split:
    """This is used to represent a branch split, each vertex position is an interpolation of two vectors, which allows more variation

    Methods:
        __init__ - Initialises the variables
    """

    def __init__(self, entree, sortie, verts1, verts2, faces, seams):
        """Initialises the variables

        Args:
            entree - (list of int) The indexes of the entry vertices
            sortie - ((list of int, list of int)) The indexes of the exit vertices
            verts1 - (list of vector) The vertices of the split in one form
            verts2 - (list of vector) The vertices of the split in the second form
            faces - (list of (int, int, int, int)) The faces of the Split
            seams - (list of (int, int)) The seams of the Split
        """
        self.entree = entree
        self.sortie = sortie
        self.verts1 = verts1
        self.verts2 = verts2
        self.faces = faces
        self.Seams = seams


def interpolate(verts1, verts2, t):
    """Linearly interpolates the vertices positions

    Args:
        verts1 - (list of vector) The first positions
        verts2 - (list of vector) The second positions
        t - (float) The interpolation factor

    Returns:
        (list of vector) The interpolated positions
    """
    return [Vector(verts1[i]) * (1 - t) + Vector(verts2[i]) * t for i in range(len(verts1))]


S2 = Split(
    # entree
    [0, 1, 2, 3, 4, 5, 6, 7],
    # sortie
    ([8, 9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22, 23]),
    # verts1
    [(-0.0, 1.0, -0.01), (-0.71, 0.71, -0.01), (-1.0, -0.0, -0.01), (-0.71, -0.71, -0.01), (0.0, -1.0, -0.01),
     (0.71, -0.71, -0.01), (1.0, -0.0, -0.02), (0.71, 0.71, -0.02), (-0.98, 0.89, 1.84), (-1.49, 0.74, 1.62),
     (-1.78, 0.24, 1.53), (-1.67, -0.33, 1.64), (-1.23, -0.64, 1.87), (-0.73, -0.51, 2.09), (-0.46, 0.0, 2.18),
     (-0.56, 0.59, 2.07), (0.72, 1.02, 1.8), (1.3, 0.65, 1.8), (1.29, -0.07, 1.93), (0.81, -0.6, 2.07),
     (0.12, -0.57, 2.13), (-0.37, -0.06, 2.17), (-0.46, 0.62, 2.06), (0.03, 1.05, 1.88), (-1.19, -0.63, 0.6),
     (-1.42, -0.01, 0.52), (-0.71, -1.0, 0.98), (-0.39, -0.91, 1.36), (0.63, -0.72, 1.11), (-0.2, -0.73, 1.49),
     (0.85, 0.64, 0.64), (1.12, 0.01, 0.68), (0.28, 0.97, 0.69), (-0.72, 0.91, 0.89), (-1.21, 0.7, 0.6),
     (-0.36, 0.92, 1.36), (-0.43, -1.0, 0.68), (0.13, -1.05, 0.69), (-.42, 0.09, 0.90), (0.13, 0.16, 0.97)],
    # verts2
    [(-0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
     (0.71, -0.71, 0.0), (1.0, -0.0, -0.0), (0.71, 0.71, -0.01), (-1.34, 0.76, 0.99), (-1.43, 0.53, 0.47),
     (-1.47, -0.01, 0.25), (-1.43, -0.56, 0.48), (-1.33, -0.79, 1.0), (-1.24, -0.58, 1.51), (-1.21, -0.03, 1.72),
     (-1.26, 0.57, 1.53), (0.73, 1.02, 1.08), (1.08, 0.65, 0.61), (1.18, -0.07, 0.7), (1.0, -0.6, 1.16),
     (0.63, -0.57, 1.75), (0.35, -0.06, 2.16), (0.21, 0.62, 2.16), (0.38, 1.05, 1.67), (-0.94, -0.63, 0.26),
     (-1.12, -0.01, 0.09), (-0.8, -1.0, 0.78), (-0.59, -0.81, 1.45), (0.75, -0.72, 0.94), (-0.07, -0.51, 1.66),
     (0.84, 0.64, 0.42), (1.12, 0.01, 0.39), (0.31, 0.97, 0.63), (-0.79, 0.91, 0.69), (-0.96, 0.7, 0.25),
     (-0.38, 0.92, 1.37), (-0.43, -1.0, 0.69), (0.13, -1.05, 0.7), (-.98, 0, 0.16), (0.85, 0.16, 0.49)],
    # faces
    [(25, 24, 11, 10), (15, 14, 21, 22), (2, 3, 24, 25), (12, 26, 27, 13), (12, 11, 24, 26), (20, 29, 28, 19),
     (20, 21, 14, 29), (14, 13, 27, 29), (31, 30, 17, 18), (30, 32, 16, 17), (7, 0, 32, 30), (6, 7, 30, 31),
     (18, 19, 28, 31), (8, 33, 34, 9), (9, 34, 25, 10), (1, 2, 25, 34), (15, 35, 33, 8), (23, 35, 15, 22),
     (35, 23, 16, 32), (33, 35, 32, 0), (34, 33, 0, 1), (5, 6, 31, 28), (36, 26, 24, 3), (37, 36, 3, 4),
     (4, 5, 28, 37), (27, 26, 36, 37), (28, 29, 27, 37)],
    # seams
    [(4, 37), (36, 37), (26, 36), (12, 26), (28, 37), (19, 28), (14, 21)])

S1 = Split(
    # entree
    [0, 1, 2, 3, 4, 5, 6, 7],
    # sortie
    ([8, 9, 10, 11, 12, 13, 14, 15], [16, 17, 18, 19, 20, 21, 22, 23]),
    # verts1
    [(0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
     (0.71, -0.71, 0.0), (1.0, 0.0, 0.0), (0.71, 0.71, 0.0), (-0.0, -0.17, 1.01), (-0.42, -0.29, 0.88),
     (-0.59, -0.58, 0.58), (-0.42, -0.88, 0.29), (0.0, -1.0, 0.16), (0.42, -0.88, 0.29), (0.59, -0.58, 0.58),
     (0.42, -0.29, 0.88), (-0.0, 1.0, 0.17), (-0.43, 0.88, 0.29), (-0.61, 0.57, 0.6), (-0.43, 0.26, 0.9),
     (0.0, 0.13, 1.02), (0.43, 0.26, 0.9), (0.61, 0.57, 0.6), (0.43, 0.88, 0.29), (0.85, 0.44, 0.37),
     (0.91, -0.38, 0.42), (0.79, 0.04, 0.65), (0.0, -0.02, 1.02), (0.43, -0.02, 0.89), (-0.43, -0.02, 0.89),
     (-0.91, -0.38, 0.41), (-0.82, 0.04, 0.65), (-0.91, 0.44, 0.37), (0, -1, 1), (0, 1, 1)],
    # verts2
    [(0.0, 1.0, 0.0), (-0.71, 0.71, 0.0), (-1.0, -0.0, 0.0), (-0.71, -0.71, 0.0), (0.0, -1.0, 0.0),
     (0.71, -0.71, 0.0), (1.0, 0.0, 0.0), (0.71, 0.71, 0.0), (-0.0, -0.17, 1.01), (-0.42, -0.29, 0.88),
     (-0.59, -0.58, 0.58), (-0.42, -0.88, 0.29), (0.0, -1.0, 0.16), (0.42, -0.88, 0.29), (0.59, -0.58, 0.58),
     (0.42, -0.29, 0.88), (-0.0, 1.0, 0.17), (-0.43, 0.88, 0.29), (-0.61, 0.57, 0.6), (-0.43, 0.26, 0.9),
     (0.0, 0.13, 1.02), (0.43, 0.26, 0.9), (0.61, 0.57, 0.6), (0.43, 0.88, 0.29), (0.85, 0.44, 0.37),
     (0.91, -0.38, 0.42), (0.79, 0.04, 0.65), (0.0, -0.02, 1.02), (0.43, -0.02, 0.89), (-0.43, -0.02, 0.89),
     (-0.91, -0.38, 0.41), (-0.82, 0.04, 0.65), (-0.91, 0.44, 0.37), (0, -1, 1), (0, 1, 1)],
    # faces
    [(4, 5, 13, 12), (3, 4, 12, 11), (7, 0, 16, 23), (0, 1, 17, 16), (27, 28, 21, 20), (29, 27, 20, 19),
     (25, 13, 5, 6), (6, 7, 23, 24), (22, 26, 24, 23), (14, 13, 25, 26), (24, 26, 25, 6), (9, 8, 27, 29),
     (8, 15, 28, 27), (22, 21, 28, 26), (14, 26, 28, 15), (30, 31, 32, 2), (2, 32, 17, 1), (2, 3, 11, 30),
     (10, 31, 30, 11), (17, 32, 31, 18), (10, 9, 29, 31), (18, 31, 29, 19)],
    # seams
    [(4, 37), (36, 37), (26, 36), (12, 26), (28, 37), (19, 28), (14, 21)])

Joncts = [S1, S2]

root = Module(
    # entree
    [],
    # sortie
    (1, [0, 1, 2, 3, 4, 5, 6, 7]),
    # verts
    [Vector((0.0, 0.9928191900253296, 0.9806214570999146)),
     Vector((-0.7020291090011597, 0.7020291090011597, 0.9806214570999146)),
     Vector((-0.9928191900253296, -4.3397506033215905e-08, 0.9806214570999146)),
     Vector((-0.7020291090011597, -0.7020291090011597, 0.9806214570999146)),
     Vector((8.679501206643181e-08, -0.9928191900253296, 0.9806214570999146)),
     Vector((0.7020292282104492, -0.7020290493965149, 0.9806214570999146)),
     Vector((0.9928191900253296, 1.1839250468881346e-08, 0.9806214570999146)),
     Vector((0.7020292282104492, 0.7020291090011597, 0.9806214570999146)),
     Vector((0.0, 1.0136922597885132, 0.45493215322494507)),
     Vector((-0.716788649559021, 0.716788649559021, 0.45493215322494507)),
     Vector((-1.0136922597885132, -4.4309896196637055e-08, 0.45493215322494507)),
     Vector((-0.716788649559021, -0.716788649559021, 0.45493215322494507)),
     Vector((8.861979239327411e-08, -1.0136922597885132, 0.45493215322494507)),
     Vector((0.7167887687683105, -0.7167885303497314, 0.45493215322494507)),
     Vector((1.0136922597885132, 1.2088158918288627e-08, 0.45493215322494507)),
     Vector((0.7167887687683105, 0.7167885899543762, 0.45493215322494507)),
     Vector((0.0, 1.1711314916610718, 0.011928796768188477)),
     Vector((-0.8281149864196777, 0.8281149864196777, 0.011928796768188477)),
     Vector((-1.1711314916610718, -5.119178325685425e-08, 0.011928796768188477)),
     Vector((-0.8281149864196777, -0.8281149864196777, 0.011928796768188477)),
     Vector((1.023835665137085e-07, -1.1711314916610718, 0.011928796768188477)),
     Vector((0.8281151056289673, -0.8281148672103882, 0.011928796768188477)),
     Vector((1.1711314916610718, 1.3965602896348628e-08, 0.011928796768188477)),
     Vector((0.8281151056289673, 0.828114926815033, 0.011928796768188477)),
     Vector((0.0, 1.416882872581482, -0.3086543381214142)),
     Vector((-1.0018874406814575, 1.0018874406814575, -0.3086543381214142)),
     Vector((-1.416882872581482, -6.19339104446226e-08, -0.3086543381214142)),
     Vector((-1.0018874406814575, -1.0018874406814575, -0.3086543381214142)),
     Vector((1.238678208892452e-07, -1.416882872581482, -0.3086543381214142)),
     Vector((1.001887559890747, -1.0018872022628784, -0.3086543381214142)),
     Vector((1.416882872581482, 1.6896155585754968e-08, -0.3086543381214142)),
     Vector((1.001887559890747, 1.001887321472168, -0.3086543381214142))],
    # faces
    [(7, 6, 14, 15), (5, 4, 12, 13), (3, 2, 10, 11), (1, 0, 8, 9), (0, 7, 15, 8), (6, 5, 13, 14),
     (4, 3, 11, 12), (2, 1, 9, 10), (9, 8, 16, 17), (8, 15, 23, 16), (14, 13, 21, 22), (12, 11, 19, 20),
     (10, 9, 17, 18), (15, 14, 22, 23), (13, 12, 20, 21), (11, 10, 18, 19), (16, 23, 31, 24),
     (22, 21, 29, 30), (20, 19, 27, 28), (18, 17, 25, 26), (23, 22, 30, 31), (21, 20, 28, 29),
     (19, 18, 26, 27), (17, 16, 24, 25)])

branch = Module(
    # entree
    [0, 1, 2, 3, 4, 5, 6, 7],
    # sortie
    (1, [0, 1, 2, 3, 4, 5, 6, 7]),
    # verts
    [Vector((0.0, 1.0, 0.0)),
     Vector((-0.7071067690849304, 0.7071067690849304, 0.0)),
     Vector((-1.0, -4.371138828673793e-08, 0.0)),
     Vector((-0.7071067690849304, -0.7071067690849304, 0.0)),
     Vector((8.742277657347586e-08, -1.0, 0.0)),
     Vector((0.70710688829422, -0.7071066498756409, 0.0)),
     Vector((1.0, 1.1924880638503055e-08, 0.0)),
     Vector((0.70710688829422, 0.7071067094802856, 0.0))],
    # faces
    [])

trunk = Split(
    # entree
    [0, 1, 2, 3, 4, 5, 6, 7],
    # sortie
    ([8, 9, 10, 11, 12, 13, 14, 15], [55, 56, 57, 58, 59, 60, 61, 62]),
    # verts1
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
     (0.42, -1.98, 1.03), (0.59, -1.6, 1.22), (0.42, -1.23, 1.41), (0, 0, 1), (0, -0.35, 0.59)],
    # verts2
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
    # faces
    [(26, 15, 14, 25), (30, 13, 12, 29), (34, 11, 10, 33), (38, 9, 8, 37), (37, 8, 15, 26), (25, 14, 13, 30),
     (29, 12, 11, 34), (33, 10, 9, 38), (2, 32, 39, 1), (43, 33, 38, 46), (4, 28, 35, 3), (6, 24, 31, 5),
     (40, 25, 30, 42), (0, 36, 27, 7), (45, 37, 26, 41), (1, 39, 36, 0), (46, 38, 37, 45), (3, 35, 32, 2),
     (44, 34, 33, 43), (5, 31, 28, 4), (7, 27, 24, 6), (41, 26, 25, 40), (27, 41, 40, 24), (35, 44, 43, 32),
     (39, 46, 45, 36), (36, 45, 41, 27), (24, 40, 42, 31), (32, 43, 46, 39), (17, 34, 44, 18), (18, 44, 35, 19),
     (19, 35, 28, 20), (20, 28, 31, 21), (21, 31, 42, 22), (22, 42, 30, 23), (23, 30, 29, 16), (16, 29, 34, 17),
     (16, 47, 54, 23), (23, 54, 53, 22), (22, 53, 52, 21), (21, 52, 51, 20), (20, 51, 50, 19), (19, 50, 49, 18),
     (18, 49, 48, 17), (17, 48, 47, 16), (53, 54, 62, 61), (51, 52, 60, 59), (49, 50, 58, 57), (47, 48, 56, 55),
     (54, 47, 55, 62), (52, 53, 61, 60), (50, 51, 59, 58), (48, 49, 57, 56)],
    # seams
    [(29, 12), (4, 28), (28, 20), (29, 16), (16, 47), (51, 20), (59, 51), (55, 47)])


class Trunk:
    """This is used to represent the base of a trunk with roots"""
    def __init__(self, roots, stem, verts, faces, seams):
        """Initializes the variables

        Args:
            roots - (list of (Vector, list of int)) The directions and indexes of roots exits
            stem - (list of int) The indexes of the trunk exit
            verts - (list of Vector) The vertices
            faces - (list of (int, int, int, int)) The faces
            seams - (list of (int, int)) The seams
        """
        self.roots = roots
        self.stem = stem
        self.verts = verts
        self.faces = faces
        self.Seams = seams


R1 = Trunk(
    # roots
    [(Vector((-6.293336696217011e-08, -0.6988458633422852, -0.3152722477912903)), 0.69, [110, 111, 112, 113, 114, 115, 116, 117]),
     (Vector((0.6009913086891174, -0.04263520613312721, -0.3981175780296326)), 0.34, [55, 56, 57, 58, 59, 60, 61, 62]),
     (Vector((0.5693859457969666, 0.49961066246032715, -0.352831494808197)), 0.34, [47, 48, 49, 50, 51, 52, 53, 54]),
     (Vector((-0.779069721698761, 0.455067813396454, -0.24110554456710815)), 0.34, [63, 64, 65, 66, 67, 68, 69, 70, 101]),
     (Vector((-0.7720233201980591, -0.09697314351797104, -0.3281529068946838)), 0.56, [71, 72, 73, 74, 75, 76, 77, 78]),
     (Vector((-1.859164768802657e-07, 0.2071729600429535, -0.4783042669296265)), 0.60, [39, 40, 41, 42, 43, 44, 45, 46])],
    # stem
    [0, 1, 2, 3, 4, 5, 6, 7],
    # verts
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
    # faces
    [(7, 6, 14, 15), (5, 4, 12, 13), (3, 2, 10, 11), (1, 0, 8, 9), (0, 7, 15, 8), (6, 5, 13, 14), (4, 3, 11, 12),
     (2, 1, 9, 10), (9, 8, 16, 17), (8, 15, 23,  16), (14,  13,  21, 22), (12, 11, 19, 20), (10, 9, 17, 18),
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
    # seams
    [(0, 8), (8, 16), (24, 16), (80, 79), (24, 79), (39, 86), (80, 86), (40, 39), (41, 40), (42, 41), (43, 42),
     (44, 43), (45, 44), (46, 45), (39, 46), (48, 47), (49, 48), (50, 49), (51, 50), (52, 51), (53, 52), (54, 53),
     (47, 54), (56, 55), (57, 56), (58, 57), (59, 58), (60, 59), (61, 60), (62, 61), (55, 62), (64, 63), (65, 64),
     (66, 65), (67, 66), (68, 67), (69, 68), (70, 69), (101, 70), (72, 71), (73, 72), (74, 73), (75, 74), (76, 75),
     (77, 76), (78, 77), (71, 78), (63, 101), (111, 110), (112, 111), (113, 112), (114, 113), (115, 114), (116, 115),
     (117, 116), (110, 117)])


def joindre(verts, faces, v1_i, v2_i):
    """ Takes two sets of eight vertices, a list of vertices, a list of faces, and adds new faces as the bridge edge loops operator would do.

    Args:
        verts - (list of (Vector, Vector, Vector)) The list of vertices
        faces - (list of (int, int, int, int)) The list of faces
        v1_i - (int, int, int, int, int, int, int, int) The indexes of the first group of vertices
        v2_i - (int, int, int, int, int, int, int, int) The indexes of the second group of vertices
    """
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


def join(verts, faces, indexes, object_verts, object_faces, scale, i1, i2, entree, directions, branch_length, s_index,
         seams,
         jonc_seams, random_angle, branch_rotation):
    """ The goal is to add a split to the tree. To do that, there is the list of existing vertices, the list of existing faces, the list of vertices to add and the list of faces to add.
        To know where to add the split, the indexes of eight vertices is given.

    Args:
        verts - (list of (Vector, Vector, Vector)) The existing vertices
        faces - (list of (int, int, int, int)) The existing faces
        indexes - ((int, int, int, int, int, int, int, int)) the indexes of the end of the branch on which the split will be added
        object_verts - (list of (Vector, Vector, Vector)) The vertices to add
        object_faces - (list of (int, int, int, int)) The faces to add
        scale - (float) the scale of which the split must be
        i1 - ((int, int, int, int, int, int, int, int))The indexes of the first end of the split
        i2 - ((int, int, int, int, int, int, int, int)) The indexes of the second end of the split
        entree - ((int, int, int, int, int, int, int, int)) the indexes of the base of the split
        directions - (Vector) The direction the split will be pointing at
        branch_length - (float) the distance between the branch end and the split base
        s_index - (int) The index of the last vertex that is part of a seam
        seams - (list of (int, int)) The seams of the tree
        jonc_seams - (list of (int, int)) The seams of the split
        random_angle - (float) The amount of possible deviation between directions and the actual split direction
        branch_rotation - (float) The rotation of the split around directions

    Returns:
        i1 - ((int, int, int, int, int, int, int, int)) The indexes of the first end of the split
        i2 - ((int, int, int, int, int, int, int, int)) The indexes of the second end of the split
        d1 - (Vector) The direction of the first end of the split
        d2 - (Vector) The direction of the second end of the split
        r1 - (float) The radius of the first end of the split
        r2 - (float) The radius of the second end of the split
        i1[0] - (int) The index of the last vertex that is part of a seam on the first end of the split
        i2[0] - (int) The index of the last vertex that is part of a seam on the second end of the split
    """
    random1 = random_angle * (random() - 0.5)
    random2 = random_angle * (random() - 0.5)
    random3 = random_angle * (random() - 0.5)

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
    return i1, i2, d1, d2, r1, r2, i1[0], i2[0]  # no need to return i1[0] and i2[0]...just do that outside of the func


def join_branch(verts, faces, indexes, scale, branch_length, branch_verts, direction, rand, s_index, seams):
    """ The goal is to add a Module to the tree. To do that, there is the list of existing vertices, the list of existing faces, the list of vertices to add and the list of faces to add.
        To know where to add the Module, the indexes of eight vertices is given.

    Args:
        verts - (list of (Vector, Vector, Vector)) The existing vertices
        faces - (list of (int, int, int, int)) The existing faces
        indexes - ((int, int, int, int, int, int, int, int)) the indexes of the end of the branch on which the Module will be added
        scale - (float) the scale of which the Module must be
        branch_length - (float) the distance between the branch end and the Module base
        branch_verts - (list of (Vector, Vector, Vector)) The vertices to add
        direction - (Vector) The direction the Module will be pointing at
        rand - (float) The amount of possible deviation between direction and the actual Module direction
        s_index - (int) The index of the last vertex that is part of a seam
        seams - (list of (int, int)) The seams of the tree

    Returns:
        nentree - ((int, int, int, int, int, int, int, int)) The indexes of the end of the Module
        direction - (Vector) The direction of the end of the Module
        ns_index - (int) The index of the last vertex that is part of a seam on the end of the Module
    """
    barycentre = Vector((0, 0, 0))
    random1 = rand * (random() - 0.5)
    random2 = rand * (random() - 0.5)
    random3 = rand * (random() - 0.5)
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
    seams.append((s_index, ns_index))

    return nentree, direction, ns_index


def gravity(direction, gravity_strength):
    """ Applies a down translation to a vector to simulate gravity

    Args:
        direction - (Vector) The Vector to apply gravity to
        gravity_strength - (float)

    Returns:
        (Vector) The vector direction translated downward
    """
    v = Vector((0, 0, -1))
    norm = direction.length
    factor = (direction.cross(v)).length / norm / 100 * gravity_strength
    return direction + v * factor


def add_tuple(t, x):
    """Adds a value x to each component of the tuple

    Args:
        t - (tupe)
        x - (int,float)

    Returns:
         tuple in the form (x + a, x + b, x + c,...) where t is in the form (a, b, c,...)"""
    return tuple([x + i for i in t])


def rot_scale(v_co, scale, directions, rot_z):
    """ Rotates and scales a set of vectors

    Args:
        v_co - (list of (float, float, float))  The coordinates of the vectors
        scale - (foat) The scalar by xhich each vector is multiplied
        directions - (tuple) A vector that would be collinear whith a former (0,0,1) vector after the rotation
        rot_z - (float) The rotation of the set of vector around directions

    Returns:
        A set of coordinates representing all vectors of v_co after rotation and scaling
    """

    (x, y, z) = directions
    directions = Vector((-x, -y, z))
    q = Vector((0, 0, 1)).rotation_difference(directions)
    mat_rot = q.to_matrix()
    mat_rot.resize_4x4()
    mc = Matrix.Rotation(rot_z, 4, 'Z')
    v_co = [((v * scale) * mc) * mat_rot for v in v_co]
    return v_co


def fix_normals(inside):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=inside)
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')


def add_leaf(position, direction, rotation, scale):
    verts, faces = ([(-1.0, 0.07, 0.05), (1.0, 0.07, 0.05), (-1.0, -1.01, 1.75),
                     (1.0, -1.01, 1.75), (-1.0, -0.76, 1.1), (-1.0, -0.38, 0.55),
                     (1.0, -0.38, 0.55), (1.0, -0.76, 1.1), (-0.33, 0.0, 0.0),
                     (0.33, 0.0, 0.0), (0.33, -1.16, 1.64), (-0.33, -1.16, 1.64),
                     (0.33, -0.56, 0.42), (-0.33, -0.56, 0.42), (0.33, -0.9, 1.0), (-0.33, -0.9, 1.0)],

                    [(14, 7, 3, 10), (9, 1, 6, 12), (12, 6, 7, 14), (5, 13, 15, 4), (13, 12, 14, 15),
                     (0, 8, 13, 5), (8, 9, 12, 13), (4, 15, 11, 2), (15, 14, 10, 11)])
    verts = [Vector(v) for v in verts]
    verts = rot_scale(verts, scale, direction, rotation)
    verts = [v + position for v in verts]
    mesh = bpy.data.meshes.new("leaf")
    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=False)
    obj = bpy.data.objects.new("leaf", mesh)
    obj.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    obj.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()


def create_tree(position, is_twig=False):
    """Creates a tree

    Details:
        There is a list of vertices, a list of faces and a list of seams.
        There is a list of all current end of the tree. At each iteration all those ends can evolve in three diferent ways:
            -The end can continue to grow as a branch, with a new end
            -The end can be splited in two branches, with a new end each
            -The end can break
        Depending on this choice, vertices and faces of a Module, Split or end cap will be added to the vertices and faces list.
        This processus is executed for both roots and branches generation.
        After this, the tree object itself is created, the vertices, faces and seams are applied.
        Once the object is created, it can be unwrapped, a material is asigned or created, and an armature is created.


    Args:
        position - (Vector) Position to generate tree at
        is_twig - (Bool) Is the tree a twig
    """
    scene = bpy.context.scene

    clock = Clock("create_tree")
    if not scene.uv:
        scene.finish_unwrap = False
    if scene.unwrap_end_iteration >= scene.iteration:
        scene.unwrap_end_iteration = scene.iteration - 1

    twig_leafs = []

    # deselecting all objects
    for select_ob in bpy.context.selected_objects:
        select_ob.select = False

    make_roots = scene.create_roots
    trunk2 = scene.preserve_trunk
    radius = scene.radius

    # the list of bones is a list of...
    # [(string : parent name, string : bone name, Vector : tail position, Vector : head position), ...]
    bones = []
    leafs_start_index = 0
    unwrap_stop_index = 0
    big_j = S1
    seams2 = [s for s in R1.Seams]
    entree = [i for i in big_j.entree]

    last_bone = (1, Vector((0, 0, 1)))

    # Roots generation
    if not make_roots:
        verts = [Vector(v) * radius for v in root.verts]
        faces = [f for f in root.faces]
        extr = [i for i in root.sortie[1]]
    else:
        print("Generating Roots...")
        verts = [Vector(v) * radius for v in R1.verts]
        faces = [f for f in R1.faces]
        extr = [i for i in R1.stem]
        roots = [(i[2], i[1], i[0], i[2][0]) for i in R1.roots]
        roots_variations = 0.5
        roots_length = 1.4
        roots_rad_dec = 0.7

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
                    direction += 0.7 * Vector((0, 0, -1)) / (max(1, 20 * abs(barycentre.z)))
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

    # branches generation
    print("Generating Branches...")
    for i in range(scene.iteration + scene.trunk_length):
        if i == scene.iteration + scene.trunk_length - scene.leafs_iteration_length:
            leafs_start_index = len(verts)
        if i == scene.unwrap_end_iteration + scene.trunk_length:
            unwrap_stop_index = len(verts)

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
                scene.update()

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
                nextremites.append((ni, radius * 0.98, direction, nsi, nb, trunk2, curr_rotation))

            elif i == scene.iteration + scene.trunk_length - 1 or random() < scene.break_chance:
                end_verts = [Vector(v) for v in end_cap.verts]
                end_faces = [f for f in end_cap.faces]
                if is_twig:
                    twig_leafs.append((pos, direction, curr_rotation))
                n = len(verts)
                join_branch(verts, faces, indexes, radius, scene.trunk_space, end_verts, direction,
                            scene.trunk_variation, s_index, seams2)

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
                                                                direction, length, s_index, seams2, jonct_seams,
                                                                variation, new_rotation)
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
                                                 variation, s_index, seams2)
                if is_twig:
                    twig_leafs.append((pos + direction * length * random(), direction, curr_rotation))
                sortie = pos + direction * scene.branch_length

                if i <= scene.bones_iterations:
                    bones.append((Lb[0], len(bones) + 2, Lb[1], sortie))

                nb = (len(bones) + 1, sortie)
                if scene.gravity_start <= i <= scene.gravity_end:
                    direction = gravity(direction, scene.gravity_strength)
                nextremites.append((ni, radius * scene.radius_dec, direction, nsi, nb, trunk2, curr_rotation))

        extremites = nextremites
    # mesh and object creation
    print("Building Object...")
    mesh = bpy.data.meshes.new("tree")

    mesh.from_pydata(verts, [], faces)
    mesh.update(calc_edges=False)
    obj = bpy.data.objects.new("tree", mesh)
    obj.location = position
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    bpy.ops.object.shade_smooth()
    obj.select = False

    vgroups = obj.vertex_groups

    # add vertex group for the leaves particle system
    leaves_group = obj.vertex_groups.new("leaf")
    vgroups.active_index = vgroups["leaf"].index
    leaves_group.add([i for i in range(leafs_start_index, len(verts))], 1.0, "ADD")  # add weights

    # add vertex group for the wind animations
    wind_group = obj.vertex_groups.new("wind_anim")

    # fix normals, then make sure they are fixed :)
    print("Setting Normals...")
    fix_normals(inside=False)
    if obj.data.polygons[0].normal.x < 0:
        fix_normals(inside=True)

    # particle setup
    if scene.particle:
        print("Configuring Particle System...")
        create_system(obj, scene.number, scene.display, vgroups["leaf"])

    # uv unwrapping
    if scene.uv:
        print("Unwrapping...")
        clock.add_sub_job("uv")
        test = [[False, []] for _ in range(len(verts))]
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

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.mark_seam(clear=False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh.vertex_colors.new()
        color_map = mesh.vertex_colors.active
        for i in range(unwrap_stop_index):
            color_map.data[i].color = (0, 0, 0)
            mesh.vertices[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')
        if scene.finish_unwrap:
            bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)
            rotate()  # this will set the mode to object already
        else:
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.mode_set(mode='VERTEX_PAINT')
        bpy.ops.paint.vertex_color_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')
        clock.stop("uv")

    # material creation
    print("Setting Materials...")
    if scene.mat:
        obj.active_material = build_bark_material("bark")

    elif bpy.data.materials.get(scene.bark_material) is not None:
        obj.active_material = bpy.data.materials.get(scene.bark_material)

    # armature creation
    if scene.create_armature:
        print("Building Armature...")
        clock.add_sub_job("armature")
        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=Vector((0, 0, 0)))
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
        scene.objects.active = arm
        bpy.ops.object.parent_set(type='ARMATURE_AUTO')
        bpy.ops.object.select_all(action='DESELECT')
        clock.stop("armature")

    if scene.visualize_leafs:
        clock.add_sub_job("vis leaves")
        scene.objects.active = obj
        vgroups.active_index = vgroups["leaf"].index
        bpy.ops.paint.weight_paint_toggle()
        clock.stop("vis leaves")

    obj.select = True
    scene.objects.active = obj
    obj["is_tree"] = True
    obj["has_armature"] = True if scene.create_armature else False

    clock.stop("create_tree")
    print("\nDeveloper Info:")
    clock.display()
    if is_twig:
        return twig_leafs