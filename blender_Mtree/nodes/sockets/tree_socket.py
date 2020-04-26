import bpy
from ..base_types.socket import MtreeSocket

class TreeSocket(bpy.types.NodeSocket, MtreeSocket):
    bl_idname = 'mt_TreeSocket'
    bl_label = "Tree Socket"

    color = (.2,.7,.2,1)
    
    def draw(self, context, layout, node, text):
        layout.label(text=text)
    
