import time
import numpy as np
import bpy
from .... import m_tree
from ..base_types.node import MtreeNode 


class TreeMesherNode(bpy.types.Node, MtreeNode):
    bl_idname = "mt_MesherNode"
    bl_label = "Tree Mesher Node"


    def init(self, context):
        self.add_output("mt_TreeSocket", "Tree", is_property=False)

    def build_tree(self):
        tree = m_tree.Tree()
        trunk_function = self.outputs[0].links[0].to_node.construct_function()
        tree.set_trunk_function(trunk_function)
        t0 = time.time()
        tree.execute_functions()
        print("executing_functions:", (time.time() - t0) * 1000)
        t0 = time.time()
        
        cpp_mesh = self.mesh_tree(tree)
        print("generating:", (time.time() - t0)*1000)

        # self.test_time(cpp_mesh)
        self.output_object(cpp_mesh)
    
    def mesh_tree(self, tree):
        mesher = m_tree.ManifoldMesher()
        mesher.radial_n_points = 32
        mesh_data = mesher.mesh_tree(tree)
        return mesh_data

    def output_object(self, cp_mesh):
        tree_obj = bpy.context.object
        if tree_obj is None:
            tree_mesh = bpy.data.meshes.new('tree')
            tree_obj = bpy.data.objects.new("tree", tree_mesh)
            bpy.context.collection.objects.link(tree_obj)
        else:
            tree_mesh = tree_obj.data
            tree_mesh.clear_geometry()
        bpy.context.view_layer.objects.active = tree_obj
        self.fill_blender_mesh(tree_mesh, cp_mesh)
   
    def fill_blender_mesh(self, mesh, cpp_mesh):
        t0 = time.time()
        verts = cpp_mesh.get_vertices()
        faces = cpp_mesh.get_polygons()
        radii = cpp_mesh.get_float_attribute("radius")
        directions = cpp_mesh.get_vector3_attribute("direction")
        print("readback", (time.time() - t0)*1000)
        t0 = time.time()

        mesh.vertices.add(len(verts)//3)
        mesh.vertices.foreach_set("co", verts)
        mesh.attributes.new(name='radius', type='FLOAT', domain='POINT')
        mesh.attributes['radius'].data.foreach_set('value', radii)
        mesh.attributes.new(name='direction', type='FLOAT_VECTOR', domain='POINT')
        mesh.attributes['direction'].data.foreach_set('vector', directions)
        
        mesh.loops.add(len(faces))
        mesh.loops.foreach_set("vertex_index", faces)
        
        loop_start = np.arange(0, len(faces), 4, dtype=np.int)
        loop_total = np.ones(len(faces)//4, dtype = np.int)*4
        mesh.polygons.add(len(faces)//4)
        mesh.polygons.foreach_set("loop_start", loop_start)
        mesh.polygons.foreach_set("loop_total", loop_total)
        
        # uv_data = uvs[triangle_array]
        # uv_layer = mesh.uv_layers.new()
        # uv_layer.data.foreach_set("uv", uv_data.flatten())
        mesh.update(calc_edges=True)    
        print("filling mesh:", (time.time() - t0)*1000)

    def draw(self, context, layout):
        valid_tree = self.get_tree_validity()
        row = layout.row()
        row.enabled = valid_tree
        properties = row.operator("mtree.node_function", text="press me !")
        properties.node_tree_name = self.get_node_tree().name
        properties.node_name = self.name
        properties.function_name = "build_tree"

    def get_tree_validity(self):
        has_valid_child = len(self.outputs[0].links) == 1
        loops_detected = self.detect_loop(self)
        return has_valid_child and not loops_detected

    def detect_loop(self, node = None, seen_nodes = None):
        if node is None: 
            node = self
        if seen_nodes is None:
            seen_nodes = set()
        for output in node.outputs:
            for link in output.links:
                destination_node = link.to_node
                if destination_node in seen_nodes:
                    return True
                seen_nodes.add(destination_node)
                self.detect_loop(destination_node, seen_nodes)
        return False

