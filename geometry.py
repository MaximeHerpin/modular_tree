from mathutils import Vector, Quaternion
from random import random
from math import pi, sqrt, inf, cos, sin
import numpy as np

def random_tangent(dir):
    v = random_on_unit_sphere()
    return v.cross(dir)

def random_on_unit_sphere():
    return Vector((random()-.5, random()-.5, random()-.5)).normalized()


def build_module_rec(node, resolution, verts, faces, uvs, weights, input_loop=[], uv_height=0):
    is_origin = False # true if thare are no input loop
    if len(node.children) == 0:
        if len(input_loop) > 0:
            faces.append(input_loop)
            n = len(input_loop)
            uvs.append([Vector((cos(i/(n-1)), sin(i/(n-1)))) for i in range(n)])
        return

    rot_dir = Vector((0,0,1)).rotation_difference(node.direction) # transformation from y_up space to directio_up space
    rot_dir_inv = rot_dir.inverted() # inverse transformation
    module_verts = [] # verts created by the module
    n_verts = len(verts) # number of vertices before adding module
    if (input_loop == []):
        is_origin = True
        module_verts = make_circle(Vector((0,0,0)), Vector((0,0,1)), node.radius, resolution)
        input_loop = [i for i in range(resolution)]
        n_verts += resolution
    else:
        input_tangent = rot_dir_inv @ (verts[input_loop[0]] - node.position)
        input_angle_offset = int(input_tangent.xy.angle_signed(Vector((1,0))) / 2/pi * resolution)
        if input_angle_offset != 0:
            input_loop = rotate(input_loop, input_angle_offset)
    output_loops = [] # input_loop for each child
    output_resolutions = [resolution]
    extremity = node.children[0]
    extremity_height = (extremity.position - node.position).magnitude
    extremity_position = rot_dir_inv @ (extremity.position - node.position)
    extremity_direction = rot_dir_inv @ extremity.direction
    extremity_verts = make_circle(extremity_position, extremity_direction, extremity.radius, resolution) # verts of output loop
    extremity_loop = [i for i in range(n_verts, n_verts + len(extremity_verts))] # indexes of output_loops
    output_loops.append(extremity_loop)
    module_verts += extremity_verts 
    n_verts += resolution
    filling_loop_indexes = [True]*resolution # False when a vert of the loop is replaces by a children loop
    loop_up = [-1]*resolution # loop for faces in the upper part of the module
    loop_down = [-1]*resolution # loop for faces in the lower part of the module
    
    for child in node.children[1:]:
        if is_origin: # if true then this child is the roots origin
            break
        max_child_res = resolution // (len(node.children) - 1) # max resolution of childs
        child_dir = rot_dir_inv @ child.direction # child direction in y_up space
        child_dir.normalize() #is this needed ?
        child_pos = rot_dir_inv @ (child.position - node.position)
        child_resolution = get_resolution(node.radius, child.radius, resolution, max_child_res)
        child_verts = make_circle_2(child_pos, child_dir, child.radius, Vector((0,0,-1)), child_resolution)
        child_loop = [i for i in range(n_verts, n_verts + child_resolution)] # input loop for child
        output_loops.append(child_loop)
        output_resolutions.append(child_resolution)
        wrap_circle(child_verts, child_dir, Vector((0,0,1)), node.radius) # wrap child verts around module cylinder
        
        angle_offset = int(((-Vector((1,0)).angle_signed(child_dir.xy)/2/pi)%1) * resolution + .5) # offset in index necessary for the loops of child to be aligned with the base loop
        for i in range(-len(child_verts)//4, len(child_verts)//4 + 1):
            filling_loop_indexes[(i + angle_offset)%resolution] = False
            loop_down[(i + angle_offset)%resolution] = n_verts + i%len(child_verts)
            loop_up[(i + angle_offset)%resolution] = n_verts + (-(i + len(child_verts)//2))%len(child_verts)
        module_verts.extend(child_verts)
        n_verts += len(child_verts)

    filling_loop = make_circle(extremity_position/2, Vector((0,0,1)), (node.radius + extremity.radius)/2, resolution)
    index = 0
    for i in range(len(filling_loop)):
        if filling_loop_indexes[i]:
            loop_down[i] = n_verts + index
            loop_up[i] = n_verts + index
            index += 1
            
    filling_loop = [filling_loop[i] for i in range(len(filling_loop)) if filling_loop_indexes[i]]
    module_verts.extend(filling_loop)
    faces.extend(bridge(input_loop, loop_down) + bridge(loop_up, extremity_loop))
    if is_origin:
        #weights.append((input_loop, 0))
        weights.append(([i for i in range(resolution, len(module_verts) - resolution)], node.radius))
    else:
        weights.append(([i for i in range(len(verts), len(verts) + len(module_verts))], node.radius))
    verts.extend([rot_dir @ v + node.position for v in module_verts])
    uv_height = uv_loops(input_loop, loop_down, uv_height, uvs, verts, node.radius, len(node.children)==1)
    uv_height = uv_loops(loop_up, extremity_loop, uv_height, uvs, verts, extremity.radius, len(node.children)==1)
    for i, child in enumerate(node.children): # recursively call function on all children
        if is_origin and i == 1: # if true then this child is the roots origin
            build_module_rec(child, resolution, verts, faces, uvs, weights, list(reversed(input_loop)), uv_height)
        else:
            build_module_rec(child, output_resolutions[i], verts, faces, uvs, weights, output_loops[i], uv_height)


def bridge(l1, l2):
    faces = []
    n = len(l1)
    for i in range(n):
        faces.append([l2[i], l1[i], l1[(i+1)%n], l2[(i+1)%n]])
    return faces


def uv_loops(l1, l2, height_offset, uvs, verts, radius, simple_branch):
    n = len(l1)
    h = height_offset
    max_length = 0
    if simple_branch:
        max_length =length = (verts[l2[0]] - verts[l1[0]]).magnitude / 2 / pi / radius
        
    for i in range(n):
        if not simple_branch:
            length = (verts[l2[i]] - verts[l1[i]]).magnitude / 2 / pi / radius
            max_length = max(max_length, length)
        uvs.append([Vector((i/n, h+length)), Vector((i/n, h)),
                    Vector(((i+1)/n, h)), Vector(((i+1)/n, h+length))])
    
    return height_offset + max_length

def rotate(l, n):
    return l[-n:] + l[:-n]


def make_circle(pos, dir, radius, resolution):
    angle = 2*pi / resolution
    rot1 = Quaternion((0, 0, 1), angle) # rotation increment after each loop
    rot2 = Vector((0,0,1)).rotation_difference(dir) # rotation to make circle face direction
    result = []
    v = Vector((radius, 0, 0))
    for i in range (resolution):
        result.append(rot2 @ v + pos)
        v = rot1 @ v    
    return result


def projected_angle(direction, v):
    v = v.project(direction).normalized()
    return 


def make_circle_2(pos, dir, radius, tangent, resolution):
    angle = 2*pi / resolution
    tangent = (tangent - tangent.project(dir)).normalized()
    rot = Quaternion(dir, angle) # rotation increment after each loop
    result = []
    v = tangent * radius
    for i in range (resolution):
        result.append(v + pos)
        v = rot @ v
    return result
   

def wrap_circle(circle, circle_dir, wrap_dir, wrap_rad):
    tangent = circle_dir.cross(wrap_dir)
    for v in circle:
        c = abs(v.dot(tangent))
        v -= ((1-sqrt(1 - c**2)) * wrap_rad) * circle_dir
    

def to_array(vectors):
    n = len(vectors)
    result = np.zeros((n, 3))
    for i, v in enumerate(vectors):
        result[i] = v.xyz
    return result


def get_resolution(base_radius, child_radius, base_resolution, max_resolution):
    n = min(max_resolution, int(child_radius / base_radius * base_resolution))
    if n % 2 == 1:
        n += 1
    if n % 4 != 0:
        n = int(n/4 + .5) * 4
    if n<4:
        n=4
    return n