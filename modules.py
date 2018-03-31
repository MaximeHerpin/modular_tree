# The objective is to build a tree object whose all branches are connected. In other words, the tree is manifold.
# To do so, the tree is generated as a succession of modules that can represent splits, stems and so on.
# The modules are objects from the class Module.
# Each module has a resolution, except the modules that make the junction between two different levels of subdivision




import bpy, bmesh
import numpy as np
from mathutils import Vector, Matrix
from math import pi, sqrt, cos, sin
from .bridge import bridge
from random import random


def square(size):
    """Returns a list of 4 vectors arranged in a square of specified size"""
    return [Vector((-1, -1, 0))*size, Vector((1, -1, 0))*size, Vector((1, 1, 0))*size, Vector((-1, 1, 0))*size]


def octagon(size):
    result = []
    for i in range(8):
        angle = pi*i/4
        result.append(Vector((cos(angle), sin(angle), 0)) * size)
    return result


def directions_to_spin(direction, secondary_direction):
    direction_rotation = Vector((0,0,1)).rotation_difference(direction).to_matrix()
    secondary_direction = secondary_direction * direction_rotation
    spin = - secondary_direction.xy.angle_signed(Vector((-1, 0)))
    return spin


def get_direction(primary_direction, angle, spin):
    rot_1 = Matrix.Rotation(angle, 4, 'Y')
    rot_2 = primary_direction.rotation_difference(Vector((0,0,1))).to_matrix()
    rot_3 = Matrix.Rotation(spin, 4, 'Z')
    direction = ((rot_1 * Vector((0, 0, 1))) * rot_3) * rot_2
    return direction


def average_vector(vectors):
    """returns the average vector of a list of vectors"""
    v = sum(vectors, Vector())
    v /= len(vectors)
    return v


def find_verts_number_rec(module):
    if module is None:
        return 0
    if module.type == 'root' or module.type == 'branch':
        return 4 + find_verts_number_rec(module.head_module_1)
    if module.type == 'split':
        return 8 + find_verts_number_rec(module.head_module_1) + find_verts_number_rec(module.head_module_2)


def find_faces_number_rec(module):
    if module is None:
        return 1
    if module.type == 'root':
        return find_faces_number_rec(module.head_module_1)
    if module.type == 'branch':
        return 4 + find_faces_number_rec(module.head_module_1)
    if module.type == 'split':
        return 7 + find_faces_number_rec(module.head_module_1) + find_faces_number_rec(module.head_module_2)


def draw_module(root, resolution_levels, twig=False):
    max_radius = root.base_radius
    root.resolution = resolution_levels
    apply_resolution_rec(root.head_module_1, resolution_levels, max_radius, root)

    verts = [[] for i in range(resolution_levels+1)]
    faces = [[] for i in range(resolution_levels+1)]
    uvs = [[] for i in range(resolution_levels+1)]
    v_groups = [[] for i in range(resolution_levels+1)]

    root.build()
    verts[-1] = [v for v in root.verts]
    extremities = [root]
    while len(extremities) > 0:
        new_extremities = []
        for module in extremities:
            for head in range(module.head_number):
                new_module = module.head_module_1 if head == 0 else module.head_module_2
                if new_module is not None:
                    resolution = new_module.resolution
                    curr_verts_number = len(verts[resolution])
                    module.link(new_module, head, curr_verts_number)
                    verts[resolution].extend(new_module.verts)
                    faces[resolution].extend(new_module.faces)
                    uvs[resolution].extend(new_module.uvs)
                    v_groups[resolution].append((list(range(curr_verts_number, curr_verts_number+len(new_module.verts))), new_module.base_radius / max_radius))
                    new_extremities.append(new_module)

        extremities = new_extremities

    objects = []

    for i in range(resolution_levels+1):
        bpy.ops.object.select_all(action='DESELECT')
        name = "twig" if twig else "tree"
        mesh = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bm.from_mesh(mesh)

        for v in verts[i]:
            bm.verts.new(v)
        bm.verts.ensure_lookup_table()

        for f in faces[i]:
            try:
                bm.faces.new([bm.verts[j] for j in f])
            except:
                print(f)

        bm.faces.ensure_lookup_table()

        bm.loops.layers.uv.new()
        uv_layer = bm.loops.layers.uv.active
        for index, face in enumerate(bm.faces):
            for j, loop in enumerate(face.loops):
                loop[uv_layer].uv = uvs[i][index][j]

        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj.location = bpy.context.scene.cursor_location
        vg = obj.vertex_groups.new("radius")
        for weights in v_groups[i]:
            vg.add(weights[0], weights[1], 'REPLACE')
        bpy.context.scene.objects.link(obj)
        bpy.context.scene.objects.active = obj
        if not twig:
            obj["is_tree"] = True

        obj["tree_type"] = "object"
        obj.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.subdivision_set(level=i)
        print(i)
        objects.append(obj)

    for o in objects:
        o.select = True
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    bridge(bpy.context.object)


