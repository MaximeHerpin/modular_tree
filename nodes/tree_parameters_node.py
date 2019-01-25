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


class MtreeParameters(Node, BaseNode):
    bl_label = "Tree parameters"
    
    auto_update = BoolProperty(update = BaseNode.property_changed)
    mesh_type = bpy.props.EnumProperty(
        items=[('final', 'Final', ''), ('preview', 'Preview', '')],
        name="output",
        default="preview", update = BaseNode.property_changed)
    resolution = IntProperty(min=0, default=16, update = BaseNode.property_changed)
    create_leafs = BoolProperty(default = False, update = BaseNode.property_changed)
    leaf_amount = IntProperty(min=1, default=3000, update = BaseNode.property_changed)
    leaf_max_radius = FloatProperty(min=0, default=.1, update = BaseNode.property_changed)
    leaf_dupli_object = PointerProperty(type=bpy.types.Object, name="leaf", update = BaseNode.property_changed)
    leaf_size = FloatProperty(min=0, default=.1, update = BaseNode.property_changed)
    leaf_extremity_only = BoolProperty(name="extremities only", default=False, update = BaseNode.property_changed)
    leaf_spread = FloatProperty(min=0, max=1, default=.2, update = BaseNode.property_changed)
    leaf_flatten = FloatProperty(min=0, max=1, default=.2, update = BaseNode.property_changed)
    leaf_weight = FloatProperty(min=-1, max=1, default=0, update = BaseNode.property_changed)

    has_changed = BoolProperty(default = True) # has there been a change in the node tree or any of its parameters
    active_tree_object = PointerProperty(type=bpy.types.Object) # referece to last tree made, used when updating

    last_execution_info = StringProperty() # this propperty is not be in the properties variable in order to avoid loop

    properties = ["resolution", "create_leafs", "leaf_amount", "leaf_max_radius", "leaf_weight", "leaf_dupli_object", "leaf_size", "leaf_extremity_only", "leaf_flatten", "leaf_spread", "mesh_type"]

    def init(self, context):
        self.name = MtreeParameters.bl_label

    def execute(self):
        new_execution_info = self.id_data.save_as_json(return_string = True) # get string of all parameters organised in a dictionary
        change_level = get_tree_changes_level(self.last_execution_info, new_execution_info) # will return a string indicating at which level of the tree a change has been made
        self.last_execution_info = new_execution_info
       
        if self.active_tree_object is not None and len(self.active_tree_object.users_scene) == 0: # if active tree has been deleted
            self.active_tree_object = None
            change_level = "tree_execution"

        tree_ob, leaf_ob = get_current_object("MESH" if self.mesh_type == "final" else "CURVE", active_tree=self.active_tree_object)
        if self.active_tree_object is None and (tree_ob is None or not tree_ob.select_get()):
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
            if self.mesh_type == "final":
                tree_ob = generate_tree_object(tree_ob, tree, self.resolution)
            else:
                tree_ob = generate_curve_object(tree_ob, tree)
            self.active_tree_object = tree_ob
        t2 = time.clock()
        if self.create_leafs:
            if change_level in {"tree_execution", "leafs_emitter"}:
                leaf_ob = generate_leafs_object(tree, self.leaf_amount, self.leaf_weight, self.leaf_max_radius, self.leaf_spread, self.leaf_flatten, self.leaf_extremity_only, leaf_ob, tree_ob)
            create_particle_system(leaf_ob, self.leaf_amount, self.leaf_dupli_object, self.leaf_size)
        elif leaf_ob != None: # if there should not be leafs yet an emitter exists, delete it
            bpy.data.objects.remove(leaf_ob, do_unlink=True) # delete leaf object
        t3 = time.clock()
        self.has_changed = False
        print("tree generation duration : {}".format(t1-t0))
        print("mesh creation duration : {}".format(t2-t1))
        print("leafs emitter creation duration : {}".format(t3-t2))
    
    def draw_buttons(self, context, layout):
        active_tree = self.active_tree_object is not None and len(self.active_tree_object.users_scene) > 0 # true if active tree exists
        if self.active_tree_object is not None and not active_tree: # if active object has been deleted
            need_update = True
        else:
            need_update = self.has_changed
        if active_tree: # if a tree object is locked
            split = layout.split(factor=0.8)
            split.label(text="active: {}".format(self.active_tree_object.name))
            op = split.operator("mtree.reset_active_tree_object", text='x')
            op.node_group_name = self.id_data.name
        if self.auto_update or active_tree:
            layout.prop(self, "auto_update")

        if need_update and not self.auto_update: # if tree needs to be updated
            ob = bpy.context.object
            if active_tree or ob is not None and ob.select_get() and ob.get("is_tree") is not None: # if a known tree is selected 
                prop_text = "Update Tree"
            else:
                prop_text = "Create Tree"
            op = layout.operator("object.mtree_execute_tree", text=prop_text) # will call ExecuteMtreeNodeTreeOperator.execute
            op.node_group_name = self.id_data.name # set name of node group to operator
        

        layout.prop(self, "mesh_type")
        layout.prop(self, "resolution")

        box = layout.box()
        box.prop(self, "create_leafs")
        if self.create_leafs:
            box.prop(self, "leaf_amount")
            box.prop(self, "leaf_max_radius")
            box.prop(self, "leaf_dupli_object")
            box.prop(self, "leaf_size")
            box.prop(self, "leaf_extremity_only")
            if not self.leaf_extremity_only:
                box.prop(self, "leaf_weight")
                box.prop(self, "leaf_spread")
                box.prop(self, "leaf_flatten")



        op = layout.operator("mtree.randomize_tree", text='randomize tree') # will call RandomizeTreeOperator.execute
        op.node_group_name = self.id_data.name # set name of node group to operator

