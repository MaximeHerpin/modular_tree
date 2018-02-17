
import bpy
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix
import numpy as np
from collections import deque
from mathutils import Vector, Matrix
from math import sqrt, cos, sin, exp
from random import random


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
            self.bone_sizes[i] = b.bone.head_radius
            self.bone_lengths[i] = b.length
            self.stiffness[i] = b.bone.head_radius * 1000
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

    def step(self, strength=1, wind_direction=Vector((1, 0, 0))):
        wind_direction = Vector((0,1,0))
        self.time += 1
        wind_vector = np.array(wind_direction) * (1 + np.cos(self.time / 40) * random() / 4) * strength / 500
        t = 1 / 34
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
        #self.bones.foreach_set('matrix', np.einsum('hik,hkj->hij', np.einsum('hik,hkj->hij', matrices, rot_Z), rot_X).ravel())
        # bones.foreach_set('matrix', matrices.ravel())
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        #bpy.context.scene.update()
        #bpy.context.scene.frame_set(self.time)
        #bpy.context.scene.update()


class ModalWindOperator(bpy.types.Operator):
    """Start armature wind simulation"""
    bl_idname = "object.modal_wind_operator"
    bl_label = "Wind Operator"


    _timer = None
    wind = None
    wind_object = None

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            self.wind.step(self.wind_object.field.strength, Matrix.Rotation(self.wind_object.rotation_euler.z, 3, 'Z') * Vector((1, 0, 0)))

        return {'PASS_THROUGH'}

    def execute(self, context):
        print("wind")
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        self.wind = Wind(context.object)
        self.wind_object = context.scene.objects.get('Field')
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)


def register():
    bpy.utils.register_class(ModalWindOperator)


def unregister():
    bpy.utils.unregister_class(ModalWindOperator)


# if __name__ == "__main__":
#     register()
#     bpy.ops.object.modal_operator('INVOKE_DEFAULT')
