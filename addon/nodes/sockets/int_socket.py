import bpy
from ..base_types.socket import MtreeSocket

class MtreeIntSocket(bpy.types.NodeSocket, MtreeSocket):
    bl_idname = 'mt_IntSocket'
    bl_label = "Mtree Int Socket"

    color = (1.0, 0.4, 0.216, 0.5)


    min_value : bpy.props.IntProperty(default = -10**9)
    max_value : bpy.props.IntProperty(default = 10**9)
    def update_value(self, context):
        self["property_value"] = max(self.min_value, min(self.max_value, self.property_value))
        mesher = self.node.get_mesher()
        if mesher is not None:
            mesher.build_tree()
    property_value : bpy.props.IntProperty(default = 0, update=update_value)


    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "property_value", text=text)
    