def visualize_with_curves(root):
    curve_data = bpy.data.curves.new('Tree', type='CURVE')
    curve_data.dimensions = '3D'
    polyline = curve_data.splines.new('POLY')
    x, y, z = root.position
    polyline.points[0].co = (x, y, z, 1)
    polyline.points[0].radius = root.base_radius
    draw_curve_rec(root, polyline, curve_data)

    curveOB = bpy.data.objects.new('Tree', curve_data)
    curveOB.location = bpy.context.scene.cursor_location
    curve_data.bevel_depth = 1
    curve_data.bevel_resolution = 0
    curve_data.fill_mode = 'FULL'

    scene = bpy.context.scene
    scene.objects.link(curveOB)
    scene.objects.active = curveOB
    curveOB["is_tree"] = True
    curveOB["tree_type"] = "curve"
    curveOB.select = True


def draw_curve_rec(module, polyline, curve_data):
    if module is not None:
        polyline.points.add(1)
        x,y,z = module.position
        polyline.points[-1].co = (x, y, z, 1)
        polyline.points[-1].radius = module.base_radius
        draw_curve_rec(module.head_module_1, polyline, curve_data)
        if module.type == 'split' and module.head_module_2 is not None:
            new_polyline = curve_data.splines.new('POLY')
            # new_polyline.points.add(1)
            new_polyline.points[0].co = (x, y, z, 1)
            new_polyline.points[0].radius = module.base_radius
            draw_curve_rec(module.head_module_2, new_polyline, curve_data)


def roll_indexes(indexes, angle_diff):
    """ shift a list according to an angle between two squares so that the indexes are aligned"""
    shift = int(4*angle_diff/pi)%8
    shifts = np.array([0, -1, -1, -2, -2, -3, -3, 0, 0, 0])
    shift = shifts[shift]
    return np.roll(indexes, -shift)


def apply_resolution_rec(module, resolution_levels, max_radius, parent):
    resolution = max(parent.resolution - 1, int(resolution_levels * module.base_radius / max_radius +.6))
    if module.type == 'branch' and parent.type == 'branch':
        module.resolution = resolution
        if resolution < parent.resolution:
            # transition = Transition(module.position, module.direction, module.base_radius, module.length, module.head_1_radius, resolution, module.starting_index, module.spin)
            # if parent.head_module_2 == module:
            #     parent.head_module_2 = transition
            # else:
            #     parent.head_module_1 = transition
            # transition.head_module_1 = module.head_module_1
            # transition.head_module_2 = module.head_module_2
            # module = transition
            module.direction = parent.direction
            module.draw_base = True
    else:
        module.resolution = parent.resolution

    if module.head_module_1 is not None:
        apply_resolution_rec(module.head_module_1, resolution_levels, max_radius, module)

    if module.head_module_2 is not None:
        apply_resolution_rec(module.head_module_2, resolution_levels, max_radius, module)


