from collections import deque

from random import random, seed
from math import pi, sqrt, cos, sin, atan
from mathutils import Vector, Matrix

import bpy
import bmesh
from bpy.types import Operator
from bpy.props import IntProperty, BoolProperty

from .modules import Root, Split, Branch, draw_module, square
from .grease_pencil import build_tree_from_strokes


def get_pruning_key(position, resolution=2):
    result = []
    for x in position.to_tuple():
        result.append(int(x*resolution) / 2)
    return tuple(result)


def grow(root, iterations, min_radius, limit_method, branch_length, split_proba, split_angle, split_deviation,
         split_radius, radius_decrease, randomness, spin, spin_randomness, creator, selection, gravity_strength,
         pruning_strength, shape_factor, up_attraction, kill_below_0=True):
    density_dict = root.density_dict
    extremities = []
    root.get_extremities_rec(extremities, selection)
    iteration = 0
    if limit_method == "iterations":
        condition = iteration < iterations
    elif limit_method == "radius":
        condition = True
    else:
        condition = False

    while condition:
        iteration += 1
        new_extremities = []
        for module, head in extremities:
            key = get_pruning_key(module.position)
            if key not in density_dict:
                density_dict[key] = 0.0
            dist_from_axis = (module.position - root.position).xy.length
            if random()*(pruning_strength*density_dict[key] + dist_from_axis/30 * shape_factor - module.direction.z*up_attraction) < 1 \
                    and (not kill_below_0 or module.position.z >= 0):
                radius = module.head_1_radius if head == 0 else module.head_2_radius
                if not (limit_method == "radius" and radius < min_radius):
                    position = module.get_head_pos(head)
                    direction = module.get_head_direction(head) + Vector((random()-.5, random()-.5, random()-.5))*randomness
                    direction.normalize()
                    if gravity_strength !=0:
                        direction += Vector((0, 0, -.1)) * gravity_strength
                        direction.normalize()
                    choice = random()
                    if choice < split_proba:
                        new_module = Split(position, direction,
                                           radius, resolution=0, head_2_length=radius*3, spin=module.spin + spin*pi/180)
                        new_module.head_1_length = branch_length
                        new_module.primary_angle = split_deviation
                        new_module.secondary_angle = split_angle*pi/180
                        new_module.head_1_radius = radius_decrease * radius
                        new_module.head_2_radius = split_radius * radius
                    else:
                        new_module = Branch(position, direction,
                                            radius, branch_length, radius_decrease, resolution=0,
                                            spin=module.spin + (random()-.5) * spin_randomness)

                    new_module.creator = creator

                    if head == 0:
                        module.head_module_1 = new_module
                    else:
                        module.head_module_2 = new_module
                    new_extremities.append((new_module, 0))
                    if new_module.type == 'split':
                        new_extremities.append((new_module, 1))

                    density_dict[key] += sqrt(new_module.base_radius)

        if iteration > iterations and limit_method == 'iterations':
            condition = False

        extremities = new_extremities

        if len(extremities) == 0:
            condition = False


def add_basic_trunk(radius, radius_decrease, randomness, up_attraction, twist, height, branch_length, horizontal=False):
    direction = Vector((1, 0, 0)) if horizontal else Vector((0, 0, 1))
    root = Root(position=Vector((0,0,0)), direction=direction, radius=radius, resolution=0)
    extremity = root
    while extremity.position.length < height:
        direction = (extremity.direction + Vector((random()-.5, random()-.5, random()-.5)) * randomness + direction * up_attraction).normalized()
        new_module = Branch(extremity.get_head_pos(0), direction, extremity.head_1_radius, branch_length, radius_decrease, resolution=0, spin=extremity.spin + twist)
        extremity.head_module_1 = new_module
        extremity = new_module
    return root


def add_splits(root, proba, selection, creator, split_angle, spin, head_size, offset, constraint_z=False):
    add_splits_rec(root.head_module_1, root, 0, proba, selection, creator, split_angle, spin, root.spin, head_size, offset, offset, constraint_z)


