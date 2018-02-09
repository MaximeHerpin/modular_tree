import bpy
import numpy as np
from mathutils import Matrix, Vector
from math import pi, exp, atan, sqrt, cos, sin
from collections import deque
from random import random


def wind_function(position, time, strength, direction=Vector((1, 0, 0)), random_wind_strength=0):
    return direction * strength  # * (1-exp(-time/10)) #* (1 + .005*(random_wind_strength-.5))* (1+cos(2*pi*time/10)/80)


def wind(armature_object):
    print("-" * 50)
    bones = organize_bones(armature_object)
    n = len(bones)
    # for b in bones:
    #     b.matrix *= Matrix.Rotation(pi/20, 4, 'X')
    #
    #     armature_object.pose.update()


    original_directions = np.ones(3 * n, dtype=np.float)

    rotation_speed = np.zeros(2 * n, dtype=np.float)
    rotation_speed.shape = (n, 2)
    original_matrices = [b.matrix for b in bones]
    current_rotation = np.zeros(2 * n, dtype=np.float)
    current_rotation.shape = (n, 2)
    original_directions.shape = (n, 3)
    for i in range(len(bones)):
        original_directions[i] = [k for k in bones[i].y_axis.normalized().to_tuple()]

    for b in bones:
        b.rotation_mode = 'QUATERNION'
        b.keyframe_insert(data_path='rotation_quaternion', frame=0)

    wind_step(bones, original_matrices, current_rotation, rotation_speed)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')


def wind_step(bones, original_matrices, current_rotation, rotation_speed):
    for frame in range(100):
        random_wind_strength = random()
        for i, b in enumerate(bones):

            wind_vector = wind_function(b.tail, frame, .5, Vector((1, 0, 0)))

            base = b.matrix.to_3x3()
            i_base = base.inverted()
            bone_vector = (b.tail - b.head)

            inertia_moment = b.length ** 2
            damping = 5
            stiffness = (b.bone.head_radius) * 500

            torque = i_base * wind_vector.cross(bone_vector)  # / 7000 /(b.bone.head_radius)**2
            if b.parent is not None and len(b.parent.children) > 1:
                stiffness *= 2
                torque /= 3
            torque_x = torque.x
            torque_z = torque.z
            timestep = 1 / 175
            r0x, r1x = general_solution_second_order(inertia_moment, damping, stiffness, torque_x, current_rotation[i][0], rotation_speed[i][0], timestep)
            r0z, r1z = general_solution_second_order(inertia_moment, damping, stiffness, torque_z, current_rotation[i][0], rotation_speed[i][0], timestep)
            rx, rz = current_rotation[i]
            current_rotation[i] = (r0x, r0z)
            rotation_speed[i] = (r1x, r1z)

            # direction = compute_new_direction(Vector(original_directions[i]), bone_vector, wind_vector, Vector(bones_inertia[i]), effective_surface, stiffness, frame)
            # direction = wind_vector
            # angle = cos(frame/10 + random_phase[i]) * effective_surface/100
            # bones_inertia[i] = np.array(list(direction.to_tuple()))
            #
            # up = b.y_axis
            #
            # # print(base)
            #
            # axis = base.inverted() * up.cross(direction)
            # rot = Matrix.Rotation(angle, 4, axis)
            # b.matrix *= rot
            # b.rotation_mode = 'QUATERNION'

            b.matrix = original_matrices[i] * Matrix.Rotation(r0x - rx, 4, 'X') * Matrix.Rotation(r0z - rz, 4, 'Z')
            b.keyframe_insert(data_path='rotation_quaternion', frame=frame + 1)
            # bpy.context.scene.update()
        bpy.context.scene.update()


