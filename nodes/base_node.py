

class BaseNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'MtreeNodeTree'

    def __init__(self):
        self.name = self.name

    def execute(self):
        pass

    def copy(self, node):
        print("Copying from node ", node)

    def free(self):
        print("Removing node ", self, ", Goodbye!")

    def draw_label(self):
        return self.name

    