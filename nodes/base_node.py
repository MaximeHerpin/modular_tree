

class BaseNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ModularTreeType'
    
    # copy function called when a node is dupplicated
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        print("Removing node ", self, ", Goodbye!")

    def execute(self):
        pass