from random import randint
import numpy as np
import time
import json
import bpy
from bpy.types import Node, Operator
import bmesh
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty, PointerProperty
from .base_node import BaseNode
from ..tree import MTree


def test_function(self, context):
    print("coucou")


class MtreeParameters(Node, BaseNode):
    def test_function2(self, context):
        print("coucou")


    bl_label = "Tree paramteters"
    
    auto_update = BoolProperty(update = BaseNode.property_changed)
    resolution = IntProperty(min=0, default=16, update = BaseNode.property_changed)
    create_leafs = BoolProperty(default = False, update = BaseNode.property_changed)
    leaf_amount = IntProperty(min=1, default=3000, update = BaseNode.property_changed)
    leaf_max_radius = FloatProperty(min=0, default=.1, update = BaseNode.property_changed)
    leaf_weight = FloatProperty(min=-1, max=1, default=0, update = BaseNode.property_changed)
    leaf_dupli_object = PointerProperty(type=bpy.types.Object, name="leaf", update = BaseNode.property_changed)
    leaf_size = FloatProperty(min=0, default=.1, update = BaseNode.property_changed)

    last_execution_info = StringProperty() # this propperty is not be in the properties variable in order to avoid loop

    properties = ["resolution", "create_leafs", "leaf_amount", "leaf_max_radius", "leaf_weight", "leaf_dupli_object", "leaf_size"]

    def init(self, context):
        self.name = MtreeParameters.bl_label

    def execute(self):
        new_execution_info = self.id_data.save_as_json(return_string = True) # get string of all parameters organised in a dictionary
        change_level = get_tree_changes_level(self.last_execution_info, new_execution_info) # will return a string indicating at which level of the tree a change has been made

        self.last_execution_info = new_execution_info
        tree_ob, leaf_ob = get_current_object()
        if tree_ob is None:
            change_level = "tree_execution"

        if change_level is None: # if there has been no changes, end the function execution
            return
        if self.auto_update and tree_ob is None: # if auto_update is on, the active object shouldn't change. If the active object changes, stop auto execution
            self.auto_update = False
            return

        tree = MTree()
        node_tree = self.id_data
        try:
            trunk = [node for node in node_tree.nodes if node.bl_idname == "MtreeTrunk"][0] # get trunk function
        except IndexError:
            ShowMessageBox("The tree needs a trunk node in order to execute", "Invalid node tree", "ERROR")
            return
        t0 = time.clock()
        if change_level != "particle_system":
            trunk.execute(tree)
        t1 = time.clock()
        if change_level == "tree_execution":
            tree_ob = generate_tree_object(tree_ob, tree, self.resolution)
        t2 = time.clock()
        if self.create_leafs:
            if change_level == "leafs_emitter":
                leaf_ob = generate_leafs_object(tree, self.leaf_amount, self.leaf_weight, self.leaf_max_radius, leaf_ob, tree_ob)
            create_particle_system(leaf_ob, self.leaf_amount, self.leaf_dupli_object, self.leaf_size)
        elif leaf_ob != None: # if there should not be leafs yet an emitter exists, delete it
            bpy.data.objects.remove(leaf_ob, do_unlink=True) # delete leaf object
        t3 = time.clock()

        print("tree generation duration : {}".format(t1-t0))
        print("mesh creation duration : {}".format(t2-t1))
        print("leafs emitter creation duration : {}".format(t3-t2))
    

    def draw_buttons(self, context, layout):
        layout.prop(self, "auto_update")
        op = layout.operator("mtree.randomize_tree", text='randomize tree') # will call RandomizeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator
        layout.prop(self, "resolution")
        op = layout.operator("object.mtree_execute_tree", text='execute tree') # will call ExecuteMtreeNodeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator

        box = layout.box()
        box.prop(self, "create_leafs")
        if self.create_leafs:
            box.prop(self, "leaf_amount")
            box.prop(self, "leaf_max_radius")
            box.prop(self, "leaf_weight")
            box.prop(self, "leaf_dupli_object")
            box.prop(self, "leaf_size")


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
    material = None # material of tree object
    if ob == None: # if no object is specified, create one        
        ob = bpy.data.objects.new('tree', mesh) 
        bpy.context.scene.collection.objects.link(ob)
        ob[tree_property] = True # create custom object parameter to recognise tree object
    else: # delete old mesh data 
        material = ob.active_material
        old_mesh = ob.data
        ob.data = mesh
        bpy.data.meshes.remove(old_mesh)

    mesh.from_pydata(verts, [], faces)
    smoothings = np.ones(len(faces), dtype=bool)
    mesh.polygons.foreach_set("use_smooth", smoothings) # smooth mesh shading
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
    if material is not None:
        ob.active_material = material
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

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def get_tree_changes_level(last_execution_info, new_execution_info):
    ''' compare two execution info and return the level of diference.
        the level of diference can be:
        - tree_execution
        - leafs_emitter
        - particle_system '''
    
    if last_execution_info == "" or new_execution_info == "":
        return "tree_execution"
    
    if last_execution_info == new_execution_info:
        print("same")
        return None

    e1 = json.loads(last_execution_info)
    e2 = json.loads(new_execution_info)
    n1 = e1["nodes"]
    n2 = e2["nodes"]
    
    if e1.keys() != e2.keys() or len(n1) != len(n2): # if the node tree has changed then the tree mesh must be recreated 
        return "tree_execution"

    leaf_emitter = False # true if a change of level leaf emitter is detected
    particle_system = False # true if a change of level particle system is detected
    for key in range(len(n1)):
        node_1 = n1[key]
        node_2 = n2[key]
        for prop in node_1.keys():
            if node_1[prop] != node_2[prop]: # if a property has been changed
                print(prop)
                if node_1["bl_idname"] != "MtreeParameters": # if the property has been changed in a tree function, the tree mesh must be recreated
                    return "tree_execution"
                elif prop == "resolution":
                    return "tree_execution"
                elif prop in {"create_leafs", "leaf_max_radius", "leaf_amount"}:
                    leaf_emitter = True
                else:
                    particle_system = True
    if leaf_emitter:
        return "leafs_emitter"
    if particle_system:
        return "particle_system"

class ExecuteMtreeNodeTreeOperator(Operator):

    bl_idname = "object.mtree_execute_tree"
    bl_label = "Execute Mtree node tree"
    node_group_name = StringProperty()

    def execute(self, context):
        node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        node.execute()
        return {'FINISHED'}

class RandomizeTreeOperator(Operator):
    bl_idname = "mtree.randomize_tree"
    bl_label = "Randomize Mtree node tree"
    
    node_group_name = StringProperty()

    def execute(self, context):
        parameters_node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        for node in [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname != "MtreeTwig"]:
            try:
                node.seed = randint(0,100)
            except:
                pass
        parameters_node.execute()
        return {'FINISHED'}

