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

import bpy


class SearchTree:
    def __init__(self, key, value, left=None, right=None, parent=None):
        self.key = key
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

    def add_rec(self, curr_node, coord, value):
        if coord == curr_node.key:
            curr_node.value += value

        if coord < curr_node.key:
            if curr_node.left is not None:
                self.add_rec(curr_node.left, coord, value)
            else:
                new_vox = SearchTree(coord, value)
                curr_node.left = new_vox

        elif coord > curr_node.key:
            if curr_node.right is not None:
                self.add_rec(curr_node.right, coord, value)
            else:
                new_vox = SearchTree(coord, value)
                curr_node.right = new_vox

    def add(self, coord, value):
        self.add_rec(self, coord, value)

    def get_value_rec(self, curr_node,  coord):
        if curr_node.key == coord:
            return curr_node.value

        if coord < curr_node.key:
            if not curr_node.left:
                return 0
            else:
                return self.get_value_rec(curr_node.left, coord)

        elif coord > curr_node.key:
            if not curr_node.right:
                return 0
            else:
                return self.get_value_rec(curr_node.right, coord)

    def get_value(self, coord):
        return self.get_value_rec(self, coord)

    def length_rec(self, curr_node):
        if self is None:
            return 0
        return 1 + self.length_rec(curr_node.left) + self.length_rec(curr_node.right)

    def prep_vis(self, coords, curr_node):
        if not (curr_node.left or curr_node.right):
            coords.append(curr_node.key)
        if curr_node.left is not None:
            coords.append(curr_node.key)
            self.prep_vis(coords, curr_node.left)
        if curr_node.right is not None:
            coords.append(curr_node.key)
            self.prep_vis(coords, curr_node.right)

    def create_vis(self, scale):
        coords = []
        self.prep_vis(coords, self)
        scene = bpy.context.scene
        spheres = []
        for coord in coords:
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, size=scale, location=coord)
            spheres.append(scene.objects.active)
        for ob in bpy.context.selected_objects:
            ob.select = False
        for ob in spheres:
            ob.select = True
        bpy.ops.object.join()
        bpy.ops.object.shade_smooth()

