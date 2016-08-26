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


def create_system(ob, number, display, vertex_group):
    """ Creates a particle system

    Args:
        ob - (object) The object on which the particle system is created
        number - (int) The number of particles that will be rendered
        display - (int) The number of particles displayed on the viewport
        vertex_group - (vertex group) The vertex group controlling the density of particles
    """
    # get the vertex group
    g = vertex_group

    # customize the particle system
    leaf = ob.modifiers.new("psys name", 'PARTICLE_SYSTEM')
    part = ob.particle_systems[0]
    part.vertex_group_density = g.name
    settings = leaf.particle_system.settings
    settings.name = "leaf"
    settings.type = "HAIR"
    settings.use_advanced_hair = True
    settings.draw_percentage = 100 * display / number
    settings.count = number
    settings.distribution = "RAND"
    settings.normal_factor = 0.250
    settings.factor_random = 0.7
    settings.use_rotations = True
    settings.phase_factor = 1
    settings.phase_factor_random = 1
    settings.particle_size = 0.015
    settings.size_random = 0.25
    settings.brownian_factor = 1
    settings.render_type = "OBJECT"
