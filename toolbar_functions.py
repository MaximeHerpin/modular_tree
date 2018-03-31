import bpy
import os
from .tree_functions import create_twig
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


class Twigoperator(Operator):
    """create a branch with leafs"""
    bl_idname = "mod_tree.twig"
    bl_label = " Make Twig"
    bl_options = {"REGISTER", "UNDO"}

    seed = IntProperty(default=43)
    length = FloatProperty(min=.01, default=20)
    iterations = IntProperty(min=1, default=4)
    radius = FloatProperty(min=0.001, default=.4)
    randomness = FloatProperty(default=.4)
    split_proba = FloatProperty(min=0, max=1, default=.3)
    offset = IntProperty(min=0, default=5)
    gravity_strength = FloatProperty(default=.5)
    leaf_type = EnumProperty(
        items=[('palmate', 'Palmate', ''), ('serrate', 'Serrate', ''), ('palmatisate', 'Palmatisate', '')],
        name="leaf type",
        default="palmate")
    leaf_size = FloatProperty(min=0, default=1)
    leaf_proba = FloatProperty(min=0, max=1, default=.5)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "seed")
        layout.prop(self, "length")
        layout.prop(self, "iterations")
        layout.prop(self, "radius")
        layout.prop(self, "randomness")
        layout.prop(self, "split_proba")
        layout.prop(self, "offset")
        layout.prop(self, "gravity_strength")
        layout.prop(self, "leaf_type")
        layout.prop(self, "leaf_size")
        layout.prop(self, "leaf_proba")

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        leaf_path = os.path.dirname(__file__) + "/resources/materials.blend\\Object\\"
        material_path = os.path.dirname(__file__) + "/resources/materials.blend\\Material\\"

        if bpy.data.materials.get("twig") is None:
            bpy.ops.wm.append(filename="twig", directory=material_path)

        bpy.ops.wm.append(filename=self.leaf_type, directory=leaf_path)
        leaf_object = bpy.context.scene.objects.get(self.leaf_type)

        create_twig(random_seed=self.seed, length=self.length, iterations=self.iterations, randomness=self.randomness, radius=self.radius,
                    split_proba=self.split_proba, offset=self.offset, gravity_strength=self.gravity_strength,
                    particle_proba=self.leaf_proba, leaf=leaf_object, leaf_size=self.leaf_size * 20, material="twig")


        return {'FINISHED'}


class AppendMaterials(Operator):
    """Import Bark materials"""
    bl_idname = "mod_tree.bark_materials"
    bl_label = "Import Bark Materials"
    bl_options = {"REGISTER", "UNDO"}


    def draw(self, context):
        pass

    def execute(self, context):
        material_path = os.path.dirname(__file__) + "/resources/materials.blend\\Material\\"

        if bpy.data.materials.get("birch") is None:
            bpy.ops.wm.append(filename="birch", directory=material_path)
        if bpy.data.materials.get("oak") is None:
            bpy.ops.wm.append(filename="oak", directory=material_path)
        if bpy.data.materials.get("Pine") is None:
            bpy.ops.wm.append(filename="Pine", directory=material_path)
        if bpy.data.materials.get("Redwood") is None:
            bpy.ops.wm.append(filename="Redwood", directory=material_path)

        return {'FINISHED'}

