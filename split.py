from collections import defaultdict
import bpy, bmesh
from mathutils import Vector, Matrix
from math import pi, sqrt
from random import random


def square(size):
    """Returns a list of 4 vectors arranged in a square of specified size"""
    return [Vector(i) * size for i in ((-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0))]


def directions_to_spin(direction, secondary_direction):
    direction_rotation = Vector((0,0,1)).rotation_difference(direction).to_matrix()
    secondary_direction = secondary_direction * direction_rotation
    spin = - secondary_direction.xy.angle_signed(Vector((-1, 0)))
    return spin


def average_vector(vectors):
    """returns the average vector of a list of vectors"""
    v = sum(vectors, Vector())
    v /= len(vectors)
    return v


def catmull_clark_subdivision(verts, faces, resolution, faces_shift=0, junctions = []):
    """subdivides the vertices and faces with th catmull clark algorithm"""

    for k in range(resolution):
        verts_number = len(verts)
        face_number = len(faces)
        # list of vectors at the center of each faces
        face_points = []

        # list of new edge points positions
        edge_points = []

        # lists of centers of adjacent faces for each vertex
        verts_adjacent_faces_points = [[] for i in range(len(verts))]

        # lists of center of adjacent edges for each vertex
        verts_adjacent_edges_centers = [[] for i in range(len(verts))]

        # dictionary where the keys are the edges and the values are lists of centers of adjacent faces
        edges = defaultdict(list)

        # dictionary where the keys are the edges and the values are the indexes of each edge new point
        edges_new_points = {}

        # dictionary where the keys are the index of boundary vertices and the values a list of boundary neighbours
        boundary_vertices = defaultdict(list)

        for f in faces:
            average = average_vector([verts[j] for j in f])
            face_points.append(average)
            for v in range(len(f)):
                verts_adjacent_faces_points[f[v]].append(average)
                v1, v2 = sorted((f[v], f[(v + 1) % len(f)]))
                edge_center = (verts[v1] + verts[v2]) / 2
                verts_adjacent_edges_centers[v1].append(edge_center)
                verts_adjacent_edges_centers[v2].append(edge_center)
                edges[(v1, v2)].append(average)

        for i, edge in enumerate(edges):
            i1, i2 = edge
            edge_center = (verts[i1] + verts[i2]) / 2

            if len(edges[edge]) == 2:
                adjacent_faces_average = sum(edges[edge], Vector()) / 2
                new_point = (edge_center + adjacent_faces_average) / 2
            else:
                new_point = edge_center
                boundary_vertices[i1].append(new_point)
                boundary_vertices[i2].append(new_point)
            edges_new_points[edge] = i
            edge_points.append(new_point)

        for i in range(len(verts)):
            n = len(verts_adjacent_faces_points[i])
            if n >= 3:
                p = verts[i]
                m1 = (n - 3) / n
                f = average_vector(verts_adjacent_faces_points[i])  # sum(verts_adjacent_faces_points[i], Vector())/4
                m2 = 1 / n
                r = average_vector(verts_adjacent_edges_centers[i])  # sum(verts_adjacent_edges_centers[i], Vector())/4
                m3 = 3 / n
                verts[i] = (f + 2 * r + (n - 3) * p) / n  # m1*p + (2*r + f)/4
            else:
                p = verts[i]
                r = sum(boundary_vertices[i], Vector()) / 2
                verts[i] = (p + r) / 2

        verts.extend(face_points + edge_points)
        new_faces = []
        fs = faces_shift
        for i, f in enumerate(faces):
            a, b, c, d = f
            edge_point_ab = verts_number + face_number + edges_new_points[tuple(sorted((a, b)))]
            edge_point_bc = verts_number + face_number + edges_new_points[tuple(sorted((b, c)))]
            edge_point_cd = verts_number + face_number + edges_new_points[tuple(sorted((c, d)))]
            edge_point_da = verts_number + face_number + edges_new_points[tuple(sorted((d, a)))]
            face_point = verts_number + i
            f1 = (a+fs, edge_point_ab+fs, face_point+fs, edge_point_da+fs)
            f2 = (b+fs, edge_point_bc+fs, face_point+fs, edge_point_ab+fs)
            f3 = (c+fs, edge_point_cd+fs, face_point+fs, edge_point_bc+fs)
            f4 = (d+fs, edge_point_da+fs, face_point+fs, edge_point_cd+fs)
            new_faces.extend([f1, f2, f3, f4])

        faces = new_faces
    if resolution == 0:
        faces = [tuple([i + faces_shift for i in f]) for f in faces]
    return verts, faces