def wind_solver(bones, original_matrices, current_rotation, rotation_speed):
    for frame in range(100):
        random_wind_strength = random()
        for i, b in enumerate(bones):

            mass = (b.bone.head_radius) ** 2 * b.length
            barycenter = b.tail * mass
            for c in b.children:
                mass += c["mass"]
                barycenter += Vector(c["barycenter"])

            b["mass"] = mass
            b["barycenter"] = barycenter
            barycenter /= mass

            wind_vector = wind_function(b.tail, frame, .3, Vector((1, 0, 0)), random_wind_strength)

            base = b.matrix.to_3x3()
            i_base = base.inverted()
            bone_vector = barycenter - b.head

            inertia_moment = bone_vector.length ** 2 * mass / 10000
            damping = 0.5 * b.bone.head_radius
            stiffness = (b.bone.head_radius) ** 2 / b.length * 800
            torque = i_base * wind_vector.cross(bone_vector) / 7000 / (b.bone.head_radius) ** 2
            torque_x = torque.x
            print(torque_x)
            torque_z = torque.z
            timestep = 1 / 24
            r0x, r1x = general_solution_second_order(inertia_moment, damping, stiffness, torque_x, current_rotation[i][0], rotation_speed[i][0], timestep)
            r0z, r1z = general_solution_second_order(inertia_moment, damping, stiffness, torque_z, current_rotation[i][0], rotation_speed[i][0], timestep)
            # r0x = .001/b.bone.head_radius  + cos(2*pi*frame/200 * mass + mass)/(100 * b.bone.head_radius)
            rx, rz = current_rotation[i]
            current_rotation[i] = (r0x, r0z)
            rotation_speed[i] = (r1x, r1z)

            # direction = compute_new_direction(Vector(original_directions[i]), bone_vector, wind_vector, Vector(bones_inertia[i]), effective_surface, stiffness, frame)
            # direction = wind_vector
            # angle = cos(frame/10 + random_phase[i]) * effective_surface/100
            # bones_inertia[i] = np.array(list(direction.to_tuple()))
            #
            # up = b.y_axis
            #
            # # print(base)
            #
            # axis = base.inverted() * up.cross(direction)
            # rot = Matrix.Rotation(angle, 4, axis)
            # b.matrix *= rot
            # b.rotation_mode = 'QUATERNION'

            b.matrix = original_matrices[i] * Matrix.Rotation(r0x - rx, 4, 'X') * Matrix.Rotation(r0z - rz, 4, 'Z')
            b.keyframe_insert(data_path='rotation_quaternion', frame=frame + 1)
            # bpy.context.scene.update()
        bpy.context.scene.update()


def compute_new_direction(original_direction, current_direction, wind_vector, bone_inertia, effective_surface, stiffness):
    new_direction = current_direction + bone_inertia * 0 + wind_vector * effective_surface + (original_direction - current_direction) * stiffness
    new_direction = current_direction + wind_vector + (original_direction - current_direction) * stiffness
    new_direction = current_direction + wind_vector / effective_surface
    return new_direction


def getRoll(bone):
    mat = bone.matrix_local.to_3x3()
    quat = mat.to_quaternion()
    if abs(quat.w) < 1e-4:
        roll = pi
    else:
        roll = 2 * atan(quat.y / quat.w)
    return roll


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
        print('d>0')
        r_delta = sqrt(delta)
        r1 = (-b - r_delta) / (2 * a)
        r2 = (-b + r_delta) / (2 * a)
        beta = (x1 - r1 * x0) / (r2 - r1)
        alpha = x0 - beta

        derived = r1 * alpha * exp(r1 * t) + r2 * beta * exp(r2 * t)
        return alpha * exp(r1 * t) + beta * exp(r2 * t) + constant_sol, derived

    else:
        print('cos')
        s = sqrt(-delta)
        r = -b / (2 * a)
        alpha = x0
        beta = (x1 - r * alpha) / s

        sol = exp(r * t) * (alpha * cos(s * t) + beta * sin(s * t)) + constant_sol
        derived = r * (sol - constant_sol) + exp(r * t) * (-alpha * s * sin(s * t) + beta * s * cos(s * t))
        return sol, derived


def add_f_curve_modifiers(armature_object):
    strength = .1
    wind_vector = Vector((1, 0, 0)) * strength

    bones = organize_bones(armature_object)

    for b in bones:
        mass = (b.bone.head_radius) ** 2 * b.length
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

        inertia_moment = bone_vector.length ** 2 * mass / 10000
        damping = 0.5 * b.bone.head_radius
        stiffness = (b.bone.head_radius) ** 2 / b.length * 800
        if b.parent is not None and len(b.parent.children) > 1:
            stiffness *= 2
            torque /= 3
        else:
            torque = Vector((0, 0, 0))
        torque = i_base * wind_vector.cross(bone_vector) / b.bone.head_radius / 1000

        f = sqrt(abs(damping ** 2 - 4 * inertia_moment * stiffness)) / 10

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


# wind(bpy.context.object)
add_f_curve_modifiers(bpy.context.object)