def add_splits_rec(module, parent_module, head, proba, selection, creator, split_angle, spin, curr_spin, head_size, curr_offset, original_offset, constraint_z):
    if module is not None:
        is_selected = curr_offset <= 0 and (selection == [] or module.creator in selection)
        if module.type == 'branch' and parent_module.head_module_1 is not None and random() < proba and is_selected:
            curr_spin += spin
            if constraint_z:
                curr_spin = -90 + int(random() < .5) * 180
            split = Split(module.position, module.direction, module.base_radius, module.resolution,
                          module.starting_index, curr_spin, head_2_length=module.base_radius*2,
                          head_2_radius=head_size)
            split.primary_angle = 0
            split.secondary_angle = split_angle*pi/180
            split.head_1_length = module.base_radius
            split.creator = creator
            child = module.head_module_1
            for i in range(int(split.head_2_radius / module.base_radius +.5)):
                if child is not None and child.type == 'branch':
                    child = child.head_module_1
                else:
                    break
            split.head_module_1 = child
            if head == 0:
                parent_module.head_module_1 = split
            else:
                parent_module.head_module_2 = split
            add_splits_rec(split.head_module_1, module, 0, proba, selection, creator, split_angle, spin, curr_spin,
                           head_size, max(0, curr_offset-1), original_offset, constraint_z)

        else:
            add_splits_rec(module.head_module_1, module, 0, proba, selection, creator, split_angle, spin, curr_spin,
                           head_size, max(0, curr_offset - 1), original_offset, constraint_z)
            if module.type == 'split':
                add_splits_rec(module.head_module_2, module, 1, proba, selection, creator, split_angle, spin, curr_spin,
                               head_size, original_offset, original_offset, constraint_z)


def add_armature(root, min_radius, min_dist):
    amt = bpy.data.armatures.new('MyRigData')
    rig = bpy.data.objects.new('MyRig', amt)
    rig.location = Vector((0, 0, 0))
    rig.show_x_ray = True
    # amt.show_names = True
    # Link object to scene
    scene = bpy.context.scene
    scene.objects.link(rig)
    scene.objects.active = rig
    scene.update()

    bpy.ops.object.mode_set(mode='EDIT')

    add_bone_rec(root, amt, min_radius, None, min_dist)

    bpy.ops.object.mode_set(mode='OBJECT')
    return rig


def add_bone_rec(module, amt, min_radius, parent, min_dist):
    if module.base_radius >= min_radius:
        if module.head_module_1 is not None:
            bone = amt.edit_bones.new('branch' + str(module.position.to_tuple()))
            bone.tail_radius = module.base_radius
            bone.head = module.position
            dist = (module.head_module_1.position - module.position).length
            if dist == 0:
                dist = 1
                print(module.type)
            child = module.head_module_1
            for i in range(int(0.5 + min_dist/dist)):
                if child is not None and child.head_module_1 is not None and child.type == 'branch':
                    child = child.head_module_1
                else:
                    break


            bone.tail = module.head_module_1.position

            if parent is not None:
                bone.parent = parent
                bone.use_connect = True

            add_bone_rec(child, amt, min_radius, bone, min_dist)

        if module.head_module_2 is not None:
            add_bone_rec(module.head_module_2, amt, min_radius, parent, min_dist)


