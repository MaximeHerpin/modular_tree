
import bpy
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix
import numpy as np
from collections import deque
from mathutils import Vector, Matrix
import mathutils.noise
from math import sqrt, cos, sin, exp
from random import random
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty


def wind_f_curve(armature_object, strength, speed):
    fcurves = armature_object.animation_data
    if fcurves is not None:
        fcurves = fcurves.action.fcurves
        for f in fcurves:
            for m in f.modifiers:
                f.modifiers.remove(m)

    wind_vector = Vector((1,0,0))
    phase_offset = 0
    for i, b in enumerate(armature_object.pose.bones):
        b.rotation_mode = 'XYZ'
        b.keyframe_insert('rotation_euler', frame=0, index=0)
        b.keyframe_insert('rotation_euler', frame=0, index=2)
        if fcurves is None:
            fcurves =  armature_object.animation_data.action.fcurves

        i_base = b.matrix.to_3x3().inverted()
        bone_vector = b.tail - b.head
        torque = i_base @ wind_vector.cross(bone_vector) / 1000 / (.1+b.bone.tail_radius ** .5) * strength
        phase_multiplier = 1/(.1 + b.bone.tail_radius**2) / 50 * speed * strength
        phase_offset += bone_vector.length * b.bone.tail_radius / 2
        f0 = fcurves[2 * i]
        f1 = fcurves[2 * i + 1]
        m0 = f0.modifiers.new(type='FNGENERATOR')
        m1 = f1.modifiers.new(type='FNGENERATOR')
        m0.function_type = 'SIN'
        m1.function_type = 'SIN'
        m0.amplitude = torque.x
        m1.amplitude = torque.z
        m0.phase_multiplier = phase_multiplier
        m1.phase_multiplier = phase_multiplier
        m0.phase_offset = phase_offset
        m1.phase_offset = phase_offset
        m0.value_offset = torque.x * 2
        m1.value_offset = torque.z * 2

class FastWind(Operator):
    """Add a wind effect to an armature"""
    bl_idname = "mod_tree.fast_wind"
    bl_label = "Fast Wind"
    bl_options = {"REGISTER", "UNDO"}

    strength: FloatProperty(default=1)
    speed: FloatProperty(min=0, default=.5)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "strength")
        layout.prop(self, "speed")

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'ARMATURE':
            #add_f_curve_modifiers(obj, self.strength/5, self.speed)
            wind_f_curve(obj, self.strength, self.speed)
        else:
            self.report({'ERROR'}, "No armature object selected")
            return {'CANCELLED'}

        return {'FINISHED'}
