from .tree_node import MTreeNode
from mathutils import Vector, Quaternion
from .geometry import random_tangent, build_module_rec
import numpy as np
from collections import deque
from random import random, randint
from math import pi

class MTree:
    def __init__(self):
        self.stem = None # TreeNode - the first node of the tree
        self.verts = [] # list of Vector - the vertices of the tree
        self.faces = [] # list of list of int - the faces of the tree
    

    def build_mesh_data(self):
        verts = []
        faces = []
        # extremities = deque([self.stem])
        # while len(extremities) != 0:
        #     extremity = extremities.popleft()
        #     verts.append(extremity.position)
        #     for child in extremity.children:
        #         extremities.append(child)
        build_module_rec(self.stem, 16, verts, faces)
        return to_array(verts), faces
    

    def create_object(self):
        pass
    

    def add_trunk(self, length, radius, shape, resolution, randomness, creator):
        self.stem = MTreeNode(Vector((0,0,0)), Vector((0,0,1)), radius, creator)
        remaining_length = length
        extremity = self.stem # extremity is always the current last node of the trunk
        while remaining_length > 0:
            if remaining_length < 1/resolution:
                resolution = 1/remaining_length # last last branch is shorter so that the trunk is exactly of required length
            tangent = random_tangent(extremity.direction)
            direction = extremity.direction + tangent * randomness / resolution # direction of new TreeNode
            position = extremity.position + extremity.direction / resolution # position of new TreeNode
            rad = radius * (remaining_length/length)**shape # radius of new TreeNode
            new_node = MTreeNode(position, direction, rad, creator) # new TreeNode
            extremity.children.append(new_node) # Add new TreeNode to extremity's children
            extremity = new_node # replace extremity by new TreeNode
            remaining_length -= 1/resolution


    def grow(self, lenght, shape_start, shape_end, shape_convexity, resolution, randomness, split_proba, split_angle, split_radius, creator):
        grow_candidates = []
        min_height, max_height = self.stem.get_grow_candidates(grow_candidates, creator) # get all leafs of valid creator

        branch_length = 1/resolution # branch length is use multiple times so best to calculate it once

        def shape_length(x):
            ''' returns y=f(x) so that f(0)=shape_start, f(1)=shape_end and f(0.5) = shape_convexity+1/2(shape_start+shape_end)'''
            return -4*shape_convexity*x*(x-1) + x*shape_end + (1-x)*shape_start
        
        for node in grow_candidates:
            if min_height == max_height:
                node.growth_goal = lenght
                node.growth = 0
            else:
                height = (node.position.y - min_height) / (max_height - min_height) # get height normed between 0 and 1
                node.growth = 0
                node.growth_goal = branch_length * shape_length(height) # add length to node growth goal
            node.growth_radius = node.radius

        grow_candidates = deque(grow_candidates) # convert grow_candidates to deque for performance (lots of adding/removing last element)

        while len(grow_candidates) > 0: # grow all candidates until there are none (all have grown to their respective length)
            node = grow_candidates.popleft()
            children_number = 1 if random() > split_proba or node.is_branch_origin else 2 # if 1 the branch grows normally, if more than 1 the branch forks into more branches
            tangent = random_tangent(node.direction)
            for i in range(children_number):
                deviation = randomness if children_number==1 else split_angle # how much the new direction will be changed by tangent
                direction = node.direction.lerp(tangent * (i-.5)*2, deviation).normalized() # direction of new node
                if i == 0:
                    position = node.position + direction * branch_length # position of new node
                else:
                    t = (tangent - tangent.project(node.direction)).normalized()
                    position = node.position + node.direction * branch_length/2 + t*node.radius
                growth = min(node.growth_goal, node.growth + branch_length) # growth of new node
                radius = node.growth_radius * (1- node.growth / node.growth_goal) # radius of new node
                if i > 0:
                    radius *= split_radius # forked branches have smaller radii
                child = MTreeNode(position, direction, radius, creator)
                child.growth_goal = node.growth_goal
                child.growth = growth
                child.growth_radius = node.growth_radius if i == 0 else node.growth_radius * split_radius
                if i > 0:
                    child.is_branch_origin = True
                node.children.append(child)
                if (growth < node.growth_goal):
                    grow_candidates.append(child) # if child can still grow, add it to the grow candidates

   
    def split(self, amount, angle, max_split_number, radius, offset, creator):
        split_candidates = []
        self.stem.get_split_candidates(split_candidates, creator)
        n_candidates = len(split_candidates)
        split_proba = amount/n_candidates

        for node in split_candidates:
            if split_proba > random():
                n_children = randint(1,max_split_number)
                tangent = random_tangent(node.direction)
                rot = Quaternion(node.direction, 2*pi/n_children)
                for i in range(n_children):
                    direction = node.direction.lerp(tangent, angle).normalized()
                    position = (node.position + node.children[0].position)/2
                    rad = node.radius * radius
                    child = MTreeNode(position, direction, rad, creator)
                    child.is_branch_origin = True
                    node.children.append(child)
                    tangent = rot @ tangent

        
    

    def add_branches(self):
        pass


def to_array(vectors):
    n = len(vectors)
    result = np.zeros((n, 3))
    for i, v in enumerate(vectors):
        result[i] = v.xyz
    return result
    