def draw_module_rec(root):
    root.build()
    verts = root.verts
    faces = []
    extremities = [root]
    while len(extremities) > 0:
        new_extremities = []
        for module in extremities:
            print('module')
            if module.head_module_1 is not None:
                for head in range(module.head_number):
                    verts_number = len(verts)
                    new_module = module.head_module_1 if head == 0 else module.head_module_2
                    module.link(new_module, head, verts_number)
                    verts.extend(new_module.verts)
                    faces.extend(new_module.faces)
                    new_extremities.append(new_module)
        extremities = new_extremities

    mesh = bpy.data.meshes.new("tree")
    bm = bmesh.new()
    bm.from_mesh(mesh)

    for v in verts:
        bm.verts.new(v)
    bm.verts.ensure_lookup_table()

    for f in faces:
        try:
            bm.faces.new([bm.verts[j] for j in f])
        except:
            print('something happened')

    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("tree", mesh)
    obj.location = Vector((0, 0, 0))
    bpy.context.scene.objects.link(obj)
    bpy.context.scene.objects.active = obj
    obj.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def roll_indexes(indexes, angle_diff):
    """ shift a list according to an angle between two squares so that the indexes are aligned"""
    shift = int(4*angle_diff/pi)%8
    shifts = [0,-1,-1,-2,-2,-3,-3,0,0,1]
    shift = shifts[shift]
    return indexes[shift:] + indexes[:shift]

# The objective is to build a tree object whose all branches are connected. In other words, the tree is manifold.
# To do so, the tree is generated as a succession of modules that can represent splits, stems and so on.
# The modules are objects from the class Module.
# Each module has a resolution, except the modules that make the junction between two different levels of subdivision


class Module:
    def __init__(self, position, direction, radius, resolution, starting_index, spin):
        self.verts = []
        self.faces = []
        self.type = 'module'
        self.position = position
        self.direction = direction
        self.base_radius = radius
        self.resolution = resolution
        self.spin = spin
        self.starting_index = starting_index
        self.base_pos = []
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

    def update_props(self):
        pass

    def __repr__(self):
        if self.type == 'split':
            return str(self.type) + " " + str(self.position.to_tuple(2)) + " " + self.head_module_1.__repr__() + self.head_module_2.__repr__()
        else:
            return str(self.type) + " " + str(self.position.to_tuple(2)) + " " + self.head_module_1.__repr__()


class Split(Module):
    def __init__(self,position=Vector(), direction=Vector(), radius=1, resolution=0, starting_index=0, spin=0):
        Module.__init__(self,position, direction, radius, resolution, starting_index, spin)
        self.type = 'split'
        self.head_1_radius = .8 * self.base_radius
        self.head_2_radius = .6 * self.base_radius
        self.primary_angle = pi/18
        self.secondary_angle = (self.head_1_radius + self.head_2_radius)
        self.head_number = 2
        self.head_1_direction = Vector()
        self.head_2_direction = Vector()

        self.verts_number = [12, 39, 135, 495, 1887, 7359, 29055]

        # self.build()
        # self.draw()

    def get_head_indexes(self, head):
        if head == 1:
            return [self.starting_index + i for i in range(4)]
        else:
            return [self.starting_index + 4 + i for i in range(4)]

    def build(self, base_indexes=range(4)):
        v2 = square(self.head_1_radius)
        v3 = square(self.head_2_radius)
        primary_rotation = Matrix.Rotation(self.primary_angle, 4, 'Y')
        secondary_rotation = Matrix.Rotation(self.primary_angle - self.secondary_angle, 4, 'Y')
        v2 = [primary_rotation * (v + Vector((0, 0, self.base_radius))) for v in v2]
        v3 = [secondary_rotation * (v + Vector((0, 0, sqrt(self.head_1_radius**2 + self.base_radius**2)))) for v in v3]
        self.verts = v2 + v3
        si = self.starting_index
        i0, i1, i2, i3 = base_indexes
        self.faces = [(i0, si, si + 1, i1), (i1, si + 1, si + 2, i2), (i2, si + 2, si + 3, i3), (i3, si+3, si+6, si+7),
                      (si+4, si+5, si, i0), (si+6, si+3, si, si+5), (i3, si+7, si+4, i0)]
        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0,0,1))).to_matrix()
        self.verts = [((v * spin_rotation) * direction_rotation) + self.position for v in self.verts]
        self.head_1_direction = (self.verts[-5] + self.verts[-7])/2 - self.position
        self.head_2_direction = (self.verts[-1] + self.verts[-3])/2 - self.position
        self.base_pos = [(v * spin_rotation) * direction_rotation + self.position for v in square(self.base_radius)]

    def link(self, module, head, verts_number):
        if head ==0:
            # module.position = (self.verts[0] + self.verts[2])/2
            module.base_radius = self.head_1_radius
            head_indexes = list(range(self.starting_index, self.starting_index + 4))
            # module.direction = self.head_1_direction
            # self.head_module_1 = module

        else:
            # module.position = (self.verts[4] + self.verts[6])/2
            module.base_radius = self.head_2_radius
            head_indexes = list(range(self.starting_index + 4, self.starting_index + 8))
            # module.direction = self.head_2_direction
            # self.head_module_2 = module

        module.starting_index = verts_number
        spin_diff = module.spin - self.spin
        module.build(roll_indexes(head_indexes, spin_diff))
        # base_verts = roll_indexes(module.base_pos, spin_diff)
        # for i in range(4):
        #     self.verts[i] = (self.verts[4*head + i] + base_verts[i]) / 2


