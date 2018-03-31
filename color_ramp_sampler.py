import bpy
import bgl


def get_viewport():
    view = bgl.Buffer(bgl.GL_INT, 4)
    bgl.glGetIntegerv(bgl.GL_VIEWPORT, view)
    return view


def s2lin(color):
    a = 0.055
    new_color = []
    for x in color:
        if x <= 0.04045:
            x *= 1 / 12.92
        else:
            x = ((x + a) / (1 + a)) ** 2.4

        new_color.append(x)
    return new_color


def add_colors_to_ramp(colors, color_ramp):


        # color_ramp = bpy.data.materials['oak'].node_tree.nodes.active.color_ramp
    elements = color_ramp.elements
    for i in range(len(elements) - 1):
        elements.remove(elements[-1])
    elements = color_ramp.elements
    elements[0].position = 0
    for i in range(len(colors) - 1):
        elements.new(position=(i + 1) / len(colors))

    elements = color_ramp.elements
    for i, c in enumerate(colors):
        c = s2lin(c)
        elements[i].color = (c[0], c[1], c[2], 1)


def draw_callback_px(self, context):
    if self.moves % 3 == 0 and len(self.colors) < 32:
        self.mouse_path.append(self.mouse_pos)
        view = get_viewport()
        x, y = self.mouse_pos
        c = bgl.Buffer(bgl.GL_FLOAT, 4)
        bgl.glReadPixels(x + view[0], y + view[1], 1, 1, bgl.GL_RGB, bgl.GL_FLOAT, c)
        self.colors.append(c.to_list())

    # 50% alpha, 2 pixel width line

    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(1, 1, 1, 0.5)
    bgl.glLineWidth(4)

    bgl.glBegin(bgl.GL_LINE_STRIP)
    for x, y in self.mouse_path:
        bgl.glVertex2i(x, y)

    bgl.glEnd()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


class ColorRampSampler(bpy.types.Operator):
    """sample colors from cursor to color ramp"""
    bl_idname = "mod_tree.color_ramp_sampler"
    bl_label = "Color Ramp Sampler"

    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            self.drawing = True

        elif event.type == 'MOUSEMOVE':
            self.mouse_pos = (event.mouse_region_x, event.mouse_region_y)
            if self.drawing:
                self.moves += 1

        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
            add_colors_to_ramp(self.colors, self.node)
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):

        args = (self, bpy.context)
        self.drawing = False
        self._handle = bpy.types.SpaceImageEditor.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        self.colors = []
        self.mouse_pos = None
        self.moves = 2
        self.mouse_path = []

        try:
            self.node = bpy.context.active_object.active_material.node_tree.nodes.active.color_ramp
        except:
            self.report({'ERROR'}, "no color ramp selected")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


class ColorRampPanel(bpy.types.Panel):
    bl_label = "Color ramp sampler panel"
    bl_idname = "mod_tree.color_ramp_panel"
    bl_space_type = 'IMAGE_EDITOR'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = 'Tree'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mod_tree.color_ramp_sampler", icon="COLOR")