class Module:
    def __init__(self, position, direction, radius, resolution, starting_index, spin):
        self.verts = np.array([])
        self.faces = np.array([])
        self.uvs = np.array([])
        self.uv_height = 0
        self.type = 'module'
        self.creator = "default"
        self.position = position
        self.direction = direction
        self.base_radius = radius
        self.resolution = resolution
        self.spin = spin
        self.starting_index = starting_index
        # self.base_pos = []
        self.head_module_1 = None
        self.head_module_2 = None

    def draw(self):
        mesh = bpy.data.meshes.new(self.type)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        for v in self.verts:
            bm.verts.new(v)
        bm.verts.ensure_lookup_table()

        for f in self.faces:
            bm.faces.new([bm.verts[i] for i in f])

        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(self.type, mesh)
        obj.location = Vector((0, 0, 0))
        bpy.context.scene.objects.link(obj)
        bpy.context.scene.objects.active = obj
        obj.select = True

    def get_faces(self, starting_index=0):
        return [tuple([i + starting_index for i in f]) for f in self.faces]

    def get_head_direction(self, head):
        return self.direction

    def get_extremities_rec(self, curr_extremities, selection):
        is_selected = selection == [] or self.creator in selection
        if self.head_module_1 is None:
            if is_selected:
                curr_extremities.append((self, 0))
        else:
            self.head_module_1.get_extremities_rec(curr_extremities, selection)
        if self.head_module_2 is None:
            if self.type == 'split' and is_selected:
                curr_extremities.append((self, 1))
        else:
            self.head_module_2.get_extremities_rec(curr_extremities, selection)

    def __repr__(self):
        if self.type == 'split':
            return str(self.type) + " " + str(self.position.to_tuple(2)) + " " + self.head_module_1.__repr__() + self.head_module_2.__repr__()
        else:
            return str(self.type) + " " + str(self.position.to_tuple(2)) + " " + self.head_module_1.__repr__()


class Split(Module):
    def __init__(self, position=Vector(), direction=Vector(), radius=1, resolution=0, starting_index=0, spin=0, head_2_length=1, head_2_radius=.6):
        Module.__init__(self,position, direction, radius, resolution, starting_index, spin)
        self.type = 'split'
        self.head_1_radius = .99 * self.base_radius
        self.head_2_radius = head_2_radius * self.base_radius
        self.primary_angle = pi/18
        self.secondary_angle = pi/4
        self.head_1_length = self.base_radius * 3
        self.head_2_length = head_2_length
        self.head_number = 2
        self.head_1_direction = Vector()
        self.head_2_direction = Vector()


        # self.build()
        # self.draw()

    def get_head_indexes(self, head):
        if head == 1:
            return [self.starting_index + i for i in range(4)]
        else:
            return [self.starting_index + 4 + i for i in range(4)]

    def get_head_pos(self, head):
        if head==0:
            direction = self.get_head_direction(0)
            return self.position + direction * self.head_1_length
        elif head==1:
            direction = self.get_head_direction(1)
            return self.position + direction * self.head_2_length

    def get_head_direction(self, head):
        if head == 0:
            return get_direction(self.direction, self.primary_angle, self.spin)
        else:
            return get_direction(self.direction, self.primary_angle - self.secondary_angle, self.spin)

    def build(self, base_indexes=range(4)):
        radius_correction = 1 - .25**(self.resolution+1)
        self.base_radius *= radius_correction
        self.head_1_radius *= radius_correction
        self.head_2_radius *= radius_correction

        uv_height = self.uv_height
        v2 = square(self.head_1_radius)
        v3 = square(self.head_2_radius)
        primary_rotation = Matrix.Rotation(self.primary_angle, 4, 'Y')
        secondary_rotation = Matrix.Rotation(self.primary_angle - self.secondary_angle, 4, 'Y')
        v2 = [primary_rotation * (v + Vector((0, 0, self.head_1_length))) for v in v2]
        v3 = [secondary_rotation * (v + Vector((0, 0, self.head_2_length))) for v in v3]
        self.verts = v2 + v3
        si = self.starting_index
        i0, i1, i2, i3 = base_indexes
        faces = [(i0, si, si + 1, i1), (i1, si + 1, si + 2, i2), (i2, si + 2, si + 3, i3), (i3, si+3, si+6, si+7), (si+4, si+5, si, i0), (si+6, si+3, si, si+5), (i3, si+7, si+4, i0)]

        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0,0,1))).to_matrix()
        self.verts = [((v * spin_rotation) * direction_rotation) + self.position for v in self.verts]
        self.head_1_direction = (self.verts[-5] + self.verts[-7])/2 - self.position
        self.head_2_direction = (self.verts[-1] + self.verts[-3])/2 - self.position
        self.verts = np.asarray([i.to_tuple() for i in self.verts])
        # self.base_pos = [(v * spin_rotation) * direction_rotation + self.position for v in square(self.base_radius)]
        uvs = [[(i / 4, uv_height), (i / 4, uv_height + .1*self.head_1_length / self.head_1_radius), ((i + 1) / 4, uv_height + .1*self.head_1_length / self.head_1_radius), ((i + 1) / 4, uv_height)] for i in range(3)]
        uvs.extend([[(i / 4, uv_height), (i / 4, uv_height + .1*self.head_2_length / self.head_2_radius), ((i + 1) / 4, uv_height + .1*self.head_2_length / self.head_2_radius), ((i + 1) / 4, uv_height)] for i in range(4)])

        if self.head_module_1 is None:
            faces.append([i for i in range(si, si+4)])
            uvs.append([(0, 0), (0, 1), (1, 1), (1, 0)])

        if self.head_module_2 is None:
            faces.append([i for i in range(si+4, si + 8)])
            uvs.append([(0, 0), (0, 1), (1, 1), (1, 0)])

        self.faces = np.asarray(faces)
        self.uvs = np.asarray(uvs)

    def link(self, module, head, verts_number):
        if head ==0:
            head_indexes = np.arange(self.starting_index, self.starting_index + 4)
        else:
            head_indexes = np.arange(self.starting_index+4, self.starting_index + 8)

        module.starting_index = verts_number
        spin_diff = (module.spin - self.spin) % (2*pi)
        module.build(roll_indexes(head_indexes, spin_diff))


