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

from os.path import join, dirname
from bpy.utils import previews

# global variables
ICONS = {'TREE'}
ICON_COLLECTION = {}


def register_icons():
    preview_coll = previews.new()
    icons_folder = join(dirname(__file__), "custom_icons")

    for icon in ICONS:
        preview_coll.load(icon, join(icons_folder, icon + ".png"), 'IMAGE')

    ICON_COLLECTION["main"] = preview_coll


def unregister_icons():
    for collection in ICON_COLLECTION.values():
        previews.remove(collection)
    ICON_COLLECTION.clear()


def get_icon(icon):
    preview_coll = ICON_COLLECTION["main"]
    return preview_coll[icon].icon_id
