from bpy.types import Node

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
    
    def update(self):
        if self.bl_idname not in {"MtreeParameters", "MtreeTwig"}: # always have a free output for tree functions
            output_number = len(self.outputs) 
            output_used = len([i for i in self.outputs if len(i.links) > 0])
            if output_number - output_used > 1: # removing output in excess
                for i in range(output_number - output_used - 1):
                    self.outputs.remove(self.outputs[-1])
            elif output_number - output_used == 0: # adding one output when a link has just been created
                self.outputs.new('TreeSocketType', str(output_used))

    def property_changed(self, context):
        self.id_data.update()
    