class Branch(Module):
    def __init__(self, position=Vector(), direction=Vector, radius=1, length=1, head_radius=.95, resolution=0,
                 starting_index=0, spin=0):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "branch"
        self.length = length
        self.head_1_radius = head_radius * self.base_radius
        self.head_number = 1
        self.draw_base = False

        # self.build()
        # self.draw()

    def get_head_indexes(self, head):
        if head == 1:
            return np.arange(4) + self.starting_index

    def get_head_pos(self, head):
        return self.position + self.direction * self.length

    def build(self, base_indexes=np.arange(4)):
        radius_correction = 1 - .25**(self.resolution+1)
        self.base_radius *= radius_correction
        self.head_1_radius *= radius_correction
        uv_height = self.uv_height
        v2 = [v + Vector((0,0, self.length)) for v in square(self.head_1_radius)]
        if self.draw_base:
            v2.extend([v + Vector((0,0, 0*self.length/4)) for v in square(self.base_radius)])
        self.verts = v2

        i0, i1, i2, i3 = base_indexes
        si = self.starting_index
        if self.draw_base:
            i0, i1, i2, i3 = [si + 4 + i for i in range(4)]

        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = np.asarray([((v * spin_rotation) * direction_rotation + self.position).to_tuple() for v in self.verts])
        # self.base_pos = [(v * spin_rotation) * direction_rotation + self.position for v in square(self.base_radius)]
        m = min(base_indexes)
        faces = [(i0, si, si + 1, i1), (i1, si + 1, si + 2, i2), (i2, si + 2, si + 3, i3), (i3, si + 3, si, i0)]
        uvs = [[(i/4, uv_height), (i/4, uv_height + .1*self.length/self.base_radius), ((i+1)/4, uv_height + .1*self.length/self.base_radius), ((i+1)/4, uv_height)] for i in range(4)]

        if self.head_module_1 is None:
            faces.append([i for i in range(si, si+4)])
            uvs.append([(0, 0), (0, 1), (1, 1), (1, 0)])

        self.faces = np.asarray(faces)
        self.uvs = np.asarray(uvs)

    def link(self, module, head, verts_number):
        # module.position = (self.verts[0] + self.verts[2])/2
        # module.base_radius = self.head_1_radius
        # module.direction = self.direction
        module.starting_index = verts_number
        # self.head_module_1 = module
        n = len(self.verts)
        head_indexes = np.arange(4) + self.starting_index
        spin_diff = module.spin - self.spin
        module.uv_height = self.uv_height + .1*self.length/self.base_radius
        module.build(roll_indexes(head_indexes, spin_diff))
        # base_verts = roll_indexes(module.base_pos, spin_diff)
        # for i in range(4):
        #     self.verts[i] = self.verts[i]*.7 + base_verts[i]*.3


