
class TreeNode:
    def __init__(self, position, direction, radius, creator=0):
        self.position = position # Vector - position of node in local space
        self.direction = direction # Vector - direction of node in local space
        self.radius = radius # float - radius of node
        self.children = [] # list of TreeNode - the extremities of the node. First child is the continuity of the branch
        self.creator = creator # int - the id of the NodeFunction that created the node 

