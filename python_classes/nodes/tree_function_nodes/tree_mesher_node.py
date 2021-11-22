import time
import numpy as np
import bpy
from .... import m_tree
from ..base_types.node import MtreeNode 

def on_update_prop(node, context):
    node.build_tree()

class TreeMesherNode(bpy.types.Node, MtreeNode):
    bl_idname = "mt_MesherNode"
    bl_label = "Tree Mesher"

    radial_resolution : bpy.props.IntProperty(name="Radial Resolution", default=32, min=3, update=on_update_prop)
    smoothness : bpy.props.IntProperty(name="smoothness", default=4, min=0, update=on_update_prop)

    def init(self, context):
        self.add_output("mt_TreeSocket", "Tree", is_property=False)

    def draw_generate(self, container):
        properties = container.operator("mtree.node_function", text="Generate Tree")
        properties.node_tree_name = self.get_node_tree().name
        properties.node_name = self.name
        properties.function_name = "build_tree"
        

    def draw_properties(self, container):
        container.prop(self, "radial_resolution")
        container.prop(self, "smoothness")

    def draw_distribute_leaves(self, container):
        properties = container.operator("mtree.add_leaves", text="Add leaves")
        properties.object_id = self.get_current_tree_object().name

    def draw(self, context, layout):
        valid_tree = self.get_tree_validity()
        generate_row = layout.row()
        generate_row.enabled = valid_tree
        self.draw_generate(generate_row)
        self.draw_properties(layout)
        leaves_row = layout.row()
        leaves_row.enabled = valid_tree
        self.draw_distribute_leaves(leaves_row)

    def build_tree(self):
        if not self.get_tree_validity():
            return
        tree = m_tree.Tree()
        trunk_function = self.outputs[0].links[0].to_node.construct_function()
        tree.set_trunk_function(trunk_function)
        tree.execute_functions()
        cpp_mesh = self.mesh_tree(tree)
        self.output_object(cpp_mesh)
    
    def mesh_tree(self, tree):
        mesher = m_tree.ManifoldMesher()
        mesher.radial_n_points = self.radial_resolution
        mesher.smooth_iterations = self.smoothness
        mesh_data = mesher.mesh_tree(tree)
        return mesh_data

    def get_current_tree_object(self):
        tree_obj = bpy.context.object
        if tree_obj is None:
            tree_mesh = bpy.data.meshes.new('tree')
            tree_obj = bpy.data.objects.new("tree", tree_mesh)
            bpy.context.collection.objects.link(tree_obj)
        return tree_obj

    def output_object(self, cp_mesh):
        tree_obj = self.get_current_tree_object()
        tree_mesh = tree_obj.data
        tree_mesh.clear_geometry()
        bpy.context.view_layer.objects.active = tree_obj
        self.fill_blender_mesh(tree_mesh, cp_mesh)
   
    def fill_blender_mesh(self, mesh, cpp_mesh):
        verts = cpp_mesh.get_vertices()
        faces = cpp_mesh.get_polygons()
        radii = cpp_mesh.get_float_attribute("radius")
        directions = cpp_mesh.get_vector3_attribute("direction")

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
        mesh.polygons.foreach_set('use_smooth',  np.ones(len(faces)//4, dtype=np.bool))
        
        
        uv_data = cpp_mesh.get_uvs()
        uv_data.shape = (len(uv_data)//2, 2)
        uv_loops = cpp_mesh.get_uv_loops()
        uvs = uv_data[uv_loops].flatten()
        uv_layer = mesh.uv_layers.new() if len(mesh.uv_layers) == 0 else mesh.uv_layers[0]
        uv_layer.data.foreach_set("uv", uvs)
        
        mesh.update(calc_edges=True)    

    def get_tree_validity(self):
        has_valid_child = len(self.outputs[0].links) == 1
        loops_detected = self.detect_loop_rec(self)
        return has_valid_child and not loops_detected

    def detect_loop_rec(self, node = None, seen_nodes = None):
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
                self.detect_loop_rec(destination_node, seen_nodes)
        return False