class Root(Module):
    def __init__(self, position=Vector(), direction=Vector, radius=1, resolution=0, starting_index=0, spin=0):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "root"
        self.head_number = 1
        self.head_1_radius = self.base_radius
        self.density_dict = dict()

    def build(self):
        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = np.asarray([((v * spin_rotation) * direction_rotation + self.position).to_tuple() for v in square(self.base_radius)])

    def get_head_pos(self, head):
        return self.position

    def link(self, module, head, verts_number):
        module.starting_index = verts_number
        spin_diff = module.spin - self.spin
        head_indexes = np.arange(4)
        module.uv_height = 0
        module.build(roll_indexes(head_indexes, spin_diff))


class Transition(Module):
    def __init__(self, position=Vector(), direction=Vector(), radius=1, length=1, head_radius=.95, resolution=0, starting_index=0, spin=0 ):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "transition"
        self.head_1_radius = head_radius
        self.length = length
        self.head_number = 1
        # print('transition')

    def build(self, base_indexes=None, create_base=False):
        v1 = octagon(self.base_radius)
        radius_correction = 1 - .25 ** (self.resolution + 1)
        self.base_radius *= radius_correction
        self.head_1_radius *= radius_correction
        v2 = [v + Vector((0,0, self.length)) for v in square(self.base_radius)]
        # v3 = [v * self.head_1_radius + Vector((0, 0, self.length/2)) for v in [Vector((-1, -.5, 0)), Vector((1, -.5, 0)), Vector((1, .5, 0)), Vector((-1, .5, 0))]]

        verts = v1 + v2

        faces = np.array([[0, 1, 14, 13], [1, 2, 10, 14], [2, 3, 11, 10], [3, 4, 15, 11], [4, 5, 12, 15], [5, 6, 8, 12], [6, 7, 9, 8], [7, 0, 13, 9], [13, 14, 10, 9], [15, 12, 8, 11]])
        faces = [[0, 1, 10, 9], [1,2,10], [2,3,11,10], [3,4,11], [4,5,8,11], [5,6,8], [6,7,9,8], [7,0,9]]
        # faces = np.array([[0, 1, 14, 13]])
        # self.faces = faces + self.starting_index
        self.faces = [tuple([i + self.starting_index for i in j]) for j in faces]
        # verts = [Vector(i) * self.base_radius for i in [(-0.37, 0.9, 0.0), (-0.9, 0.37, 0.0), (-0.9, -0.37, 0.0),
        #                                                 (-0.37, -0.9, 0.0), (0.37, -0.9, 0.0), (0.9, -0.37, -0.0),
        #                                                 (0.9, 0.37, 0.0), (0.37, 0.9, 0.0), (-0.9, -0.9, 1.38),
        #                                                 (0.9, -0.9, 1.38),
        #                                                 (0.9, 0.9, 1.38), (-0.9, 0.9, 1.38), (-0.93, 0.42, 0.84),
        #                                                 (-0.93, -0.42, 0.84), (0.93, -0.42, 0.84), (0.93, 0.42, 0.84)]]
        #
        # f = [tuple([i + self.starting_index for i in j]) for j in [[6, 15, 14, 5], [2, 13, 12, 1], [8, 13, 2, 3],
        #                                                            [11, 12, 13, 8], [0, 1, 12, 11], [14, 9, 4, 5],
        #                                                            [10, 9, 14, 15], [6, 7, 10, 15], [4, 9, 8, 3],
        #                                                            [0, 11, 10, 7]]]

        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = np.asarray([((v * spin_rotation) * direction_rotation + self.position).to_tuple() for v in verts])


    def link(self, module, head, verts_number):
        # module.position = (self.verts[0] + self.verts[2])/2
        # module.base_radius = self.head_1_radius
        # module.direction = self.direction
        module.starting_index = verts_number
        # self.head_module_1 = module
        head_indexes = np.arange(4) + self.starting_index + 8
        spin_diff = module.spin - self.spin
        module.uv_height = self.uv_height + .1*self.length/self.base_radius
        module.build(roll_indexes(head_indexes, spin_diff))
        # base_verts = roll_indexes(module.base_pos, spin_diff)
        # for i in range(4):
        #     self.verts[i] = self.verts[i]*.7 + base_verts[i]*.3

