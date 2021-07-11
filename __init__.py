# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
from pathlib import Path
from . import python_classes

VERSION_FILEPATH = os.path.join(Path(__file__).parent, "VERSION")


def get_version():
    with open(VERSION_FILEPATH, "r") as f:
        return tuple(int(i) for i in f.read().split("_"))


bl_info = {
    "name" : "Modular Tree",
    "author" : "Maxime",
    "description" : "create trees",
    "blender" : (2, 83, 0),
    "version" : get_version(),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}


# auto_load.init()

def register():
    python_classes.register()
    # auto_load.register()

def unregister():
    python_classes.unregister()
    # auto_load.unregister()
