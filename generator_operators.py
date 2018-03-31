# Copyright 2016 Maxime Herpin
#
# ##### BEGIN GPL LICENSE BLOCK ######
# This file is part of Modular Tree.
#
# Modular Tree is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Modular Tree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Modular Tree.  If not, see <http://www.gnu.org/licenses/>.
# ##### END GPL LICENSE BLOCK #####


import bpy
from bpy.types import Operator
from bpy.props import StringProperty


# class MakeTreeFromNodes(Operator):
#     """makes a tree from a node group"""
#     bl_idname = "mod_tree.tree_from_nodes"
#     bl_label = " Make Tree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     node_group_name = StringProperty()
#     node_name = StringProperty()
#
#     def draw(self, context):
#         pass
#
#     def execute(self, context):
#         bpy.ops.object.delete(use_global=False)
#         print("tree")
#         print(self.node_name)
#         print(self.node_group_name)
#         # node = bpy.data.node_groups.get("NodeTree.002").nodes.get("BuildTree")
#         node = context.active_node.id_data.nodes.get("BuildTree")
#         node.execute()
#
#         # bpy.ops.object.subdivision_set(level=1)
#
#         return {'FINISHED'}
#
# class visualize_with_curves(Operator):
#     """makes a tree from a node group"""
#     bl_idname = "mod_tree.visualize"
#     bl_label = " visualize Tree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     node_group_name = StringProperty()
#     node_name = StringProperty()
#
#     def draw(self, context):
#         pass
#
#     def execute(self, context):
#         bpy.ops.object.delete(use_global=False)
#         print("tree")
#         print(self.node_name)
#         print(self.node_group_name)
#         node = bpy.data.node_groups.get("NodeTree.002").nodes.get("BuildTree")
#         node.execute()
#
#         # bpy.ops.object.subdivision_set(level=1)
#
#         return {'FINISHED'}


