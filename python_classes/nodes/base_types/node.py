import bpy



class MtreeNode:
    @classmethod
    def poll(cls, nodeTree):
        return nodeTree.bl_idname == "mt_MtreeNodeTree"

    # utility functions ----------------------------

    def get_node_tree(self):
        return self.id_data

    def get_child_nodes(self):
        child_nodes = []
        for socket in self.outputs:
            for link in socket.links:
                child_nodes.append(link.to_node)
        return child_nodes
    
    def get_parent_nodes(self):
        parent_nodes = []
        for socket in self.inputs:
            for link in socket.links:
                parent_nodes.append(link.from_node)
        return parent_nodes
    
    def add_input(self, socket_type, name, **kwargs):
        socket = self.inputs.new(socket_type, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)
    
    def add_output(self, socket_type, name, **kwargs):
        socket = self.outputs.new(socket_type, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)


    def get_mesher_rec(self):
        if self.bl_idname == 'mt_MesherNode':
            return self
        
        for parent in self.get_parent_nodes():
            mesher = parent.get_mesher_rec()
            if mesher is not None:
                return mesher
        return None
        

    # Node events, don't override ----------------

    def draw_buttons(self, context, layout):
        self.draw(context, layout)

    def draw_buttons_ext(self, context, layout):
        self.draw_inspector(context, layout)
    
    
    
    # Functions that can be overriden -------------

    def draw(self, context, layout):
        pass

    def draw_inspector(self, context, layout):
        pass



class MtreeFunctionNode(MtreeNode):
    exposed_parameters = [] # List defined for each sub class
    advanced_parameters = []
    tree_function = None # tree function type, as defined in m_tree. Should be overriden 

    def draw(self, context, layout):
        for parameter in self.exposed_parameters:
            layout.prop(self, parameter)
        
    def draw_inspector(self, context, layout):
        for parameter in self.exposed_parameters + self.advanced_parameters:
            layout.prop(self, parameter)

    def construct_function(self):
        function_instance = self.tree_function()
        for parameter in self.exposed_parameters:
            setattr(function_instance, parameter, getattr(self, parameter))
        
        for input_socket in self.inputs:
            if input_socket.is_property:
                if input_socket.bl_idname == "mt_PropertySocket":
                    property = input_socket.get_property()
                    setattr(function_instance, input_socket.property_name, property)
                else:
                    setattr(function_instance, input_socket.property_name, input_socket.property_value)
        
        for child in self.get_child_nodes():
            if isinstance(child, MtreeFunctionNode):
                child_function = child.construct_function()
                function_instance.add_child(child_function)

        return function_instance
    