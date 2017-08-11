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


def create_system(ob, number, display, vertex_group, object_name, size, emitter=False, max_number=0):
    """ Creates a particle system

    Args:
        ob - (object) The object on which the particle system is created
        number - (int) The number of particles that will be rendered
        display - (int) The number of particles displayed on the viewport
        vertex_group - (vertex group) The vertex group controlling the density of particles
    """
    leaf = ob.modifiers.new("leafs", 'PARTICLE_SYSTEM')
    part = ob.particle_systems[0]

    settings = leaf.particle_system.settings
    settings.name = "leaf"
    settings.type = "HAIR"
    settings.use_advanced_hair = True
    settings.draw_percentage = 100 * display / number

    settings.use_rotation_dupli = True
    settings.use_rotations = True
    settings.particle_size = 0.1 * size
    settings.size_random = 0.25
    settings.brownian_factor = 1
    settings.render_type = "OBJECT"
    if bpy.data.objects.get(object_name) is not None:
        settings.dupli_object = bpy.context.scene.objects[object_name]

    if not emitter:
        g = vertex_group
        settings.count = number
        part.vertex_group_density = g.name
        settings.distribution = "RAND"
        bpy.data.particles["leaf"].rotation_mode = 'OB_Z'
        bpy.data.particles["leaf"].phase_factor_random = 2
        bpy.data.particles["leaf"].rotation_factor_random = 0.12
        settings.normal_factor = 0.250
        settings.factor_random = 0.7
        settings.use_render_emitter = False
        settings.phase_factor = 1
        settings.phase_factor_random = 1

    else:
        settings.count = min(number, max_number)
        settings.emit_from = 'FACE'
        settings.userjit = 1
        settings.rotation_mode = 'NOR'
        bpy.data.particles["leaf"].phase_factor = -.1
        settings.phase_factor_random = 0.2
        settings.phase_factor_random = 0.30303
        settings.factor_random = 0.2



