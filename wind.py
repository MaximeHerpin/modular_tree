
import bpy
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix
import numpy as np
from collections import deque
from mathutils import Vector, Matrix
from math import sqrt, cos, sin, exp
from random import random


class Wind1:
    def __init__(self, armature_object):
        self.time = 0
        self.bones = armature_object.pose.bones
        self.n = len(self.bones)
        self.bone_sizes = np.zeros(self.n, dtype=np.float)
        self.bone_lengths = np.zeros(self.n, dtype=np.float)
        self.bone_lengths.shape = (self.n, 1)

        for i, b in enumerate(self.bones):
            self.bone_sizes[i] = b.bone.head_radius
            self.bone_lengths[i] = b.length

        inertia_moment = self.bone_lengths ** 2
        damping = np.ones(self.n, dtype=np.float) * 10
        damping.shape = (self.n, 1)
        self.stiffness = self.bone_sizes * 50
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
        self.time += 1
        wind_vector = np.array(wind_direction) * (1 + np.cos(self.time / 10) * random() / 4) * strength / 500
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

        # for i in range(self.n):
        #    matrices[i] = matrices[i].dot(rot_X[i])
        # matrices[i] = matrices[i].dot(np.array([list(i.to_tuple()) for i in list(Matrix.Rotation(true_angle[i,0], 4, 'X'))]))
        # matrices[i] = matrices[i].dot(np.array([list(i.to_tuple()) for i in list(Matrix.Rotation(angle[i,1] - memory[i,1], 4, 'Y'))]))
        # self.bones.foreach_set('matrix', matrices.ravel())
        self.bones.foreach_set('matrix',
                               np.einsum('hik,hkj->hij', np.einsum('hik,hkj->hij', matrices, rot_Z), rot_X).ravel())
        # bones.foreach_set('matrix', matrices.ravel())
        # bpy.ops.object.mode_set(mode='EDIT')
        # bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.frame_set(1)


class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Simple Modal Operator"


    _timer = None
    wind = None
    wind_object = None

    def modal(self, context, event):
        if event.type in {'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            # delta = self.first_mouse_x - event.mouse_x
            # context.object.location.x = self.first_value + delta * 0.01
            # numpy_wind(context.object)

            self.wind.step(self.wind_object.field.strength,
                           Matrix.Rotation(self.wind_object.rotation_euler.z, 3, 'Z') * Vector((1, 0, 0)))

        if event.type == 'NUMPAD_PLUS':
            self.strength += .1
        if event.type == 'NUMPAD_MINUS':
            self.strength -= .1

        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, context.window)
        wm.modal_handler_add(self)
        self.wind = Wind1(context.object)
        self.wind_object = context.scene.objects['Field']
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


# def compute_composite_body_forces(bone):
#     mass = bone.bone.tail_radius**2 * bone.length
#     center_of_mass =
#     if bone.parent is not None:



def general_solution_second_order(a, b, c, d, x0, x1, t):
    """solve linear diferential equation of second order ax'' + bx' + cx = d with x(0)=x0 and x'(0)=x1"""

    constant_sol = d / c

    delta = b ** 2 - 4 * a * c
    if delta > 0:
        r_delta = sqrt(delta)
        r1 = (-b - r_delta) / (2 * a)
        r2 = (-b + r_delta) / (2 * a)
        beta = (x1 - r1 * x0) / (r2 - r1)
        alpha = x0 - beta

        derived = r1 * alpha * exp(r1 * t) + r2 * beta * exp(r2 * t)
        return alpha * exp(r1 * t) + beta * exp(r2 * t) + constant_sol, derived

    else:
        s = sqrt(-delta) / (2 * a)
        r = -b / (2 * a)
        alpha = x0
        beta = (x1 - r * alpha) / s

        sol = exp(r * t) * (alpha * cos(s * t) + beta * sin(s * t)) + constant_sol
        derived = r * (sol - constant_sol) + exp(r * t) * (-alpha * s * sin(s * t) + beta * s * cos(s * t))
        return sol, derived


def register():
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(ModalOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.modal_operator('INVOKE_DEFAULT')
