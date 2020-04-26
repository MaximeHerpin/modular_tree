import bpy


class MyCustomTree(bpy.types.NodeTree):
    bl_idname = "mt_MtreeNodeTree"
    bl_label = "Mtree"
    bl_icon = "ONIONSKIN_ON"