class Branch(Module):
    def __init__(self, position=Vector(), direction=Vector, radius=1, length=1, head_radius=.95, resolution=0,
                 starting_index=0, spin=0):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "branch"
        self.length = length
        self.head_1_radius = head_radius * self.base_radius
        self.verts_number = [4 * 2**i for i in range(7)]
        self.head_number = 1

        # self.build()
        # self.draw()

    def get_head_indexes(self, head):
        if head == 1:
            return [self.starting_index + i for i in range(4)]

    def build(self, base_indexes=range(4)):
        v2 = [v + Vector((0,0, self.length)) for v in square(self.head_1_radius)]
        self.verts = v2
        i0, i1, i2, i3 = base_indexes
        si = self.starting_index
        self.faces = [(i0, si, si+1, i1), (i1, si+1, si+2, i2), (i2, si+2, si+3, i3), (i3, si+3, si, i0)]
        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = [(v * spin_rotation) * direction_rotation + self.position for v in self.verts]
        self.base_pos = [(v * spin_rotation) * direction_rotation + self.position for v in square(self.base_radius)]

    def link(self, module, head, verts_number):
        # module.position = (self.verts[0] + self.verts[2])/2
        # module.base_radius = self.head_1_radius
        # module.direction = self.direction
        module.starting_index = verts_number
        # self.head_module_1 = module
        n = len(self.verts)
        head_indexes = list(range(self.starting_index, self.starting_index + 4))
        spin_diff = module.spin - self.spin
        module.build(roll_indexes(head_indexes, spin_diff))
        # base_verts = roll_indexes(module.base_pos, spin_diff)
        # for i in range(4):
        #     self.verts[i] = (self.verts[i] + base_verts[i])/2


class Root(Module):
    def __init__(self, position=Vector(), direction=Vector, radius=1, resolution=0, starting_index=0, spin=0):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "root"
        self.head_number = 1
        self.head_1_radius = self.base_radius

    def build(self):
        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = [(v * spin_rotation) * direction_rotation + self.position for v in square(self.base_radius)]

    def link(self, module, head, verts_number):
        module.starting_index = verts_number
        spin_diff = module.spin - self.spin
        head_indexes = list(range(4))
        module.build(roll_indexes(head_indexes, spin_diff))


