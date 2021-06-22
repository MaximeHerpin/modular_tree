#include <iostream>
#include "source/utilities/GeometryUtilities.hpp"
#include "source/utilities/NodeUtilities.hpp"
#include "ManifoldMesher.hpp"

namespace Mtree
{
    using namespace NodeUtilities;

	Mesh ManifoldMesher::mesh_tree(Tree& tree)
    {
        return Mesh();
    }

    void ManifoldMesher::mesh_node_rec(Node& node, Vector3 node_position, int radial_n_points, int base_start_index, Mesh& mesh) const
    {
        if (node.children.size() == 0)
        {
            return;
        }
        else if (node.children.size() == 1)
        {
            Vector3 child_pos = node_position + node.direction * node.length;
            int child_circle_index = add_circle(child_pos, node.children[0]->node, 1 , radial_n_points, mesh);
            bridge_circles(base_start_index, child_circle_index, radial_n_points, mesh);
            mesh_node_rec(node.children[0]->node, child_pos, radial_n_points, child_circle_index, mesh);
        }
        else
        {
            int first_rim_index = add_circle(node_position, node, .33f, radial_n_points, mesh);
            int second_rim_index = add_circle(node_position, node, .66f, radial_n_points, mesh);
            int end_circle_index = add_circle(node_position, node, 1, radial_n_points, mesh);

            std::vector<IndexRange> children_ranges = get_children_ranges(node, radial_n_points);
            
            bridge_circles(base_start_index, first_rim_index, radial_n_points, mesh);
            bridge_circles(first_rim_index, second_rim_index, radial_n_points, mesh);
            bridge_circles(second_rim_index, end_circle_index, radial_n_points, mesh);
        }
    }


    int ManifoldMesher::add_circle(const Vector3 & node_position, const Node& node, float factor, const int radial_n_points, Mesh& mesh) const
    {
        const Vector3& right = node.tangent;
        Vector3 up = node.tangent.cross(node.direction);
        for (int i = 0; i < radial_n_points; i++)
        {
            float angle = (float)i / radial_n_points * 2 * M_PI;
            Vector3 point = cos(angle) * right + sin(angle) * up;
            mesh.vertices.push_back(point);
        }
    }


    void ManifoldMesher::bridge_circles(const int first_start_index, const int second_start_index, const int radial_n_points, Mesh& mesh) const
    {

    }
    
    std::vector<ManifoldMesher::IndexRange> ManifoldMesher::get_children_ranges(const Node& node, const int radial_n_points) const
    {
        std::vector<IndexRange> ranges;
        for (auto& child : node.children)
        {
            float angle = get_branch_angle_around_parent(node, child->node); // TODO
            IndexRange range = get_branch_indices_on_circle(radial_n_points, node.radius, child->node.radius, angle); // TODO
            ranges.push_back(range);
        }
        return ranges;
    }
}