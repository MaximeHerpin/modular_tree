import bpy


class MtreeSocket:

    is_property : bpy.props.BoolProperty(default=True)
    property_name : bpy.props.StringProperty()
    property_value : None
    color : (.5,.5,.5,1)
    
    def draw_color(self, context, node):
        return self.color