class Transition(Module):
    def __init__(self, position=Vector(), direction=Vector(), radius=1, resolution=0, starting_index=0, spin=0):
        Module.__init__(self, position, direction, radius, resolution, starting_index, spin)
        self.type = "transition"
        self.head_1_radius = 1
        self.head_number = 1
        print('transition')

    def build(self, base_indexes=None, create_base=False):
        verts = [Vector(i) * self.base_radius for i in [(-0.37, 0.9, 0.0), (-0.9, 0.37, 0.0), (-0.9, -0.37, 0.0),
                                                        (-0.37, -0.9, 0.0), (0.37, -0.9, 0.0), (0.9, -0.37, -0.0),
                                                        (0.9, 0.37, 0.0), (0.37, 0.9, 0.0), (-0.9, -0.9, 1.38),
                                                        (0.9, -0.9, 1.38),
                                                        (0.9, 0.9, 1.38), (-0.9, 0.9, 1.38), (-0.93, 0.42, 0.84),
                                                        (-0.93, -0.42, 0.84), (0.93, -0.42, 0.84), (0.93, 0.42, 0.84)]]

        f = [tuple([i + self.starting_index for i in j]) for j in [[6, 15, 14, 5], [2, 13, 12, 1], [8, 13, 2, 3],
                                                                   [11, 12, 13, 8], [0, 1, 12, 11], [14, 9, 4, 5],
                                                                   [10, 9, 14, 15], [6, 7, 10, 15], [4, 9, 8, 3],
                                                                   [0, 11, 10, 7]]]

        spin_rotation = Matrix.Rotation(self.spin, 4, 'Z')
        direction_rotation = self.direction.rotation_difference(Vector((0, 0, 1))).to_matrix()
        self.verts = [(v * spin_rotation) * direction_rotation + self.position for v in verts]
        self.faces = f

    def link(self, module, head, verts_number):
        # noinspection PyTypeChecker
        module.position = (self.verts[8] + self.verts[10]) / 2
        module.base_radius = self.base_radius
        module.direction = self.direction
        module.starting_index = verts_number
        self.head_module_1 = module
        head_indexes = list(range(8 + self.starting_index, 8 + self.starting_index + 4))
        spin_diff = module.spin - self.spin
        module.build(roll_indexes(head_indexes, spin_diff))


class Tree:
    def __init__(self):
        print('new_tree')
        self.position = Vector()
        # list of the radius factors at which the resolution change
        self.resolutions = [.5, .25, 0]
        self.verts = [[] for i in self.resolutions]
        self.faces = [[] for i in self.resolutions]
        self.radius = 1

        root = Root(direction=Vector((0, 0, 1)), resolution=0)
        root.build()
        self.tree = root
        self.verts[0] = root.verts
        self.faces[0] = root.faces
        self.extremities = [root]
        # list of vertices that are not connected because of a change of resolution
        self. junctions = [[] for i in range(len(self.resolutions))]
        self.junctions_table = {}

        self.grow()
        print(self.tree)
        self.draw()

    def lod(self, radius):
        res = 0
        while radius < self.resolutions[res]:
            res += 1
        return res

    def grow(self):
        for iteration in range(20):
            new_extremities = []
            for module in self.extremities:
                for head in range(module.head_number):
                    radius = module.head_1_radius if head == 0 else module.head_2_radius
                    if self.resolutions[module.resolution] > radius and module.type != "transition":
                        res = module.resolution + 1
                    else:
                        res = module.resolution
                    override_choice = False
                    if res != module.resolution:
                        new_module = Transition(spin=module.spin, resolution=res)
                        override_choice = True
                    print(res)
                    verts_number = len(self.verts[res])
                    if not override_choice:
                        choice = random()
                        if choice < 0.3:
                            new_module = Split(spin=module.spin + pi/2, resolution=res)
                        else:
                            new_module = Branch(spin=module.spin, resolution=res)
                    module.link(new_module, head, verts_number)

                    if new_module.type == "transition":
                        junction_index = len(self.junctions)
                        for i in module.get_head_indexes(head)+[j+verts_number for j in range(4)]:
                            self.junctions_table[i] = junction_index
                        self.junctions[res].append(((module.get_head_indexes(head)), [i+verts_number for i in range(4)]))
                    self.verts[res].extend(new_module.verts)
                    self.faces[res].extend(new_module.faces)
                    new_extremities.append(new_module)
            self.extremities = new_extremities

    def draw(self):
        mesh = bpy.data.meshes.new("tree")
        bm = bmesh.new()
        bm.from_mesh(mesh)
        faces_shift = 0
        for i in range(len(self.resolutions)):
            if len(self.verts[i]) > 0 and self.faces is not None:
                res = len(self.resolutions) - 1 - i
                self.verts[i], self.faces[i] = catmull_clark_subdivision(self.verts[i], self.faces[i], res, faces_shift,
                                                                         self.junctions)

            faces_shift += len(self.verts[i])

            for v in self.verts[i]:
                bm.verts.new(v)
            bm.verts.ensure_lookup_table()

            for f in self.faces[i]:
                try:
                    bm.faces.new([bm.verts[j] for j in f])
                except:
                    print('something happened')

        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new("tree", mesh)
        obj.location = Vector((0, 0, 0))
        bpy.context.scene.objects.link(obj)
        bpy.context.scene.objects.active = obj
        obj.select = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')