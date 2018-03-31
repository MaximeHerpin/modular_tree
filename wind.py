
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


class Wind:
    def __init__(self, armature_object):
        self.time = 0
        self.bones = armature_object.pose.bones
        self.n = len(self.bones)
        self.bone_sizes = np.zeros(self.n, dtype=np.float)
        self.bone_lengths = np.zeros(self.n, dtype=np.float)
        self.bone_lengths.shape = (self.n, 1)
        self.stiffness = np.zeros(self.n, dtype=np.float)
        for i, b in enumerate(self.bones):
            self.bone_sizes[i] = b.bone.tail_radius
            self.bone_lengths[i] = b.length
            self.stiffness[i] = b.bone.tail_radius * 1000
            if b.parent is not None and len(b.parent.children) > 1:
                self.stiffness[i] *= 3

        inertia_moment = self.bone_lengths ** 2
        damping = np.ones(self.n, dtype=np.float) * 10
        damping.shape = (self.n, 1)
        #self.stiffness = self.bone_sizes * 100
        self.stiffness[0] *= 10
        self.stiffness.shape = (self.n, 1)

        self.s = np.sqrt(np.abs(damping ** 2 - 4 * inertia_moment * self.stiffness)) / (2 * inertia_moment)
        self.r = - damping / (2 * inertia_moment)

        self.original_matrices = np.zeros(self.n * 16, dtype=np.float)
        self.bones.foreach_get('matrix', self.original_matrices)

        self.current_rotations = np.zeros(self.n * 2, dtype=np.float)
        self.current_speeds = np.zeros(self.n * 2, dtype=np.float)
        self.current_rotations.shape = (self.n, 2)
        self.current_speeds.shape = (self.n, 2)

    def step(self, strength=1, wind_direction=Vector((1, 0, 0)), turbulence=.5):
        # wind_direction = Vector((0,1,0))
        self.time += 1
        # wind_vector = np.array(wind_direction) * (1 + np.cos(self.time / 40) * random() / 4) * strength / 500
        turbulence_vect = mathutils.noise.turbulence_vector(Vector((.05,0,0))*self.time, 2, False)
        wind_vector = (np.array(wind_direction) + turbulence * .5 * turbulence_vect) * strength * .01
        t = 1 / 54
        matrices = np.zeros(self.n * 16, dtype=np.float)
        self.bones.foreach_get('matrix', matrices)
        matrices.shape = (self.n, 4, 4)
        i_base = np.linalg.inv(matrices[:, :3, :3])
        bone_vect = matrices[:, :3, 1] * self.bone_lengths
        torque = np.einsum('ijk,ik->ij', i_base, np.cross(wind_vector, bone_vect))[:, 0:3:2]

        # torque +=.01
        torque.shape = (self.n, 2)
        alpha = self.current_rotations
        beta = (self.current_speeds - self.r * alpha) / self.s
        memory = self.current_rotations.copy()
        angle = np.exp(self.r * t) * (alpha * np.cos(self.s * t) + beta * np.sin(self.s * t)) + torque / self.stiffness
        # angle -= memory
        true_angle = angle - memory
        self.current_rotations = angle
        self.current_speeds = self.r * (angle - torque) + np.exp(self.r * t) * (
            -alpha * self.s * np.sin(self.s * t) + beta * self.s * np.cos(self.s * t))

        Cos = np.cos(true_angle)
        Sin = np.sin(true_angle)
        rot_X_cos = np.tile([0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 0], self.n)
        rot_X_sin = np.tile([0, 0, 0, 0, 0, 0, -1.0, 0, 0, 1.0, 0, 0, 0, 0, 0, 0], self.n)
        rot_X_cos.shape = (self.n, 16)
        rot_X_cos *= Cos[:, 0].reshape(self.n, 1)
        rot_X_sin.shape = (self.n, 16)
        rot_X_sin *= Sin[:, 0].reshape(self.n, 1)
        diag = np.tile([1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0], self.n)
        diag.shape = (self.n, 16)
        rot_X = rot_X_cos + rot_X_sin + diag
        rot_X.shape = (self.n, 4, 4)

        rot_Z_cos = np.tile([1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 0], self.n)
        rot_Z_sin = np.tile([0, 0, 1.0, 0, 0, 0, 0, 0, -1.0, 0, 0, 0, 0, 0, 0, 0], self.n)
        rot_Z_cos.shape = (self.n, 16)
        rot_Z_cos *= Cos[:, 1].reshape(self.n, 1)
        rot_Z_sin.shape = (self.n, 16)
        rot_Z_sin *= Sin[:, 1].reshape(self.n, 1)
        diag = np.tile([0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1.0], self.n)
        diag.shape = (self.n, 16)
        rot_Z = rot_Z_cos + rot_Z_sin + diag
        rot_Z.shape = (self.n, 4, 4)

        for i in range(self.n):
            #matrices[i] = matrices[i].dot(rot_X[i])
            #matrices[i] = matrices[i].dot(rot_Z[i])
            matrices[i] = matrices[i].dot(np.array([list(i.to_tuple()) for i in list(Matrix.Rotation(true_angle[i,0], 4, 'X'))]))
            matrices[i] = matrices[i].dot(np.array([list(i.to_tuple()) for i in list(Matrix.Rotation(true_angle[i,1], 4, 'Y'))]))
        self.bones.foreach_set('matrix', matrices.ravel())
        # self.bones.foreach_set('matrix', np.einsum('hik,hkj->hij', np.einsum('hik,hkj->hij', matrices, rot_Z), rot_X).ravel())
        # self.bones.foreach_set('matrix', matrices.ravel())
        # bpy.ops.object.mode_set(mode='EDIT')
        # bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.context.scene.update()
        # bpy.context.scene.frame_set(self.time)


        #bpy.context.scene.update()


