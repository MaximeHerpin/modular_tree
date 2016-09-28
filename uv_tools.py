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
from math import radians, cos, sin

import bpy
import bmesh
from collections import defaultdict


def rotate():
    """After automatic unwrap, the uv islands are not correctly oriented, this function corrects it by rotating them accordingly."""
    bpy.ops.object.mode_set(mode='EDIT')
    make_islands = MakeIslands()
    bm = make_islands.get_bm()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    sel_islands = make_islands.selected_islands()

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
            x1 += 0.25 * f0.loops[i][bm.loops.layers.uv.active].uv.x
            x2 += 0.25 * f1.loops[i][bm.loops.layers.uv.active].uv.x
            y1 += 0.25 * f0.loops[i][bm.loops.layers.uv.active].uv.y
            y2 += 0.25 * f1.loops[i][bm.loops.layers.uv.active].uv.y

        if (abs(x2 - x1) < abs(y2 - y1)) and (len(island) % 8 == 0):
            make_islands.rotate_island(island, 90)

    bpy.ops.uv.pack_islands(rotate=False, margin=0.001)
    bpy.ops.object.mode_set(mode='OBJECT')


def add_seams(indexes, seams):
    """Takes a list of indexes and couples them

    Args:
        indexes - (list of int)
        seams - (list of (int, int))
    """
    n = len(indexes)
    for i in range(n):
        seams.append((indexes[i], indexes[(i + 1) % n]))


# This part is heavily inspired by the "UV Align\Distribute" addon made by Rebellion (Luca Carella)
class MakeIslands:
    """TODO - Summary

    Methods:
        __init__ - TODO: this can be a copy of the method's summary
        add_to_island - TODO
        get_islands - TODO
        active_island - TODO
        selected_islands - TODO
    """
    def __init__(self):
        self.uvlayer = None
        self.bm = None
        self.initbmesh()
        self.face_to_verts = defaultdict(set)
        self.vert_to_faces = defaultdict(set)
        self.selectedIsland = set()
        for face in self.bm.faces:
            for loop in face.loops:
                if not self.uvlayer:
                    continue
                assert self.uvlayer is not None

                ind = '{0[0]:.5} {0[1]:.5} {1}'.format(loop[self.uvlayer].uv, loop.vert.index)
                self.face_to_verts[face.index].add(ind)
                self.vert_to_faces[ind].add(face.index)
                if face.select:
                    if loop[self.uvlayer].select:
                        self.selectedIsland.add(face.index)

        self.islands = []
        self.faces_left = set(self.face_to_verts.keys())
        while len(self.faces_left) > 0:
            face_id = self.faces_left.pop()
            self.current_island = []
            self.add_to_island(face_id)
            self.islands.append(self.current_island)

    def initbmesh(self):
        self.bm = bmesh.from_edit_mesh(bpy.context.edit_object.data)
        self.uvlayer = self.bm.loops.layers.uv.active
        if not self.uvlayer:
            print("THERE ARE NO UVLAYERS FOR THIS LOOP!")

    def add_to_island(self, face_id):
        """TODO - Summary

        Args:
            face_id - TODO
        """
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

    def selected_islands(self):
        """TODO - Summary

        Returns:
            _selectedIslands - TODO
        """

        _selectedIslands = []
        for island in self.islands:
            if not self.selectedIsland.isdisjoint(island):
                _selectedIslands.append(island)
        return _selectedIslands

    def b_box_center(self, island):
        min_x = 1000
        min_y = 1000
        max_x = -1000
        max_y = -1000

        for face_id in island:
            face = self.bm.faces[face_id]
            for loop in face.loops:
                min_x = min(loop[self.uvlayer].uv.x, min_x)
                min_y = min(loop[self.uvlayer].uv.y, min_y)
                max_x = max(loop[self.uvlayer].uv.x, max_x)
                max_y = max(loop[self.uvlayer].uv.y, max_y)

        return (Vector((min_x, min_y)) + Vector((max_x, max_y))) / 2

    def rotate_island(self, island, angle):
        rad = radians(angle)
        center = self.b_box_center(island)
        for face_id in island:
            face = self.bm.faces[face_id]
            for loop in face.loops:
                x = loop[self.bm.loops.layers.uv.active].uv.x
                y = loop[self.bm.loops.layers.uv.active].uv.y
                xt = x - center.x
                yt = y - center.y
                xr = (xt * cos(rad)) - (yt * sin(rad))
                yr = (xt * sin(rad)) + (yt * cos(rad))
                loop[self.bm.loops.layers.uv.active].uv.x = xr + center.x
                loop[self.bm.loops.layers.uv.active].uv.y = yr + center.y

    def get_bm(self):
        return self.bm


