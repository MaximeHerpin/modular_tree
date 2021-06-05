import bpy
from ..base_types.socket import MtreeSocket

class MtreeFloatSocket(bpy.types.NodeSocket, MtreeSocket):
    bl_idname = 'mt_FloatSocket'
    bl_label = "Mtree Float Socket"

    color = (1.0, 0.4, 0.216, 0.5)


    min_value : bpy.props.FloatProperty(default = -float('inf'))
    max_value : bpy.props.FloatProperty(default = float('inf'))
    def update_value(self, context):
        self["property_value"] = max(self.min_value, min(self.max_value, self.property_value))
        mesher = self.node.get_mesher_rec()
        if mesher is not None:
            mesher.build_tree()
    property_value : bpy.props.FloatProperty(default = 0, update=update_value)


    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "property_value", text=text)
    
