
from math import inf

class MTreeNode:
    def __init__(self, position, direction, radius, creator=0):
        self.position = position # Vector - position of node in local space
        self.direction = direction # Vector - direction of node in local space
        self.radius = radius # float - radius of node
        self.children = [] # list of TreeNode - the extremities of the node. First child is the continuity of the branch
        self.creator = creator # int - the id of the NodeFunction that created the node
        self.growth = 0 # float - when growing nodes it is useful to know how much they should grow. this parameter gives the length a node has grown since grow was called.
        self.growth_goal = 0 # float - How much the node should be grown.
        self.growth_radius = 0 # float - The radius of the node when it first started growing
        self.can_be_splitted = True # bool - if true the node can be splitted (can have more than 1 children)
        self.position_in_branch = 0 # float - 0 when node is at the begining of a branch, 1 when it is at the end
        self.is_branch_origin = False

    def get_grow_candidates(self, candidates, creator):
        '''
        recursively populate candidates with leafs of tree if a leaf has the right creator
        returns min and max height of found nodes
        '''
        max_height = -inf # initilizing max and min heights
        min_height = inf

        if len(self.children) == 0: # only extremities can be grown
            if self.creator == creator: # only grow node created by creator
                candidates.append(self)
                max_height = min_height = self.position.z # get height of node
            
        for child in self.children:
            min_h, max_h = child.get_grow_candidates(candidates, creator) # recursivelly call function to children
            min_height = min(min_height, min_h) # min height is now the min between istself and the min height of child
            max_height = max(max_height, max_h) # max height is now the max between istself and the max height of child
        
        return min_height, max_height


    def set_positions_in_branches(self, current_distance=0, distance_from_parent=0):
        ''' set each node position_in_branch property to it's correct value
            to do so, the function returns the length of current branch '''

        current_distance += distance_from_parent # increase current distance by the distance from node parent

        if len(self.children) == 0: # if node is the end of the branch, return the length of the branch and set the position_in_branch to 1
            self.position_in_branch = 1
            return current_distance
        
        for child in self.children[1:]: # recursivelly call the function on all side children
            child.set_positions_in_branches(0, 0) # the current_distance of a side child is 0 since it is the begining of a new branch

        distance_to_child = (self.position - self.children[0].position).length
        branch_length = self.children[0].set_positions_in_branches(current_distance, distance_to_child)

        self.position_in_branch = 0 if branch_length==0 else current_distance / branch_length
        return branch_length
        
    def get_split_candidates(self, candidates, creator, offset, current_offset=0):
        if len(self.children) == 1 and not self.is_branch_origin and self.creator == creator and current_offset >= offset:
            candidates.append(self)
        
        for i, child in enumerate(self.children):
            current_offset = 0 if i > 0 else current_offset + (child.position - self.position).length
            child.get_split_candidates(candidates, creator, offset, current_offset)

    def get_leaf_candidates(self, candidates, max_radius):
        ''' recursively populates a list with position, direction radius of all modules susceptible to create a leaf'''
        if self.radius <= max_radius:
            extremity = len(self.children) == 0
            direction = self.direction if extremity else (self.children[0].position - self.position)
            length = direction.magnitude
            if length != 0:
                direction /= length
            candidates.append((self.position, direction, length, self.radius, extremity))
        
        for child in self.children:
            child.get_leaf_candidates(candidates, max_radius)