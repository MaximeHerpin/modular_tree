# Copyright 2016 Maxime Herpin, Jake Dube
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

from mathutils import Vector, Matrix

import bpy

# Material node_tree
Bark_Nodes, Bark_Links = ([('NodeReroute', Vector((-580.0, 460.0)), 'Reroute', ''),
    ('ShaderNodeSeparateXYZ', Vector((-560.0, 140.0)), 'Separate XYZ', ''),
    ('ShaderNodeMixRGB', Vector((-380.0, 140.0)), 'Mix', ''),
    ('ShaderNodeTexNoise', Vector((-560.0, 0.0)), 'Noise Texture', ''),
    ('ShaderNodeVectorMath', Vector((-740.0, 0.0)), 'Vector Math', ''),
    ('ShaderNodeObjectInfo', Vector((-940.0, -140.0)), 'Object Info', ''),
    ('ShaderNodeTexImage', Vector((-220.0, 440.0)), 'Bark texture', 'Bark texture'),
    ('ShaderNodeMapping', Vector((-560.0, 440.0)), 'Mapping', ''),
    ('ShaderNodeMapping', Vector((-561.4127807617188, 749.75927734375)), 'Mapping.001', ''),
    ('ShaderNodeTexImage', Vector((-213.890625, 727.4722900390625)), 'Bark texture.001', 'Bark texture'),
    ('ShaderNodeTexCoord', Vector((-935.7615966796875, 212.72984313964844)), 'Texture Coordinate', ''),
    ('NodeReroute', Vector((280.0, 140.0)), 'Reroute.003', ''),
    ('ShaderNodeOutputMaterial', Vector((1580.0, 440.0)), 'Material Output', ''),
    ('ShaderNodeTexNoise', Vector((880.0, 540.0)), 'Noise Texture.001', ''),
    ('ShaderNodeBrightContrast', Vector((1060.0, 540.0)), 'Bright/Contrast', ''),
    ('NodeReroute', Vector((360.0, -20.0)), 'Reroute.001', ''),
    ('ShaderNodeInvert', Vector((880.0, 300.0)), 'Invert', ''),
    ('NodeReroute', Vector((960.0, -20.0)), 'Reroute.002', ''),
    ('ShaderNodeMixRGB', Vector((300.0, 300.0)), 'Mix.002', ''),
    ('ShaderNodeValToRGB', Vector((620.0, 300.0)), 'moss height', 'moss height'),
    ('ShaderNodeMath', Vector((460.0, 300.0)), 'Math.001', ''),
    ('ShaderNodeMixRGB', Vector((1040.0, 300.0)), 'moss color', 'moss color'),
    ('ShaderNodeMixRGB', Vector((1240.0, 440.0)), 'color variation', 'color variation'),
    ('ShaderNodeAttribute', Vector((-220.0, 900.0)), 'Attribute', ''),
    ('ShaderNodeMixRGB', Vector((-3.890625, 533.7361450195312)), 'Mix.001', ''),
    ('ShaderNodeBsdfDiffuse', Vector((1400.0, 440.0)), 'Diffuse BSDF', '')],
    [([10, 'Object'], [4, 'Vector']), ([10, 'Generated'], [1, 'Vector']), ([1, 'Z'], [2, 'Color1']), ([3, 'Fac'], [2, 'Color2']), ([19, 'Color'], [16, 'Color']), ([16, 'Color'], [21, 'Fac']), ([17, 'Output'], [21, 'Color1']), ([20, 'Value'], [19, 'Fac']), ([2, 'Color'], [18, 'Color1']), ([18, 'Color'], [20, 'Value']), ([11, 'Output'], [18, 'Color2']), ([0, 'Output'], [13, 'Vector']), ([22, 'Color'], [25, 'Color']), ([21, 'Color'], [22, 'Color1']), ([13, 'Fac'], [14, 'Color']), ([14, 'Color'], [22, 'Fac']), ([11, 'Output'], [15, 'Input']), ([15, 'Output'], [17, 'Input']), ([10, 'UV'], [7, 'Vector']), ([7, 'Vector'], [6, 'Vector']), ([4, 'Vector'], [3, 'Vector']), ([4, 'Vector'], [0, 'Input']), ([5, 'Location'], [4, 'Vector']), ([8, 'Vector'], [9, 'Vector']), ([10, 'Generated'], [8, 'Vector']), ([9, 'Color'], [24, 'Color2']), ([24, 'Color'], [11, 'Input']), ([23, 'Fac'], [24, 'Fac']), ([6, 'Color'], [24, 'Color1']), ([25, 'BSDF'], [12, 'Surface'])])


