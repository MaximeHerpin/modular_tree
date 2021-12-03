import os
from pathlib import Path
import bpy

MTREE_RESOURCE_DIR = (Path(__file__).parent.parent.parent / "resources").resolve()

class ResourceUtils:

    geo_nodes_dir = os.path.join(MTREE_RESOURCE_DIR, "geo_node")

    @classmethod
    def append_geo_node(cls, name:str):
        group = bpy.data.node_groups.get(name, None)

        if group is None:
            directory = os.path.join(cls.geo_nodes_dir, "geo_nodes_2_93.blend", "NodeTree")
            filepath = os.path.join(directory, name)
            bpy.ops.wm.append(filepath=filepath,filename=name,directory=directory, autoselect=False)
            group = bpy.data.node_groups[name]

        return group