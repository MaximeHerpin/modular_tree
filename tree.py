from .tree_node import MTreeNode
from mathutils import Vector, Quaternion
from .geometry import random_tangent, build_module_rec
import numpy as np
from collections import deque
from random import random, randint, sample
from math import pi

class MTree:
    def __init__(self):
        self.stem = None # TreeNode - the first node of the tree
        self.verts = [] # list of Vector - the vertices of the tree
        self.faces = [] # list of list of int - the faces of the tree
    

    def build_mesh_data(self, resolution):
        verts = []
        faces = []
        weights = []
        uvs = []
        build_module_rec(self.stem, resolution, verts, faces, uvs, weights)
        return to_array(verts), faces, weights, uvs
    

    def create_object(self):
        pass
    

    def add_trunk(self, length, radius, end_radius, shape, resolution, randomness, axis_attraction, creator):
        self.stem = MTreeNode(Vector((0,0,0)), Vector((0,0,1)), radius, creator)
        self.stem.is_branch_origin = True
        remaining_length = length
        extremity = self.stem # extremity is always the current last node of the trunk
        while remaining_length > 0:
            if remaining_length < 1/resolution:
                resolution = 1/remaining_length # last last branch is shorter so that the trunk is exactly of required length
            tangent = random_tangent(extremity.direction)
            direction = extremity.direction + tangent * randomness / resolution # direction of new TreeNode
            course_correction = Vector((-extremity.position.x,-extremity.position.y,1/direction.z))
            direction += course_correction * axis_attraction
            direction.normalize()
            position = extremity.position + extremity.direction / resolution # position of new TreeNode
            rad = radius * (remaining_length/length)**shape + (1 - remaining_length/length) * end_radius# radius of new TreeNode
            new_node = MTreeNode(position, direction, rad, creator) # new TreeNode
            extremity.children.append(new_node) # Add new TreeNode to extremity's children
            extremity = new_node # replace extremity by new TreeNode
            remaining_length -= 1/resolution


    def grow(self, length, shape_start, shape_end, shape_convexity, resolution, randomness, split_proba, split_angle,
             split_radius, split_flatten, end_radius, gravity_strength, floor_avoidance, can_spawn_leaf, creator, selection):
        grow_candidates = []
        self.stem.get_grow_candidates(grow_candidates, selection) # get all leafs of valid creator

        branch_length = 1/resolution # branch length is use multiple times so best to calculate it once

        def shape_length(x):
            ''' returns y=f(x) so that f(0)=shape_start, f(1)=shape_end and f(0.5) = shape_convexity+1/2(shape_start+shape_end)'''
            return -4*shape_convexity*x*(x-1) + x*shape_end + (1-x)*shape_start
        
        for node in grow_candidates:
            node.growth = 0
            node.growth_goal = max(0.001, length * shape_length(node.position_in_branch)) # add length to node growth goal
            node.growth_radius = node.radius

        grow_candidates = deque(grow_candidates) # convert grow_candidates to deque for performance (lots of adding/removing last element)

        while len(grow_candidates) > 0: # grow all candidates until there are none (all have grown to their respective length)
            node = grow_candidates.popleft()
            children_number = 1 if random() > split_proba or node.is_branch_origin else 2 # if 1 the branch grows normally, if more than 1 the branch forks into more branches
            tangent = random_tangent(node.direction)
            if tangent.z < 0 or children_number > 1:
                tangent.z *= (1-split_flatten)
                tangent.normalize()
            for i in range(children_number):
                deviation = randomness if children_number==1 else split_angle # how much the new direction will be changed by tangent
                direction = node.direction.lerp(tangent * (i-.5)*2, deviation) # direction of new node
                direction += Vector((0,0,-1)) * gravity_strength / 10 / resolution # apply gravity
                if floor_avoidance != 0:
                    below_ground = -1 if floor_avoidance < 0 else 1 # if -1 then the branches must stay below ground, if 1 they must stay above ground
                    distance_from_floor = max(.01, abs(node.position.z))
                    direction_toward_ground = max(0, - direction.z * below_ground) # get how much the branch is going towards the floor
                    floor_avoidance_strength = direction_toward_ground * .3 / distance_from_floor * floor_avoidance

                    if floor_avoidance_strength > .1 * (1+floor_avoidance): # if the branch is too much towards the floor, break it 
                        break
                    direction += Vector((0,0,1)) * floor_avoidance_strength
                direction.normalize() 
                if i == 0:
                    position = node.position + direction * branch_length # position of new node
                else:
                    t = (tangent - tangent.project(node.direction)).normalized()
                    position = (node.position + node.children[0].position)/2 + t*node.radius
                growth = min(node.growth_goal, node.growth + branch_length) # growth of new node

                radius = node.growth_radius * ((1- node.growth / node.growth_goal) + end_radius * node.growth / node.growth_goal) # radius of new node
                if i > 0:
                    radius *= split_radius # forked branches have smaller radii
                child = MTreeNode(position, direction, radius, creator)
                child.growth_goal = node.growth_goal
                child.growth = growth
                child.growth_radius = node.growth_radius if i == 0 else node.growth_radius * split_radius
                child.can_spawn_leaf = can_spawn_leaf
                if i > 0:
                    child.is_branch_origin = True
                node.children.append(child)
                if (growth < node.growth_goal):
                    grow_candidates.append(child) # if child can still grow, add it to the grow candidates

   
    def split(self, amount, angle, max_split_number, radius, min_height, flatten, creator, selection):
        split_candidates = []
        self.stem.set_positions_in_branches()
        self.stem.get_split_candidates(split_candidates, selection, min_height)
        
        amount = min(amount, len(split_candidates))
        split_candidates = sample(split_candidates, amount)
        for node in split_candidates:
            n_children = randint(1,max_split_number)
            tangent = random_tangent(node.direction)
            flatten_tangent = tangent.copy()
            flatten_tangent.z = 0
            tangent = tangent.lerp(flatten_tangent, flatten)
            tangent.normalize()
            rot = Quaternion(node.direction, 2*pi/n_children)
            for i in range(n_children):
                t = node.position_in_branch
                direction = node.direction.lerp(tangent, angle * (1-t/2)).normalized()
                position = (node.position + node.children[0].position)/2
                position += (tangent - tangent.project(node.direction)).normalized() * node.radius
                rad = node.radius * radius
                child = MTreeNode(position, direction, rad, creator)
                child.position_in_branch = node.position_in_branch
                child.is_branch_origin = True
                child.can_spawn_leaf = False
                node.children.append(child)
                tangent = rot @ tangent

    
    def add_branches(self, amount, angle, max_split_number, radius, end_radius, min_height, length,
                     shape_start, shape_end, shape_convexity, resolution, randomness,
                     split_proba, split_flatten, gravity_strength, floor_avoidance, can_spawn_leaf, creator, selection):
        split_creator = creator - 0.5
        split_selection = selection
        grow_selection = creator - 0.5
        grow_creator = creator
        self.split(amount, angle, max_split_number, radius, min_height, split_flatten, split_creator, split_selection)
        self.grow(length, shape_start, shape_end, shape_convexity, resolution, randomness, split_proba, 0.3, 0.9,
                  split_flatten, end_radius, gravity_strength, floor_avoidance, can_spawn_leaf, grow_creator, grow_selection)


    def roots(self, length, resolution, split_proba, randomness, creator):
        if len(self.stem.children) == 0: # roots can only be added on a trunk on non 0 length
            return
        
        roots_origin = MTreeNode(self.stem.position, -self.stem.direction, self.stem.radius, -1)
        roots_origin.is_branch_origin = True
        self.stem.children.append(roots_origin) # stem is set as branch origin, so it cannot be splitted by split function. second children of stem will then always be root origin

        self.grow(length, 1, 1, 0, resolution, randomness, split_proba, .5, .6, 0, 0, -.1, -1, False, creator, -1)


    def get_leaf_emitter_data(self, number, weight, max_radius, spread, flatten, extremity_only):
        leaf_candidates = []
        self.stem.get_leaf_candidates(leaf_candidates, max_radius)
        if not extremity_only:
            if (number > len(leaf_candidates)):
                factor = number // len([i for i in leaf_candidates if not i[-1]]) # remove extremities from factor because they won't participate in candidate addition
                add_candidates(leaf_candidates, factor)
            leaf_candidates = sample(leaf_candidates, number)
        else:
            leaf_candidates = [i for i in leaf_candidates if i[-1]]
        verts = []
        faces = []

        for position, direction, length, radius, is_end in leaf_candidates:
            tangent = Vector((0,0,1)).cross(direction).normalized()
            if not is_end: # only change direction when leaf is not at a branch extremity
                tangent = (randint(0,1) * 2 - 1) * tangent # randomize sign of tangent
                direction = direction.lerp(tangent, spread)
                direction.z *= (1-flatten)
                direction.z -= weight
                direction.normalize()
            x_axis = direction.orthogonal()
            y_axis = direction.cross(x_axis)
            v1 = position + x_axis * .01
            v3 = position + y_axis * .01
            v2 = position - x_axis * .01
            n_verts = len(verts)
            verts.extend([v3, v2, v1])
            faces.append((n_verts, n_verts+1, n_verts+2))
        
        return verts, faces


    def twig(self, radius, length, branch_number, randomness, resolution, gravity_strength, flatten):
        self.stem = MTreeNode(Vector((0,0,0)), Vector((1,0,0)), radius*.1, 0)
        self.grow(1, 1, 1, 0, resolution, randomness/2/resolution, 0, .2, 0, 0, 0, .1,0, True, 1, 0)
        self.add_branches(branch_number, .5, 2, .7, .1, 0, length*.7, .5, .5, 0, resolution, randomness/resolution, .1/resolution, flatten, gravity_strength/resolution, 0, True, 2, 1)

        leaf_candidates = []
        self.stem.get_leaf_candidates(leaf_candidates, radius)
        return [i for i in leaf_candidates if i[-1]]


def to_array(vectors):
    n = len(vectors)
    result = np.zeros((n, 3))
    for i, v in enumerate(vectors):
        result[i] = v.xyz
    return result


def add_candidates(leaf_candidates, dupli_number):
    ''' create new leaf candidates by interpolating existing ones '''
    new_candidates = []

    for position, direction, length, radius, is_end in leaf_candidates:
        if is_end: # no new candidate can be created from end_leaf
            continue
        for i in range(dupli_number):
            pos = position + direction*length * (i+1)/(dupli_number+2)
            new_candidates.append((pos, direction, length, radius, is_end))
    leaf_candidates.extend(new_candidates)