def get_current_object(tree_ob_type, active_tree):
    '''' return active object if it is a valid tree and potentially the leaf emitter attached to it '''
    ob = bpy.context.object
    if active_tree is None: # if there is no active tree
        if ob is None or not ob.select_get(): # if ob is not selected or non existent
            return None, None
    else:
        ob = active_tree
            
    tree_ob = None
    leaf_ob = None
    if ob.get("is_tree") is not None: # if true then the active object is a tree
        if tree_ob is None and ob.type == tree_ob_type: # check if the object is of correct type
            tree_ob = ob
        for child in ob.children: # looking if the tree has a leaf emitter
            if child.get("is_leaf") is not None: # if true then the child is a leaf emitter
                leaf_ob = child
                break
        if ob.type != tree_ob_type: # if types are mismatched, delete ob
            bpy.data.objects.remove(ob, do_unlink=True)
    
    elif ob.get("is_leaf"): # if true then the active object is a leaf emitter
        leaf_ob = ob
        parent = ob.parent
        if parent is not None and parent.get("is_tree"): # if parent is a tree (it should be)
            tree_ob = parent
    
    
    return tree_ob, leaf_ob

def generate_tree_object(ob, tree, resolution, tree_property="is_tree"):
    ''' Create the tree mesh/object '''
    t0 = time.clock()
    verts, faces, radii, uvs = tree.build_mesh_data(resolution) # tree mesh data
    dt = time.clock() - t0
    print("mesh data creation : {}".format(dt))
    mesh = bpy.data.meshes.new("tree")
    material = None # material of tree object
    if ob == None: # if no object is specified, create one        
        ob = bpy.data.objects.new('tree', mesh) 
        bpy.context.scene.collection.objects.link(ob)
        ob[tree_property] = True # create custom object parameter to recognise tree object
    else: # delete old mesh data 
        material = ob.active_material
        old_mesh = ob.data
        ob.parent_type = "OBJECT" 
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

def generate_curve_object(ob, tree):
    ''' create the tree object as a curve '''
    
    if ob == None: # if no object is specified, create one
        curve_data = bpy.data.curves.new('Tree', type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.bevel_depth = 1
        curve_data.bevel_resolution = 0
        curve_data.fill_mode = 'FULL'
        ob = bpy.data.objects.new('Tree', curve_data)      
        bpy.context.scene.collection.objects.link(ob)
        ob["is_tree"] = True # create custom object parameter to recognise tree object
    else: # delete old mesh data 
        material = ob.active_material
        curve_data = ob.data
        curve_data.splines.clear()
    
    positions = [[]]
    radii = [[]]
    tree.stem.get_branches(positions, radii)
    for i in range(len(positions)):
        polyline = curve_data.splines.new('POLY')
        co = positions[i]
        radius = radii[i]
        polyline.points.add(len(radius)-1)
        polyline.points.foreach_set("co", co)
        polyline.points.foreach_set("radius", radius)
    
    return ob

def generate_leafs_object(tree, number, weight, max_radius, spread, flatten, extremity_only, ob=None, tree_ob=None):
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
        
    verts, faces = tree.get_leaf_emitter_data(number, weight, max_radius, spread, flatten, extremity_only) # emitter mesh data
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
                elif prop in {"mesh_type", "resolution"}:
                    return "tree_execution"
                elif prop in {"create_leafs", "leaf_max_radius", "leaf_amount", "leaf_weight", "leaf_spread", "leaf_flatten", "leaf_extremity_only"}:
                    leaf_emitter = True
                else:
                    particle_system = True
    if leaf_emitter:
        return "leafs_emitter"
    if particle_system:
        return "particle_system"

class ExecuteMtreeNodeTreeOperator(Operator):
    """Execute or update tree"""
    bl_idname = "object.mtree_execute_tree"
    bl_label = "Execute Mtree node tree"
    node_group_name = StringProperty()

    def execute(self, context):
        node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        node.execute()
        return {'FINISHED'}

class RandomizeTreeOperator(Operator):
    """Randomize all tree seeds"""
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

class ResetActiveTreeObject(Operator):
    """stop tracking tree"""
    bl_idname = "mtree.reset_active_tree_object"
    bl_label = "Reset Active Tree Object"
    
    node_group_name = StringProperty()

    def execute(self, context):
        parameters_node = [i for i in bpy.data.node_groups[self.node_group_name].nodes if i.bl_idname == "MtreeParameters"][0]
        parameters_node.active_tree_object = None
        parameters_node.has_changed = True
        return {'FINISHED'}