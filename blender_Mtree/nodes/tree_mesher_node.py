import bpy
from ... import m_tree
from .base_types.node import MtreeNode 


class TreeMesherNode(bpy.types.Node, MtreeNode):
    bl_idname = "mt_MesherNode"
    bl_label = "Tree Mesher Node"


    def init(self, context):
        self.add_output("mt_TreeSocket", "Tree", is_property=False)



    def build_tree(self):
        tree = m_tree.Tree()
        trunk_function = self.outputs[0].links[0].to_node.construct_function()
        tree.set_trunk_function(trunk_function)
        tree.execute_functions()
        
        mesh = self.mesh_tree(tree)
        self.output_object(mesh)

    
    def mesh_tree(self, tree):
        mesher = m_tree.BasicMesher()
        mesh = mesher.mesh_tree(tree)
        return mesh

    def output_object(self, mesh):
        tree_mesh = bpy.data.meshes.new('tree')
        tree_mesh.from_pydata(mesh.get_vertices(), [], mesh.get_polygons())
        tree_obj = bpy.data.objects.new("tree", tree_mesh)
        bpy.context.collection.objects.link(tree_obj)

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