#
# class MakeTreeOperator(Operator):
#     """Make a tree"""
#     bl_idname = "mod_tree.add_tree"
#     bl_label = "Make Tree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         # this block saves everything and cancels operator if something goes wrong
#         display_logo()
#         messages, message_lvls, status = save_everything()
#         for i, message in enumerate(messages):
#             self.report({message_lvls[i]}, message)
#             return {status}
#
#         scene = context.scene
#         seed(scene.mtree_props.SeedProp)
#         alt_create_tree(self, scene.cursor_location)
#
#         return {'FINISHED'}
#
#
# class BatchTreeOperator(Operator):
#     """Batch trees"""
#     bl_idname = "mod_tree.batch_tree"
#     bl_label = "Batch Tree Generation"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         # this block saves everything and cancels operator if something goes wrong
#         display_logo()
#         messages, message_lvls, status = save_everything()
#         for i, message in enumerate(messages):
#             self.report({message_lvls[i]}, message)
#             return {status}
#
#         mtree_props = context.scene.mtree_props
#         trees = []
#         space = mtree_props.batch_space
#         seeds = []
#         if mtree_props.batch_group_name != "":
#             if mtree_props.batch_group_name not in bpy.data.groups:
#                 bpy.ops.group.create(name=mtree_props.batch_group_name)
#         for i in range(mtree_props.tree_number):
#             new_seed = randint(0, 1000)
#             while new_seed in seeds:
#                 new_seed = randint(0, 1000)
#             seeds.append(new_seed)
#             pointer = int(sqrt(mtree_props.tree_number))
#             pos_x = i % pointer
#             pos_y = i // pointer
#             seed(new_seed)
#             new_tree = alt_create_tree(self, Vector((-space * pointer / 2, -space * pointer / 2, 0)) + Vector((pos_x, pos_y, 0)) * space)
#             trees.append(new_tree)
#             if mtree_props.batch_group_name != "":
#                 bpy.ops.object.group_link(group=mtree_props.batch_group_name)
#         for tree in trees:
#             tree.select = True
#
#         return {'FINISHED'}
#
#
# class MakeTwigOperator(Operator):
#     """Creates a twig"""
#     bl_idname = "mod_tree.add_twig"
#     bl_label = "Create Twig"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         scene = context.scene
#         mtree_props = scene.mtree_props
#
#         # this block saves everything and cancels operator if something goes wrong
#         display_logo()
#         messages, message_lvls, status = save_everything(twig=True)
#         for i, message in enumerate(messages):
#             self.report({message_lvls[i]}, message)
#             return {status}
#
#         seed(mtree_props.TwigSeedProp)
#         twig = create_twig(scene.cursor_location)
#         twig.name = 'twig'
#
#         return {'FINISHED'}
#
#
# class UpdateTreeOperator(Operator):
#     """Update a tree"""
#     bl_idname = "mod_tree.update_tree"
#     bl_label = "Update Selected Tree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         # this block saves everything and cancels operator if something goes wrong
#         display_logo()
#         messages, message_lvls, status = save_everything()
#         for i, message in enumerate(messages):
#             self.report({message_lvls[i]}, message)
#             return {status}
#
#         mtree_props = context.scene.mtree_props
#
#         seed(mtree_props.SeedProp)
#         obj = bpy.context.active_object
#
#         try:
#             is_tree_prop = obj.get('is_tree')
#             has_arm_prop = obj.get('has_armature')
#             has_emitter_prop = obj.get('has_emitter')
#         except AttributeError:
#             self.report({'ERROR'}, "No active tree object!")
#             return {'CANCELLED'}
#
#         if is_tree_prop:
#             pos = obj.location
#             name = obj.name
#             scale = obj.scale
#             rot = obj.rotation_euler
#             alt_create_tree(self, pos)
#             ob = context.active_object  # this is the new object that has been set active by 'create_tree'
#             ob.scale = scale
#             ob.name = name
#             ob.rotation_euler = rot
#             ob.select = False
#             obj.select = True
#
#             if has_arm_prop:
#                 arm_pos = obj.parent.location
#                 arm_scale = obj.parent.scale
#                 arm_rot = obj.parent.rotation_euler
#                 obj.parent.select = True
#
#                 if mtree_props.create_armature:
#                     ob.parent.location = arm_pos
#                     ob.parent.scale = arm_scale
#                     ob.parent.rotation_euler = arm_rot
#                 else:
#                     ob.location = arm_pos
#                     ob.scale = arm_scale
#                     ob.rotation_euler = arm_rot
#
#             if has_emitter_prop:
#                 children = obj.children
#                 emitter = [i for i in children if i.get("emitter")][0]
#                 emitter.select = True
#
#             bpy.ops.object.delete(use_global=False)
#             ob.select = True
#
#         else:
#             self.report({'ERROR'}, "No active tree object!")
#             return {'CANCELLED'}
#
#         return {'FINISHED'}
#
#
# class UpdateTwigOperator(Operator):
#     """Update a twig"""
#     bl_idname = "mod_tree.update_twig"
#     bl_label = "Update Selected Twig"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         # this block saves everything and cancels operator if something goes wrong
#         display_logo()
#         messages, message_lvls, status = save_everything(twig=True)
#         for i, message in enumerate(messages):
#             self.report({message_lvls[i]}, message)
#             return {status}
#
#         mtree_props = context.scene.mtree_props
#
#         seed(mtree_props.SeedProp)
#         obj = bpy.context.active_object
#
#         try:
#             is_tree_prop = obj.get('is_tree')
#         except AttributeError:
#             self.report({'ERROR'}, "No active tree object!")
#             return {'CANCELLED'}
#
#         if is_tree_prop:
#             pos = obj.location
#             scale = obj.scale
#             rot = obj.rotation_euler
#             name = obj.name
#             bpy.ops.mod_tree.add_twig()
#             ob = bpy.context.active_object  # this is the new object that has been set active by 'create_tree'
#             ob.scale = scale
#             ob.location = pos
#             ob.name = name
#             ob.rotation_euler = rot
#             ob.select = False
#             obj.select = True
#             bpy.ops.object.delete(use_global=False)
#             ob.select = True
#
#         else:
#             self.report({'ERROR'}, "No active twig object!")
#             return {'CANCELLED'}
#
#         return {'FINISHED'}
#
#
# class SetupNodeTreeOperator(Operator):
#     """setup a node tree"""
#     bl_idname = "mod_tree.setup_node_tree"
#     bl_label = "Setup NodeTree"
#     bl_options = {"REGISTER", "UNDO"}
#
#     def execute(self, context):
#         mtree_props = context.scene.mtree_props
#         setup_node_tree(bpy.data.node_groups[mtree_props.node_tree])
#         return {'FINISHED'}