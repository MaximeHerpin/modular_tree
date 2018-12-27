import os
import json
from collections import deque
import bpy
from mathutils import Vector
from bpy.types import NodeTree, Node, NodeSocket, Operator, Object
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from bpy.props import IntProperty, FloatProperty, EnumProperty, BoolProperty, StringProperty, PointerProperty
from .base_node import BaseNode

def get_preset_list(self, context): # used to get all presets
    folder_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    folder_path = os.path.join(folder_path, "presets")
    presets_names = []
    for f in os.listdir(folder_path):
        if f.endswith(".json"):
            presets_names.append(f[:-5])        
    return [(i, i, "") for i in presets_names]

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class MtreeNodeTree(NodeTree):
    '''Mtree node editor'''
    bl_idname = 'mtree_node_tree'
    bl_label = "Mtree Node Tree"
    bl_icon = 'NODETREE'

    preset_to_load = EnumProperty(name = "Presets", items = get_preset_list, description = "presets")
    preset_to_save = StringProperty(name="name", default="default tree")

    def save_as_json(self):
        ''' save node tree information in a json file '''
        folder_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        folder_path = os.path.join(folder_path, "presets")
        path = os.path.join(folder_path , self.preset_to_save + ".json")
        with open(path, 'w') as outfile: # write to preset
            node_tree_data = {} # the disctionary that will be dumped in the preset
            node_tree_data["nodes"] = [] # the list of nodes
            node_tree_data["links"] = [] # the list of links between the nodes

            nodes = [i for i in self.nodes if i.bl_idname == "MtreeTrunk"] # list of nodes in rigth order (from trunk to tree parameter)
            extremities = deque(nodes)
            while len(extremities) > 0:
                node = extremities.popleft()
                for output in node.outputs:
                    for link in output.links:
                        child = link.to_node
                        if not child in nodes:
                            extremities.append(child)
                            nodes.append(child)
            nodes += [i for i in self.nodes if i.bl_idname == "MtreeParameters"]

            for node in nodes: # populating the node list
                node_data = {}
                if node.bl_idname != "MtreeTwig": # twig nodes are not saved (mayby they should ?)
                    node_data["bl_idname"] = node.bl_idname
                    node_data["name"] = node.name
                    node_data["outputs_count"] = len(node.outputs)
                    node_data["location"] = [i for i in node.location]
                    for prop in node.properties:
                        if type(getattr(node, prop)) != Object:
                            node_data[prop] = getattr(node, prop)            
                node_tree_data["nodes"].append(node_data)

            for link in self.links: # populating the link list
                link_data = {}
                link_data["from_node"] = link.from_node.name
                link_data["to_node"] = link.to_node.name
                link_data["output_index"] = int(link.from_socket.identifier)
                node_tree_data["links"].append(link_data)
            
            json.dump(node_tree_data, outfile, indent=4)
        self.preset_to_save = self.preset_to_load # set preset name to the preset just loaded
            
    def load_json(self):
        ''' retrieve and replace a node tree data from a json file '''
        folder_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        folder_path = os.path.join(folder_path, "presets")
        path = os.path.join(folder_path , self.preset_to_load + ".json")
        with open(path) as f:
            node_tree_data = json.load(f) # new node tree data
            self.nodes.clear() # remove all nodes of node tree
            last_node_location = Vector((0,0)) # keep track of position of last node added
            for node in node_tree_data["nodes"]:
                bl_idname = node["bl_idname"]
                new_node = self.nodes.new(bl_idname)
                last_node_location += Vector((200, 0)) # offset last node position, which will be the position of new node 
                new_node.location = last_node_location
                
                outputs_count = node["outputs_count"]
                for i in range(outputs_count-1): # adding outputs
                    self.outputs.new('TreeSocketType', str(i))

                for prop in [key for key in node.keys() if key not in {"bl_idname", "outputs_count"}]: # enumerating all property names of node except bl_idname
                    prop_value = node[prop]
                    setattr(new_node, prop, prop_value) # set property value to new node
            
            for link in node_tree_data["links"]:
                from_node = self.nodes[link["from_node"]]
                to_node = self.nodes[link["to_node"]]
                output_index = link["output_index"]
                self.links.new(from_node.outputs[output_index], to_node.inputs[0])
                


class TreeSocket(NodeSocket):
    """Tree socket type"""
    bl_idname = "TreeSocketType"
    bl_label = "Tree Socket"

    default_value = None
    def draw(self, context, layout, node, text):
        pass

    def draw_color(self, context, node):
        return .125, .571, .125, 1


class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'mtree_node_tree'


# all categories in a list
node_categories = [
    # identifier, label, items list
    MyNodeCategory('NODES', "Nodes", items=[
        NodeItem("MtreeTrunk"),
        NodeItem("MtreeParameters"),
        NodeItem("MtreeGrow"),
        NodeItem("MtreeSplit"),
        NodeItem("MtreeBranch"),
        NodeItem("MtreeTwig")
    ]),
]


class MtreeSaveLoadPreset(Operator):
    """save Mtree node tree as preset"""
    bl_idname = "mtree.save_preset"
    bl_label = " Save or Load Preset"
    bl_options = {"REGISTER", "UNDO"}
 
    node_group_name = StringProperty()
    load = BoolProperty(default=False)

    def execute(self, context):        
        node_tree = bpy.data.node_groups[self.node_group_name] # get node tree
        if self.load:
            node_tree.load_json() # load json preset
        else:
            node_tree.save_as_json() # save preset as json
        return {'FINISHED'}


class MtreePanel(bpy.types.Panel):
    bl_idname = "mtree_settings_panel"
    bl_label = "Mtree Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Mtree"

    @classmethod
    def poll(cls, context):
        tree = cls.getTree()
        if tree is None: return False # only display panel when a node group is selected
        return tree.bl_idname == "mtree_node_tree" # only display panel when selected node group is an Mtree node tree

    def draw(self, context):
        layout = self.layout

        tree = context.space_data.edit_tree

        box = layout.box()
        box.label(text="load preset")
        box.prop(tree, "preset_to_load")
        op = box.operator("mtree.save_preset", text='load preset') # will call MtreeSavePreset.execute
        op.node_group_name = tree.name #set node group name as curent node tree name
        op.load = True # set action to load

        box = layout.box()
        box.label(text="save preset")
        box.prop(tree, "preset_to_save")
        op = box.operator("mtree.save_preset", text='save preset') # will call MtreeSavePreset.execute
        op.node_group_name = tree.name #set node group name as curent node tree name
        op.load = False # set action to save

    @classmethod
    def getTree(cls):
        return bpy.context.space_data.edit_tree

classes = [
    MtreeNodeTree,
    TreeSocket,
    MtreePanel,
    MtreeSaveLoadPreset,
]




