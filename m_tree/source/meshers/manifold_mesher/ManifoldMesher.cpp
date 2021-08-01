#include <iostream>
#include <algorithm>
#include "source/utilities/GeometryUtilities.hpp"
#include "source/utilities/NodeUtilities.hpp"
#include "ManifoldMesher.hpp"
#include "smoothing.hpp"

namespace Mtree
{
    using namespace NodeUtilities;

	Mesh ManifoldMesher::mesh_tree(Tree& tree)
    {
        Mesh mesh;
        auto& smooth_attr = mesh.add_attribute<float>(AttributeNames::smooth_amount);
        auto& radius_attr = mesh.add_attribute<float>(AttributeNames::radius);
        auto& direction_attr = mesh.add_attribute<Vector3>(AttributeNames::direction);
        for (auto& stem : tree.get_stems())
        {
            int start_index = mesh.vertices.size();
            add_circle(stem.position, stem.node, 0, radial_resolution, mesh);
            mesh_node_rec(stem.node, stem.position, radial_resolution, start_index, mesh);
        }
        MeshProcessing::Smoothing::smooth_mesh(mesh, 4, 1, &smooth_attr.data);

        int max = 0;
        for (auto& polygon : mesh.polygons)
        {
            for (auto index: polygon)
            {
                if (index > max)
                {
                    max = index;
                }
            }
        }
        std::cout<<"max_index: "<< max << " , vertices_size: " << mesh.vertices.size() << std::endl;
        return mesh;
    }

    void ManifoldMesher::mesh_node_rec(Node& node, Vector3 node_position, int radial_n_points, int base_start_index, Mesh& mesh) const
    {
        if (node.children.size() == 0)
        {
            return;
        }
        else if (node.children.size() == 1)
        {
            int child_circle_index = add_circle(node_position, node, 1 , radial_n_points, mesh);
            bridge_circles(base_start_index, child_circle_index, radial_n_points, mesh);
            Vector3 child_pos = NodeUtilities::get_position_in_node(node_position, node, node.children[0]->position_in_parent);
            mesh_node_rec(node.children[0]->node, child_pos, radial_n_points, child_circle_index, mesh);
        }
        else
        {
            int end_circle_index = add_circle(node_position, node, 1, radial_n_points, mesh);
            std::vector<IndexRange> children_ranges = get_children_ranges(node, radial_n_points);
            bridge_circles(base_start_index, end_circle_index, radial_n_points, mesh, &children_ranges);
            for (int i = 0; i < node.children.size(); i++)
            {
                if (i == 0) // first child is the continuity of the branch
                {
                    Vector3 child_pos = NodeUtilities::get_position_in_node(node_position, node, node.children[i]->position_in_parent);
                    mesh_node_rec(node.children[0]->node, child_pos, radial_n_points, end_circle_index, mesh);
                }
                else
                {
                    int child_circle_index;
                    auto& child = *node.children[i];
                    float child_twist = get_child_twist(child.node, node);
                    Vector3 child_pos = get_side_child_position(node, child, node_position);
                    float smooth_amount = get_smooth_amount(child.node.radius, node.length);
                    int child_radial_n = add_child_circle(base_start_index, radial_n_points, children_ranges[i - 1], child_twist, smooth_amount, child_pos, child.node.radius, mesh, child_circle_index);
                    mesh_node_rec(node.children[i]->node, child_pos, child_radial_n, child_circle_index, mesh);
                }
            }

        }
    }

    int ManifoldMesher::add_circle(const Vector3& node_position, const Node& node, float factor, const int radial_n_points, Mesh& mesh) const
    {
        const Vector3& right = node.tangent;
        int return_index = mesh.vertices.size();
        Vector3 up = node.tangent.cross(node.direction);
        Vector3 circle_position = node_position + node.length * factor * node.direction;
        float radius = Geometry::lerp(node.radius, node.children[0]->node.radius, factor);
        auto& smooth_attr = *static_cast<Attribute<float>*> (mesh.attributes[AttributeNames::smooth_amount].get());
        auto& radius_attr = *static_cast<Attribute<float>*> (mesh.attributes[AttributeNames::radius].get());
        float smooth_amount = get_smooth_amount(radius, node.length);
        auto& direction_attr = *static_cast<Attribute<Vector3>*> (mesh.attributes[AttributeNames::direction].get());
        for (int i = 0; i < radial_n_points; i++)
        {
            float angle = (float)i / radial_n_points * 2 * M_PI;
            Vector3 point = cos(angle) * right + sin(angle) * up;
            point = point * radius + circle_position;
            int index = mesh.add_vertex(point);
            smooth_attr.data[index] = smooth_amount;
            radius_attr.data[index] = radius;
            direction_attr.data[index] = node.direction;
        }
        return return_index;
    }

    void ManifoldMesher::bridge_circles(const int first_start_index, const int second_start_index, const int radial_n_points, Mesh& mesh, std::vector<IndexRange>* mask) const
    {
        for (int i = 0; i < radial_n_points; i++)
        {
            if (mask != nullptr && is_index_in_branch_mask(*mask, i, radial_n_points))
            {
                continue;
            }
            mesh.polygons.push_back({
                first_start_index + i,
                first_start_index + (i + 1) % radial_n_points,
                second_start_index + (i + 1) % radial_n_points,
                second_start_index + i
            });
        }
    }
    
    std::vector<ManifoldMesher::IndexRange> ManifoldMesher::get_children_ranges(const Node& node, const int radial_n_points) const
    {
        std::vector<IndexRange> ranges;
        for (int i = 1; i < node.children.size(); i++)
        {
            auto& child = node.children[i];
            float angle = get_branch_angle_around_parent(node, child->node);
            IndexRange range = get_branch_indices_on_circle(radial_n_points, node.radius, child->node.radius, angle);
            ranges.push_back(range);
        }
        return ranges;
    }

