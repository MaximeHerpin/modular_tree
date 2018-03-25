import bpy
from math import pi
from mathutils import Euler
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty



def add_trunk_weight(obj, height, power=1.5):
    vg = obj.vertex_groups.get('base_trunk_displace')
    if vg is not None:
        obj.vertex_groups.remove(vg)

    vg = obj.vertex_groups.new("base_trunk_displace")
    verts = obj.data.vertices
    faces = obj.data.polygons
    verts_indexes = set()
    for f in faces:
        if f.center.z > height * 1.1:
            break

        for v in f.vertices:
            verts_indexes.add(v)

    for v in verts_indexes:
        weight = max(0, 1 - verts[v].co.z / height)**power
        vg.add([v], weight, 'REPLACE')


class TrunkDisplacement(Operator):
    """ adds a displace modifier and weight groups to the trunk base"""
    bl_idname = "mod_tree.trunk_displace"
    bl_label = " displace trunk"
    bl_options = {"REGISTER", "UNDO"}

    height = FloatProperty(min=.01, default=3)
    power = FloatProperty(min=0, default=1.5, name="weight shape")
    displace_strength = FloatProperty(default=2)

    pattern_type = EnumProperty(
        items=[('cloud', 'Cloud', ''), ('bands', 'Bands', '')],
        name="pattern_type",
        default="bands")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "height")
        layout.prop(self, "power")
        box = layout.box()
        box.prop(self, "pattern_type")
        box.prop(self, "displace_strength")

    def execute(self, context):
        obj = context.object
        message = None
        if obj is None:
            message = "no object selected"
        if obj.get("is_tree") is None:
            message = "no tree selected"
        elif obj["tree_type"] == "curve":
            message = "this operator only works on objects, not curves."
        if message is not None:
            self.report({'ERROR'}, message)
            return {'CANCELLED'}

        add_trunk_weight(obj, self.height, self.power)
        disp = obj.modifiers.new(type='DISPLACE', name='trunk displace')
        disp.vertex_group = "base_trunk_displace"

        if self.pattern_type == "cloud":
            tex = bpy.data.textures.new('trunk_base_disp', type='CLOUDS')
            tex.noise_scale = 3
            disp.mid_level = .4


        else:
            tex = bpy.data.textures.new('trunk_base_disp', type='WOOD')
            tex.wood_type = 'BANDNOISE'
            tex.noise_scale = 0.4
            tex.turbulence = 2
            empt = bpy.data.objects.new("empty", None)
            bpy.context.scene.objects.link(empt)
            empt.location = obj.location
            empt.scale = (4, 4, 4)
            empt.rotation_euler = Euler((-pi / 4, 0, 0), 'XYZ')
            disp.texture_coords = 'OBJECT'
            disp.texture_coords_object = empt
            disp.mid_level = 0

        disp.texture = tex
        disp.strength = self.displace_strength

        return {'FINISHED'}
