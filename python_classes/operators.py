from bpy.utils import register_class, unregister_class
from gpu_extras.batch import batch_for_shader
import time
import bpy
import bmesh
import gpu
import numpy as np

from .. import m_tree

class MtreeTest(bpy.types.Operator):
    """Mtree Tests"""      # Use this as a tooltip for menu items and buttons.
    bl_idname = "m_tree.test"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Mtree Test"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    resolution: bpy.props.FloatProperty(name="resolution", default=1, min=.001)
    length: bpy.props.FloatProperty(name="length", default=1, min=.001)
    radius: bpy.props.FloatProperty(name="radius", default=.3, min=.001)
    randomness: bpy.props.FloatProperty(name="randomness", default=.1, min=.001)
    # branches_per_meter: bpy.props.FloatProperty(name="branches per meter", default=2, min=.001)
    # branches_radius : bpy.props.FloatProperty(name="branches radius", default=.5, min=.001, max = 1)
    # branches_length : bpy.props.FloatProperty(name="branches length", default=7, min=.001)
    # branches_angle : bpy.props.FloatProperty(name="branches angle", default=45, min=.001)
    # split_proba : bpy.props.FloatProperty(name="split proba", default=.1, min=0, max = 1)

    growth_iterations : bpy.props.IntProperty(name="growth_iterations", default=5, min=0)
    apical_dominance : bpy.props.FloatProperty(name="apical_dominance", default=.6, min=0, max = 1)
    branch_length : bpy.props.FloatProperty(name="branch length", default=.5, min=.001)
    gravitropism : bpy.props.FloatProperty(name="gravitropism", default=.1)
    gravity_strength : bpy.props.FloatProperty(name="gravity_strength", default=.1)
    branches_angle : bpy.props.FloatProperty(name="branches angle", default=45, min=.001)
    grow_threshold : bpy.props.FloatProperty(name="grow threshold", default=.2, min=0)
    split_threshold : bpy.props.FloatProperty(name="split threshold", default=.7, min=0)



    def execute(self, context):        # execute() is called when running the operator.

        t0 = time.time()
        tree = m_tree.Tree()
        trunk = m_tree.TrunkFunction()
        trunk.resolution = self.resolution
        trunk.length = self.length
        trunk.radius = self.radius
        trunk.randomness = self.randomness

        # branches = m_tree.BranchFunction()
        # branches.branches_per_meter = self.branches_per_meter
        # branches.radius = self.branches_radius
        # branches.length = self.branches_length
        # branches.branch_angle = self.branches_angle
        # branches.split_proba = self.split_proba
        # branches.resolution = self.resolution
        # branches.randomness = self.randomness
        # trunk.add_child(branches)

        growth = m_tree.GrowthFunction()
        growth.iterations = self.growth_iterations
        growth.grow_threshold = self.grow_threshold
        growth.split_threshold = self.split_threshold
        growth.apical_dominance = self.apical_dominance
        growth.randomness = self.randomness
        growth.branch_length = self.branch_length
        growth.gravitropism = self.gravitropism
        growth.gravity_strength = self.gravity_strength
        growth.split_angle = self.branches_angle

        trunk.add_child(growth)


        tree.set_trunk_function(trunk)
        tree.execute_functions()
        mesher = m_tree.BasicMesher()
        mesh = mesher.mesh_tree(tree)
        print(time.time() - t0)
        t0 = time.time()
        tree_mesh = bpy.data.meshes.new('tree')
        tree_mesh.from_pydata(mesh.get_vertices(), [], mesh.get_polygons())
        tree_obj = bpy.data.objects.new("tree", tree_mesh)
        context.collection.objects.link(tree_obj)
        print(time.time() - t0)
        return {'FINISHED'}


    def create_bmesh(self, vertices, polygons):
        bm = bmesh.new()

        for vert in vertices:
            bm.verts.new(vert)
        
        bm.verts.ensure_lookup_table()

        for polygon in polygons:
            bm.faces.new([bm.verts[i] for i in polygon])
        
        return bm
    

    def draw_with_shader(self, vertices, polygons):
        # shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
        # vertices = np.array(vertices).reshape(len(vertices) * 3)
        # polygons = np.array(polygons).reshape(len(polygons) * 4)
        polygons = [[i[j] for j in range(3)] for i in polygons]
        # self.batch = batch_for_shader(shader, 'TRIS',{"pos": vertices}, indices=polygons)
        # self.shader = gpu.shader.from_builtin('3D_SMOOTH_COLOR')
    
    def draw_mesh(self):
        self.batch.draw(self.shader)


class ExecuteNodeFunction(bpy.types.Operator):
    bl_idname = "mtree.node_function"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Node Function callback"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    node_tree_name: bpy.props.StringProperty()
    node_name: bpy.props.StringProperty()
    function_name : bpy.props.StringProperty()

    def execute(self, context):
        node = bpy.data.node_groups[self.node_tree_name].nodes[self.node_name]
        getattr(node, self.function_name)()
        return {'FINISHED'}


def register():
    register_class(ExecuteNodeFunction)

def unregister():
    unregister_class(ExecuteNodeFunction)
