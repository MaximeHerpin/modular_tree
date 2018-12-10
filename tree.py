from .tree_node import TreeNode
from mathutils import Vector
from .geometry import random_tangent

class Tree:
    def __init__(self):
        self.stem = None # TreeNode - the first node of the tree
        self.verts = [] # list of Vector - the vertices of the tree
        self.faces = [] # list of list of int - the faces of the tree
    

    def build_mesh_data(self):
        pass
    

    def create_object(self):
        pass
    

    def add_trunk(self, length, radius, shape, resolution, randomness, creator):
        self.stem = TreeNode(Vector((0,0,0)), Vector((0,0,1)), radius, creator)
        remaining_length = length
        extremity = self.stem # extremity is always the current last node of the trunk
        while remaining_length > 0:
            if remaining_length < resolution:
                resolution = remaining_length # last last branch is shorter so that the trunk is exactly of required length
            tangent = random_tangent(extremity.direction)
            direction = extremity.direction + tangent * randomness / resolution # direction of new TreeNode
            position = extremity.position + extremity.direction / resolution # position of new TreeNode
            radius = extremity.radius * (1 - remaining_length/length)**shape # radius of new TreeNode
            new_node = TreeNode(position, direction, radius, creator) # new TreeNode
            extremity.children.append(new_node) # Add new TreeNode to extremity's children
            extremity = new_node # replace extremity by new TreeNode
            remaining_length -= resolution

    
    def grow(self):
        pass
    

    def split(self):
        pass
    

    def add_branches(self):
        pass

    