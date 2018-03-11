import bpy
from mathutils import Vector
from math import inf


class Loop:
    def __init__(self):
        self.verts = []
        self.barycenter = Vector()
        self.neighbour = None

    def update_barycenter(self, data):
        self.barycenter = Vector((0, 0, 0))
        for v in self.verts:
            self.barycenter += data.vertices[v].co
        self.barycenter /= len(self.verts)

    def bridge(self, data):
        for v0 in self.verts:
            pos = data.vertices[v0].co
            closest = 0
            dist = inf
            for v1 in self.neighbour.verts:
                if (pos - data.vertices[v1].co).length < dist:
                    closest = v1
                    dist = (pos - data.vertices[v1].co).length
            data.vertices[v0].co = data.vertices[closest].co


def bridge(obj):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(type='EDGE')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold()
    bpy.ops.object.mode_set(mode='OBJECT')
    data = obj.data
    verts = [v.index for v in data.vertices if v.select]
    edges = [e for e in data.edges if e.select]

    verts_dict = {v: -1 for v in verts}
    loops_dict = {}
    loops_number = 0
    for e in edges:
        v0, v1 = e.vertices
        if verts_dict[v0] != -1 and verts_dict[v1] != -1:
            ma = max(verts_dict[v0], verts_dict[v1])
            mi = min(verts_dict[v0], verts_dict[v1])
            loops_dict[ma] = mi

        elif verts_dict[v1] != -1:
            verts_dict[v0] = verts_dict[v1]

        elif verts_dict[v0] != -1:
            verts_dict[v1] = verts_dict[v0]

        else:
            verts_dict[v0] = loops_number
            verts_dict[v1] = loops_number
            loops_dict[loops_number] = loops_number
            loops_number += 1

    loops = [Loop() for i in range(loops_number)]
    for v in verts:
        loops[loops_dict[verts_dict[v]]].verts.append(v)
    loops = [loops[i] for i in range(len(loops)) if len(loops[i].verts) > 0 and i > 0]

    for l in loops:
        l.update_barycenter(data)

    print(len(loops))

    new_loops = []
    for i, l in enumerate(loops):
        bar = l.barycenter
        dist = inf
        neighbour = (-1, None)
        for j, l1 in enumerate(loops):
            if i != j:
                new_dist = (l1.barycenter - bar).length
                if new_dist < dist:
                    dist = new_dist
                    neighbour = (j, l1)
        l.neighbour = neighbour[1]
        new_loops.append(l)
        loops[-1], loops[neighbour[0]] = loops[neighbour[0]], loops[-1]
        loops.pop()

    print(len(new_loops))

    for l in new_loops:
        l.bridge(data)

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.mode_set(mode='OBJECT')