def add_particles_emitter(root, max_radius, proba, dupli_object, size=1, ends_only=True):
    mesh = bpy.data.meshes.new("tree_leaves_emitter")
    bm = bmesh.new()
    bm.from_mesh(mesh)

    verts = deque()
    weights = deque()

    density_dict = root.density_dict
    add_emitters_rec(root, max_radius, verts, proba, weights, density_dict, ends_only)

    verts = list(verts)
    weights = list(weights)

    for v in verts:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    for i in range(int(len(verts)/4)):
        try:
            bm.faces.new([bm.verts[j] for j in range(i*4, i*4+4)])
        except:
            print('unable to create face')

    bm.faces.ensure_lookup_table()

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("tree_leaves_emitter", mesh)
    obj.location = bpy.context.scene.cursor_location
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    vg = obj.vertex_groups.new("leaves")
    for i in range(len(verts)):
        vg.add([i], weights[i//4], "ADD")
    create_particle_system(obj, len(verts)/4, vg, dupli_object, size)
    return obj


def add_emitters_rec(module, max_radius, verts, proba, weights, density_dict, ends_only):
    if module.base_radius < max_radius:

        chance = random()*(module.base_radius/max_radius)
        # print(chance)
        if ends_only and False:
            chance *= .5 + module.position.normalized().dot(module.direction) * .5

        key = get_pruning_key(module.position)
        can_see_sun = not ends_only
        if key not in density_dict or density_dict[key] < .5:
            print("key")
            can_see_sun = True
            if not ends_only:
                chance /= 2

        if can_see_sun and chance < proba:
            print('coucou')
            axis = Vector((1, 0, 0))
            if module.direction != Vector((0, 0, 1)):
                axis = module.direction.cross(Vector((0, 0, 1))).cross(module.direction).normalized()
            angle = (random() - .5) * pi/2
            direction = module.direction * Matrix.Rotation(angle, 3, axis)
            direction.z *= .3
            v = square(.1)
            rot = direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
            verts.extend([i*rot + module.position for i in v])
            weights.append(min(1, module.base_radius)/2 + .5)

    if module .head_module_1 is not None:
        add_emitters_rec(module.head_module_1, max_radius, verts, proba, weights, density_dict, ends_only)
    if module.head_module_2 is not None:
        add_emitters_rec(module.head_module_2, max_radius, verts, proba, weights, density_dict, ends_only)


def create_particle_system(obj, number, vertex_group, dupli_object, size):
    """ Creates a particle system

    Args:
        ob - (object) The object on which the particle system is created
        number - (int) The number of particles that will be rendered
        display - (int) The number of particles displayed on the viewport
        vertex_group - (vertex group) The vertex group controlling the density of particles
    """
    leaf = obj.modifiers.new("leafs", 'PARTICLE_SYSTEM')
    part = obj.particle_systems[0]

    settings = leaf.particle_system.settings
    settings.name = "leaf"
    settings.type = "HAIR"
    settings.use_advanced_hair = True
    settings.use_emit_random = False
    settings.use_rotation_dupli = True
    settings.use_rotations = True
    settings.particle_size = 0.1 * size
    settings.size_random = 0.25
    settings.brownian_factor = 1
    settings.use_render_emitter = False

    settings.render_type = "OBJECT"
    if dupli_object is not None:
        settings.dupli_object = dupli_object
    settings.count = number
    settings.emit_from = 'FACE'
    settings.userjit = 1
    settings.rotation_mode = 'NOR'
    bpy.data.particles["leaf"].phase_factor = -.1
    settings.phase_factor_random = 0.2
    settings.phase_factor_random = 0.30303
    settings.factor_random = 0.2
    leaf.particle_system.vertex_group_length = vertex_group.name


def create_twig(random_seed, length, iterations, randomness, radius, split_proba, offset, gravity_strength,
                particle_proba, leaf, leaf_size, material):
    seed(random_seed)
    tree = add_basic_trunk(radius=radius, radius_decrease=.97, randomness=randomness, up_attraction=2, twist=0, height=length, branch_length=.8, horizontal=True)

    add_splits(root=tree, proba=.97, selection=[], creator="", split_angle=50, spin=180, head_size=.6, offset=offset, constraint_z=True)

    grow(root=tree, iterations=iterations, min_radius=0, limit_method="iterations", branch_length=2.5, split_proba=split_proba,
         split_angle=45, split_deviation=.25, split_radius=.6, radius_decrease=.88, randomness=randomness, spin=180,
         spin_randomness=.1, creator="", selection=[], gravity_strength=gravity_strength, pruning_strength=0, shape_factor=0, up_attraction=0, kill_below_0=False)

    draw_module(tree, 0, twig=True)
    obj = bpy.context.object
    obj.active_material = bpy.data.materials.get(material)
    bpy.ops.object.select_all(action='DESELECT')

    emitter = add_particles_emitter(tree, radius * particle_proba / 2, particle_proba, leaf, leaf_size, ends_only=False)
    emitter.select = True
    bpy.context.scene.objects.active = emitter
    bpy.ops.object.duplicates_make_real()

    for ob in bpy.context.selected_objects:
        if ob == emitter:
            ob.select = False
    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.join()
    obj.scale = (.2,.2,.2)

    bpy.ops.object.select_all(action='DESELECT')
    emitter.select = True
    leaf.select = True
    bpy.ops.object.delete(use_global=False)





