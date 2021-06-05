import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem

class MTreeNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'mt_MtreeNodeTree'

node_categories = [
    # identifier, label, items list
    MTreeNodeCategory('Mesher', "Mesher", items=[
        NodeItem("mt_MesherNode"),
    ]),
    MTreeNodeCategory('Trunk', "Trunk", items=[
        NodeItem("mt_TrunkNode"),
    ]),
    MTreeNodeCategory('Branch', "Branch", items=[
        NodeItem("mt_BranchNode"),
    ]),
]

def register():
    nodeitems_utils.register_node_categories('MTREE_NODES', node_categories)


def unregister():
    nodeitems_utils.unregister_node_categories('MTREE_NODES')