Leaf_Nodes, Leaf_Links = ([('ShaderNodeMapping', Vector((-1020.0, 440.0)), 'Mapping', ''),
     ('ShaderNodeTexCoord', Vector((-1200.0, 440.0)), 'Texture Coordinate', ''),
     ('ShaderNodeTexImage', Vector((-660.0, 440.0)), 'Image Texture', ''),
     ('NodeReroute', Vector((-460.0, 540.0)), 'Reroute', ''),
     ('ShaderNodeSeparateRGB', Vector((-660.0, 140.0)), 'Separate RGB', ''),
     ('ShaderNodeOutputMaterial', Vector((280.0, 500.0)), 'Material Output', ''),
     ('ShaderNodeBsdfTransparent', Vector((-80.0, 380.0)), 'Transparent BSDF', ''),
     ('ShaderNodeBsdfTranslucent', Vector((-260.0, 500.0)), 'Translucent BSDF', ''),
     ('ShaderNodeAddShader', Vector((-80.0, 500.0)), 'Add Shader', ''),
     ('ShaderNodeBsdfDiffuse', Vector((-260.0, 380.0)), 'Diffuse BSDF', ''),
     ('ShaderNodeMixShader', Vector((100.0, 500.0)), 'Mix Shader', ''),
     ('ShaderNodeHueSaturation', Vector((-460.0, 440.0)), 'Hue Saturation Value', ''),
     ('NodeReroute', Vector((60.0, 540.0)), 'Reroute.001', ''),
     ('ShaderNodeMixRGB', Vector((-820.0, 140.0)), 'Mix', ''),
     ('ShaderNodeObjectInfo', Vector((-1000.0, 140.0)), 'Object Info', '')],
     [([7, 'BSDF'], [8, 'Shader']), ([8, 'Shader'], [10, 'Shader']), ([9, 'BSDF'], [8, 'Shader']), ([11, 'Color'], [9, 'Color']), ([0, 'Vector'], [2, 'Vector']), ([1, 'UV'], [0, 'Vector']), ([11, 'Color'], [7, 'Color']), ([6, 'BSDF'], [10, 'Shader']), ([2, 'Color'], [11, 'Color']), ([13, 'Color'], [4, 'Image']), ([4, 'R'], [11, 'Hue']), ([10, 'Shader'], [5, 'Surface']), ([12, 'Output'], [10, 'Fac']), ([2, 'Alpha'], [3, 'Input']), ([3, 'Output'], [12, 'Input']), ([14, 'Random'], [13, 'Fac'])])


def build_bark_material(mat_name):
    if not bpy.context.scene.render.engine == 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    mat = bpy.data.materials.new(name=mat_name)
    mat.diffuse_color = (0.214035, 0.0490235, 0.0163952)
    mat.specular_color = (0.0469617, 0.0469617, 0.0469617)
    mat.specular_hardness = 10
    mat.use_nodes = True
    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Diffuse BSDF'))
    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Material Output'))

    for (n_type, loc, name, label) in Bark_Nodes:
        new_node = mat.node_tree.nodes.new(n_type)
        new_node.location = loc
        new_node.name = name
        new_node.label = label

    nodes = mat.node_tree.nodes
    nodes['Mapping'].scale = (15, 15, 15)
    nodes['Mapping.001'].scale = (20, 20, 20)
    nodes["Bark texture.001"].projection = 'BOX'
    nodes['Attribute'].attribute_name = "Col"
    nodes["Noise Texture"].inputs[1].default_value = 2
    nodes["Noise Texture"].inputs[2].default_value = 10
    nodes["Mix"].blend_type = 'MULTIPLY'
    nodes["Mix.002"].blend_type = 'MULTIPLY'
    nodes["Mix.002"].inputs[0].default_value = 0.95
    nodes["Math.001"].operation = 'MULTIPLY'
    nodes["Math.001"].inputs[1].default_value = 30
    nodes["moss height"].color_ramp.elements[0].position = 0.3
    nodes["moss height"].color_ramp.elements[1].position = 0.5
    nodes["Noise Texture.001"].inputs[1].default_value = 0.7
    nodes["Noise Texture.001"].inputs[2].default_value = 10
    nodes["Bright/Contrast"].inputs[2].default_value = 5
    nodes["moss color"].blend_type = 'MULTIPLY'
    nodes["moss color"].inputs[2].default_value = [0.342, 0.526, 0.353, 1.0]
    nodes["color variation"].blend_type = 'OVERLAY'
    nodes["color variation"].inputs[2].default_value = [0.610, 0.648, 0.462, 1.0]

    mat.node_tree.links.new(nodes["Texture Coordinate"].outputs[3], nodes["Vector Math"].inputs[1])
    links = mat.node_tree.links
    for f, t in Bark_Links:
        from_node = mat.node_tree.nodes[f[0]]
        to_node = mat.node_tree.nodes[t[0]]
        links.new(from_node.outputs[f[1]], to_node.inputs[t[1]])
    return mat


def build_leaf_material(mat_name):
    if not bpy.context.scene.render.engine == 'CYCLES':
        bpy.context.scene.render.engine = 'CYCLES'

    mat = bpy.data.materials.new(name=mat_name)
    mat.diffuse_color = (0.081, 0.548, 0.187)
    mat.specular_color = (0.0469617, 0.0469617, 0.0469617)
    mat.specular_hardness = 10
    mat.use_nodes = True
    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Diffuse BSDF'))
    mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Material Output'))

    for (n_type, loc, name, label) in Leaf_Nodes:
        new_node = mat.node_tree.nodes.new(n_type)
        new_node.location = loc
        new_node.name = name
        new_node.label = label
    nodes = mat.node_tree.nodes
    nodes["Mix"].inputs[1].default_value = (.4, .4, .4, 1)
    nodes["Mix"].inputs[2].default_value = (.6, .6, .6, 1)
    links = mat.node_tree.links
    mat.node_tree.links.new(nodes["Translucent BSDF"].outputs[0], nodes["Add Shader"].inputs[1])
    mat.node_tree.links.new(nodes["Add Shader"].outputs[0], nodes["Mix Shader"].inputs[2])
    for f, t in Leaf_Links:
        from_node = mat.node_tree.nodes[f[0]]
        to_node = mat.node_tree.nodes[t[0]]
        links.new(from_node.outputs[f[1]], to_node.inputs[t[1]])

    return mat