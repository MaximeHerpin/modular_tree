import bpy
from bpy.types import Node, Operator
import bmesh
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty, PointerProperty
from .base_node import BaseNode
from ..tree import MTree

class MtreeParameters(Node, BaseNode):
    bl_label = "Tree paramteters"
    
    resolution = IntProperty(min=0, default=16)
    create_leafs = BoolProperty(default = False)
    leaf_amount = IntProperty(min=1, default=3000)
    leaf_max_radius = FloatProperty(min=0, default=.1)
    leaf_weight = FloatProperty(min=-1, max=1, default=0)
    leaf_dupli_object = PointerProperty(type=bpy.types.Object, name="leaf")
    leaf_size = FloatProperty(min=0, default=.1)

    def init(self, context):
        self.name = MtreeParameters.bl_label

    def draw_buttons(self, context, layout):
        layout.prop(self, "resolution")
        op = layout.operator("object.mtree_execute_tree", text='execute') # will call ExecuteMtreeNodeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator

        box = layout.box()
        box.prop(self, "create_leafs")
        if self.create_leafs:
            box.prop(self, "leaf_amount")
            box.prop(self, "leaf_max_radius")
            box.prop(self, "leaf_weight")
            box.prop(self, "leaf_dupli_object")
            box.prop(self, "leaf_size")

    def execute(self):
        tree = MTree()
        node_tree = self.id_data
        trunk = [node for node in node_tree.nodes if node.bl_idname == "MtreeTrunk"][0] # get trunk function
        # TODO : check that there is only one trunk node
        trunk.execute(tree)
        print("-"*50)

        tree_ob, leaf_ob = get_current_object()
        tree_ob = generate_tree_object(tree_ob, tree, self.resolution)
        if self.create_leafs:
            leaf_ob = generate_leafs_object(tree, self.leaf_amount, self.leaf_weight, self.leaf_max_radius, leaf_ob, tree_ob)
            create_particle_system(leaf_ob, self.leaf_amount, self.leaf_dupli_object, self.leaf_size)
        elif leaf_ob != None: # if there should not be leafs yet an emitter exists, delete it
            bpy.data.objects.remove(leaf_ob, do_unlink=True) # delete leaf object

def get_current_object():
    '''' return active object if it is a valid tree and potentially the leaf emitter attached to it '''
    ob = bpy.context.object
    if ob is None:
        return None, None
    tree_ob = None
    leaf_ob = None
    if ob.get("is_tree") is not None: # if true then the active object is a tree
        tree_ob = ob
        for child in ob.children: # looking if the tree has a leaf emitter
            if child.get("is_leaf") is not None: # if true then the child is a leaf emitter
                leaf_ob = child
                break
    
    if ob.get("is_leaf"): # if true then the active object is a leaf emitter
        leaf_ob = ob
        parent = ob.parent
        if parent is not None and parent.get("is_tree"): # if parent is a tree (it should be)
            tree_ob = parent
    
    return tree_ob, leaf_ob

def generate_tree_object(ob, tree, resolution, tree_property="is_tree"):
    ''' Create the tree mesh/object '''
    verts, faces, radii, uvs = tree.build_mesh_data(resolution) # tree mesh data
    mesh = bpy.data.meshes.new("tree")
    if ob == None: # if no object is specified, create one        
        ob = bpy.data.objects.new('tree', mesh) 
        bpy.context.scene.collection.objects.link(ob)
        ob[tree_property] = True # create custom object parameter to recognise tree object
    
    else: # delete old mesh data 
        old_mesh = ob.data
        ob.data = mesh
        bpy.data.meshes.remove(old_mesh)

    mesh.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()

    bm.loops.layers.uv.new()
    uv_layer = bm.loops.layers.uv.active
    for index, face in enumerate(bm.faces):
        for j, loop in enumerate(face.loops):
            loop[uv_layer].uv = uvs[index][j]

    bm.to_mesh(mesh)
    bm.free()

    
    for i in ob.vertex_groups:
        ob.vertex_groups.remove(i)
    v_group = ob.vertex_groups.new() # adding radius vertex group
    for v, w in radii:
        v_group.add(v, w, "ADD")
    
    return ob

def generate_leafs_object(tree, number, weight, max_radius, ob=None, tree_ob=None):
    ''' Create the particle system emitter object used for the leafs '''
    mesh = bpy.data.meshes.new("leafs")
    if ob == None: # if no object is specified, create one        
        ob = bpy.data.objects.new('leafs', mesh)
        collection = bpy.context.scene.collection
        collection.objects.link(ob)
        ob['is_leaf'] = True # create custom object parameter to recognise tree object
    else:
        old_mesh = ob.data
        ob.data = mesh
        bpy.data.meshes.remove(old_mesh)
        
    verts, faces = tree.get_leaf_emitter_data(number, weight, max_radius) # emitter mesh data
    mesh.from_pydata(verts, [], faces) # fill object mesh with new data
    ob.parent = tree_ob # make sure leafe emitter is child of tree object
    return ob

def create_particle_system(ob, number, dupli_object, size):
    """ Creates a particle system for the leafs emitter"""
    leaf = None #particle system
    for modifier in ob.modifiers: # check if object has already the particle system created
        if modifier.type == "PARTICLE_SYSTEM":
            leaf = modifier
    if leaf is None: # true when the particle system is not already in object
        leaf = ob.modifiers.new("leafs", 'PARTICLE_SYSTEM')

    settings = leaf.particle_system.settings
    settings.name = "leaf"
    settings.type = "HAIR"
    settings.count = number
    settings.use_advanced_hair = True
    settings.emit_from = 'FACE'
    settings.use_emit_random = False
    settings.use_even_distribution = False
    settings.userjit = 1
    settings.use_rotations = True
    settings.rotation_mode = 'NOR'
    bpy.data.particles["leaf"].phase_factor = -.1
    settings.phase_factor_random = 0.2
    settings.factor_random = 0.2
    settings.rotation_factor_random = 0.2
    settings.particle_size = size
    settings.size_random = 0.25
    ob.show_instancer_for_render = False
    settings.render_type = "OBJECT"
    if dupli_object is not None:
        settings.instance_object = dupli_object
        settings.use_rotation_instance = True


class ExecuteMtreeNodeTreeOperator(Operator):

    bl_idname = "object.mtree_execute_tree"
    bl_label = "Execute Mtree node tree"
    node_group_name = StringProperty()

    def execute(self, context):
        node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        node.execute()
        return {'FINISHED'}