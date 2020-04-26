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
    
    def add_input(self, socket_type, name, **kwargs):
        socket = self.inputs.new(socket_type, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)
    
    def add_output(self, socket_type, name, **kwargs):
        socket = self.outputs.new(socket_type, name)
        for key, value in kwargs.items():
            setattr(socket, key, value)


    # Node events, don't ovberride ----------------

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
            print(self, input_socket)
            if input_socket.is_property:
                print(input_socket)
                print(getattr(input_socket, "property_name"))
                print("coucou")
                setattr(function_instance, input_socket.property_name, input_socket.property_value)
        
        for child in self.get_child_nodes():
            if isinstance(child, MtreeFunctionNode):
                child_function = child.construct_function()
                function_instance.add_child(child_function)

        return function_instance
    