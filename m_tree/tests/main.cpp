#include <iostream>

#include "source/mesh/Mesh.hpp"
#include "source/tree/Tree.hpp"
#include "source/tree_functions/TrunkFunction.hpp"
#include "source/tree_functions/BranchFunction.hpp"
#include "source/tree_functions/GrowthFunction.hpp"
#include "source/meshers/splines_mesher/BasicMesher.hpp"
#include "source/meshers/manifold_mesher/ManifoldMesher.hpp"


using namespace Mtree;

int main()
{
    std::cout<<"hello world"<<std::endl;

    for (size_t i = 0; i < 360; i++)
    {

        auto trunk = std::make_shared<TrunkFunction>();
        trunk->resolution = 2.5;
        auto branch = std::make_shared<BranchFunction>();
        branch->branches_density = .001;
        branch->start_radius = .4;
        branch->phillotaxis = i;
        trunk->add_child(branch);
        Tree tree(trunk);
        tree.execute_functions();
        ManifoldMesher mesher;
        mesher.radial_resolution = 32;
        mesher.mesh_tree(tree);
    }
    std::cout << "hello world" << std::endl;
    return 0;
}