    float ManifoldMesher::get_branch_angle_around_parent(const Node& parent, const Node& branch) const
    {
        Vector3 projected_branch_dir = Geometry::projected_on_plane(branch.direction, parent.direction).normalized();
        auto& right = parent.tangent;
        Vector3 up = right.cross(parent.direction);
        float cos_angle = projected_branch_dir.dot(right);
        float sin_angle = projected_branch_dir.dot(up);
        return std::fmod(std::atan2(sin_angle, cos_angle) + 2*M_PI, 2*M_PI);
    }

    ManifoldMesher::IndexRange ManifoldMesher::get_branch_indices_on_circle(const int radial_n_points, const float circle_radius, const float branch_radius, const float branch_angle) const
    {
        float angle_delta = std::asin(branch_radius / circle_radius);
        float increment = 2 * M_PI / radial_n_points;
        int min_index = (int)(std::fmod(branch_angle - angle_delta + 2*M_PI, 2 * M_PI) / increment);
        int max_index = (int)(std::fmod(branch_angle + angle_delta + increment + 2*M_PI, 2 * M_PI) / increment);
        return IndexRange{ min_index, max_index };
    }
    
    bool ManifoldMesher::is_index_in_branch_mask(const std::vector<IndexRange>& mask, const int index, const int radial_n_points) const
    {
        int offset = radial_n_points / 2;
        for (auto range : mask)
        {
            int i = index;
            if (range.max_index < range.min_index)
            {
                i = (i + offset) % radial_n_points;
                range.min_index = (range.min_index + offset) % radial_n_points;
                range.max_index = (range.max_index + offset) % radial_n_points;
            }
            if (i >= range.min_index && i < range.max_index)
            {
                return true;
            }
        }
        return false;
    }
        
    int ManifoldMesher::add_child_circle(const int rim_circle_index, const int rim_circle_n_points, const IndexRange child_range, const float child_twist, const float smooth_amount, const Vector3& child_position, const float child_radius, Mesh& mesh, int& child_circle_index) const
    {
        int base_radial_n = 2 * ((child_range.max_index - child_range.min_index + rim_circle_n_points)% rim_circle_n_points + 1); // number of vertices in child circle
        child_circle_index = mesh.vertices.size();

        int offset = (int)(child_twist / (2*M_PI) * base_radial_n - base_radial_n/4 + base_radial_n) % base_radial_n;

        int step = 1;
        int start = child_range.min_index + rim_circle_index;
        std::vector<int> child_base_indices;
        child_base_indices.resize(base_radial_n);

        Vector3 child_base_center{0,0,0};
        for (int i = 0; i < base_radial_n/2; i++)
        {
            int lower_index = (child_range.min_index + i) % rim_circle_n_points + rim_circle_index;
            int upper_index = lower_index + rim_circle_n_points;
            int vertex_index = start + (i % (base_radial_n/2)) * step;
            
            child_base_indices[i] = lower_index;
            child_base_indices[base_radial_n - i - 1] = upper_index;
        }

        for (auto& i : child_base_indices)
        {
            child_base_center += mesh.vertices[i];
        }
        child_base_center /= child_base_indices.size();
        
        auto& smooth_attr = *static_cast<Attribute<float>*> (mesh.attributes[AttributeNames::smooth_amount].get());
        auto& radius_attr = *static_cast<Attribute<float>*> (mesh.attributes[AttributeNames::radius].get());
        auto& direction_attr = *static_cast<Attribute<Vector3>*> (mesh.attributes[AttributeNames::direction].get());

        Vector3 direction = (mesh.vertices[child_base_indices[2]] - mesh.vertices[child_base_indices[0]]).cross(mesh.vertices[child_base_indices[1]] - mesh.vertices[child_base_indices[0]]).normalized();

        for (int i = 0; i < base_radial_n; i++)
        {
            int index = (i+offset)%base_radial_n;
            Vector3 vertex = mesh.vertices[child_base_indices[index]];
            vertex = (vertex - child_base_center).normalized() * child_radius + child_position;
            int added_vertex_index = mesh.add_vertex(vertex);
            smooth_attr.data[added_vertex_index] = smooth_amount;
            radius_attr.data[added_vertex_index] = child_radius;
            direction_attr.data[added_vertex_index] = direction;
            mesh.polygons.push_back({
                child_base_indices[index],
                child_base_indices[(index + 1) % base_radial_n],
                child_circle_index + (i + 1) % base_radial_n,
                child_circle_index + i,
                });

        }
        return base_radial_n;
    }
    
    float ManifoldMesher::get_child_twist(const Node& child, const Node& parent) const
    {
        Vector3 projected_parent_dir = Geometry::projected_on_plane(parent.direction, child.direction).normalized();
        auto& right = projected_parent_dir;
        Vector3 up = right.cross(child.direction);
        float cos_angle = child.tangent.dot(right);
        float sin_angle = child.tangent.dot(up);
        return std::fmod(std::atan2(sin_angle, cos_angle) + 2 * M_PI, 2 * M_PI);
    }
    
    Vector3 ManifoldMesher::get_side_child_position(const Node& parent, const NodeChild& child, const Vector3& node_position) const
    {
        Vector3 tangent = Geometry::projected_on_plane(child.node.direction, parent.direction).normalized();
        return node_position + parent.direction * parent.length * child.position_in_parent + tangent * parent.radius;
    }
    
    float ManifoldMesher::get_smooth_amount(const float radius, const float node_length) const
    {
        return std::min(1.f, radius / node_length);
    }
}