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

import os

import bpy
from bpy.types import Operator, Panel, Scene, Menu, AddonPreferences
import mathutils

from .prep_manager import save_everything
from .logo import display_logo


class WindOperator(Operator):
    """Make a tree"""
    bl_idname = "mod_tree.animate_wind"
    bl_label = "Animate Wind"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # this block saves everything and cancels operator if something goes wrong
        display_logo()
        messages, message_lvls, status = save_everything()
        for i, message in enumerate(messages):
            self.report({message_lvls[i]}, message)
            return {status}

        mtree_props = context.scene.mtree_props

        # check for control object and terrain
        if not mtree_props.terrain:
            self.report({'ERROR'}, "Missing terrain object!")
            return {'CANCELLED'}
        if not mtree_props.wind_controller:
            self.report({'ERROR'}, "Missing control object!")
            return {'CANCELLED'}

        try:
            wind_texture = bpy.data.textures["TreeWind"]
        except KeyError:
            wind_texture = bpy.data.textures.new("TreeWind", 'CLOUDS')
            # change default settings
            wind_texture.use_color_ramp = True
            wind_texture.noise_scale = 5
            # set up color ramp
            ramp = wind_texture.color_ramp
            ramp.color_mode = 'HSV'
            ramp.hue_interpolation = 'CW'
            ramp.elements[0].color = mathutils.Vector((1, 0, 0, 1))
            ramp.elements[1].color = mathutils.Vector((0, 1, 0, 1))

        for obj in bpy.context.selected_objects:
            bpy.context.scene.objects.active = obj
            try:
                if obj['is_tree']:
                    if "wind_anim" not in obj.vertex_groups:
                        wind_group = obj.vertex_groups.new("wind_anim")
                    else:
                        wind_group = obj.vertex_groups["wind_anim"]
                else:
                    print("Not a tree:", obj)
                    continue

            except KeyError:
                print("Not a tree:", obj)
                continue

            wind_group.add([i for i in range(len(obj.data.vertices))], 1.0, "REPLACE")

            if mtree_props.clear_mods:
                # remove all modifiers
                [obj.modifiers.remove(m) for m in obj.modifiers]

            orig_mods_len = len(obj.modifiers)

            # setup vertex weighting modifier
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
            vwp = obj.modifiers[orig_mods_len]  # this is an index so if len(0), [0] will be correct
            vwp.vertex_group = wind_group.name
            vwp.target = bpy.data.objects[mtree_props.terrain]
            vwp.min_dist = mtree_props.wind_height_start
            vwp.max_dist = mtree_props.wind_height_full
            vwp.proximity_mode = 'GEOMETRY'
            vwp.proximity_geometry = {'FACE'}

            # setup displace modifier
            bpy.ops.object.modifier_add(type='DISPLACE')
            displace = obj.modifiers[orig_mods_len + 1]
            displace.texture_coords = 'OBJECT'
            displace.texture_coords_object = bpy.data.objects[mtree_props.wind_controller]
            displace.direction = 'RGB_TO_XYZ'
            displace.strength = mtree_props.wind_strength
            displace.texture = bpy.data.textures[wind_texture.name]
            displace.vertex_group = wind_group.name

        return {'FINISHED'}


class SetupTerrainOperator(Operator):
    """Builds terrain"""
    bl_idname = "mod_tree.build_terrain"
    bl_label = "Build Terrain"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # add a plane

        # add modifiers (subdivision, displace)

        # add a particle system
        # - enable use mod stack
        # - use hair
        # - set group to forest group

        return {'FINISHED'}


def append_objs(path, prefix="", suffix="", case_sens=False, ignore="IGNORE"):
    """Appends all objects into scene from .blend if they meet argument criteria."""

    scene = bpy.context.scene

    with bpy.data.libraries.load(path) as (data_from, data_to):
        if not case_sens:
            data_to.objects = [name for name in data_from.objects if
                               name.lower().startswith(prefix.lower()) and name.lower().endswith(suffix.lower()) and ignore.upper() not in name.upper()]
        else:
            data_to.objects = [name for name in data_from.objects if name.startswith(prefix) and name.endswith(suffix) and ignore.upper() not in name.upper()]

    for obj in data_to.objects:
        if obj is not None:
            scene.objects.link(obj)


class MakeControllerOperator(Operator):
    """Makes controller"""
    bl_idname = "mod_tree.make_wind_controller"
    bl_label = "Make Wind Controller"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tiles_path = os.path.join(os.path.dirname(__file__), "wind_anim", "wind_controller.blend")
        append_objs(tiles_path)

        return {'FINISHED'}


class MakeTerrainOperator(Operator):
    """Makes controller"""
    bl_idname = "mod_tree.make_terrain"
    bl_label = "Make Terrain"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tiles_path = os.path.join(os.path.dirname(__file__), "wind_anim", "terrain.blend")
        append_objs(tiles_path)

        return {'FINISHED'}