class ModalWindOperator(bpy.types.Operator):
    """Start armature wind simulation"""
    bl_idname = "mod_tree.modal_wind_operator"
    bl_label = "Wind Operator"


    _timer = None
    wind = None
    wind_object = None
    turbulence = FloatProperty(default=.5)
    armature = None

    wind_rotation = FloatProperty(default=0)


    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # bpy.context.scene.frame_set(self.time)
            try:
                self.wind.step(self.wind_object.scale[0], Matrix.Rotation(self.wind_object.rotation_euler.z + self.wind_rotation, 3, 'Z') * Vector((1, 0, 0)), 1)
            except:
                self.cancel(context)
                self.report({'ERROR'}, "Select the controller object, and then the armature object")
                return {'CANCELLED'}
            ob = bpy.context.object
            self.armature.select = True
            bpy.context.scene.objects.active = self.armature
            bpy.ops.object.convert(target='MESH')
            self.armature.select = False
            bpy.context.scene.objects.active = ob
            ob.select = True

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("wind")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        self.armature = bpy.context.object
        if self.armature is None:
            # self.report({'ERROR'}, "no armature selected")
            self.cancel(context)
            return {'CANCELLED'}

        self.wind = Wind(context.object)
        try:
            self.wind_object = [i for i in context.selected_objects if i != self.armature][0]
            # self.wind_object = context.scene.objects.get('Field')
        except:
            self.cancel(context)
            self.report({'ERROR'}, "Select the controller object, and then the armature object")
            return {'CANCELLED'}

        wm.modal_handler_add(self)

        # if self.wind_object is None:


        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def organize_bones(armature_object):
    bones = deque()
    organize_bones_rec(armature_object.pose.bones[0], bones)
    return list(reversed(bones))


def organize_bones_rec(bone, bones):
    bones.append(bone)
    for child in bone.children:
        organize_bones_rec(child, bones)


def add_f_curve_modifiers(armature_object, strength, speed):
    wind_vector = Vector((1, 0, 0)) * strength

    fcurves = armature_object.animation_data.action.fcurves
    for f in fcurves:
        for m in f.modifiers:
            f.modifiers.remove(m)

    bones = organize_bones(armature_object)

    for b in bones:
        mass = b.bone.tail_radius ** 2 * b.length
        barycenter = b.tail * mass
        for c in b.children:
            mass += c["mass"]
            barycenter += Vector(c["barycenter"])
        b["mass"] = mass
        b["barycenter"] = barycenter
        barycenter /= mass

        b.rotation_mode = 'XYZ'
        b.keyframe_insert('rotation_euler', frame=0, index=0)
        b.keyframe_insert('rotation_euler', frame=0, index=2)

    fcurves = armature_object.animation_data.action.fcurves


    for i in range(len(bones)):
        f0 = fcurves[2 * i]
        f1 = fcurves[2 * i + 1]
        b = bones[i]

        i_base = b.matrix.to_3x3().inverted()
        bone_vector = b.tail - b.head

        inertia_moment = bone_vector.length ** 2 * bones[i]["mass"] / 10000
        damping = 0.5 * b.bone.tail_radius
        stiffness = b.bone.tail_radius ** 2 / b.length * 800
        if b.parent is not None and len(b.parent.children) > 1:
            stiffness *= 2
            # torque /= 3
        # else:
        #     torque = Vector((0, 0, 0))
        torque = i_base * wind_vector.cross(bone_vector) / (b.bone.tail_radius) / 1000

        f = sqrt(abs(damping ** 2 - 4 * inertia_moment * stiffness)) / (5*b.bone.tail_radius) * speed

        x_amplitude = torque.x
        z_amplitude = torque.z

        m0 = f0.modifiers.new(type='FNGENERATOR')
        m1 = f1.modifiers.new(type='FNGENERATOR')
        m0.function_type = 'SIN'
        m1.function_type = 'SIN'
        m0.amplitude = x_amplitude
        m1.amplitude = z_amplitude
        m0.phase_multiplier = f
        m1.phase_multiplier = f
        m0.value_offset = x_amplitude * 3
        m1.value_offset = z_amplitude * 3


class FastWind(Operator):
    """makes a tree from a node group"""
    bl_idname = "mod_tree.fast_wind"
    bl_label = "Fast Wind"
    bl_options = {"REGISTER", "UNDO"}

    strength = FloatProperty(default=1)
    speed = FloatProperty(min=0, default=.5)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "strength")
        layout.prop(self, "speed")

    def execute(self, context):
        obj = bpy.context.object
        if obj is not None and obj.type == 'ARMATURE':
            add_f_curve_modifiers(obj, self.strength/5, self.speed)
        else:
            self.report({'ERROR'}, "No armature object selected")
            return {'CANCELLED'}

        return {'FINISHED'}