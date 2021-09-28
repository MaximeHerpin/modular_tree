#include <iostream>
#include <algorithm>
#include "source/utilities/GeometryUtilities.hpp"
#include "source/utilities/NodeUtilities.hpp"
#include "ManifoldMesher.hpp"
#include "smoothing.hpp"

using namespace Mtree::NodeUtilities;

namespace 
{

}


namespace Mtree
{

	Mesh ManifoldMesher::mesh_tree(Tree& tree)
    {
        Mesh mesh;
        auto& smooth_attr = mesh.add_attribute<float>(AttributeNames::smooth_amount);
        auto& radius_attr = mesh.add_attribute<float>(AttributeNames::radius);
        auto& direction_attr = mesh.add_attribute<Vector3>(AttributeNames::direction);
        for (auto& stem : tree.get_stems())
        {
            CircleDesignator start_circle{ mesh.vertices.size(), mesh.uvs.size() };
            add_circle(stem.position, stem.node, 0, radial_resolution, mesh, 0);
            mesh_node_rec(stem.node, stem.position, radial_resolution, start_circle, mesh, 0);
        }
        // MeshProcessing::Smoothing::smooth_mesh(mesh, 4, 1, &smooth_attr.data);
        return mesh;
    }

    void ManifoldMesher::mesh_node_rec(Node& node, Vector3 node_position, int radial_n_points, CircleDesignator base, Mesh& mesh, float uv_y) const
    {
        if (node.children.size() == 0)
        {
            return;
        }
        else if (node.children.size() == 1)
        {
            float uv_growth = node.length / (node.radius+.001f) / (2*M_PI);
            auto child_circle = add_circle(node_position, node, 1 , radial_n_points, mesh, uv_y);
            bridge_circles(base, child_circle, radial_n_points, mesh);
            Vector3 child_pos = NodeUtilities::get_position_in_node(node_position, node, node.children[0]->position_in_parent);
            mesh_node_rec(node.children[0]->node, child_pos, radial_n_points, child_circle, mesh, uv_y + uv_growth);
        }
        else
        {
            float uv_growth = node.length / (node.radius + .001f) / (2*M_PI);
            auto end_circle = add_circle(node_position, node, 1, radial_n_points, mesh, uv_y);
            std::vector<IndexRange> children_ranges = get_children_ranges(node, radial_n_points);
            bridge_circles(base, end_circle, radial_n_points, mesh, &children_ranges);
            for (int i = 0; i < node.children.size(); i++)
            {
                if (i == 0) // first child is the continuity of the branch
                {
                    Vector3 child_pos = NodeUtilities::get_position_in_node(node_position, node, node.children[i]->position_in_parent);
                    mesh_node_rec(node.children[0]->node, child_pos, radial_n_points, end_circle, mesh, uv_y + uv_growth);
                }
                else
                {
                    auto& child = *node.children[i];
                    //float child_twist = get_child_twist(child.node, node);
                    //Vector3 child_pos = get_side_child_position(node, child, node_position);
                    //float smooth_amount = get_smooth_amount(child.node.radius, node.length);
                    //auto [child_radial_n, child_circle] = add_child_circle(base.vertex_index, radial_n_points, children_ranges[i - 1], child_twist, smooth_amount, child_pos, child.node.radius, mesh);
                    Vector3 child_pos = get_side_child_position(node, child, node_position);
                    auto child_base = add_child_circle_bis(node, child, child_pos, node_position, base, children_ranges[i - 1], mesh);
                    mesh_node_rec(node.children[i]->node, child_pos, child_base.radial_n, child_base, mesh, node.radius/(child.node.radius * 2 * M_PI));
                }
            }

        }
    }

    ManifoldMesher::CircleDesignator ManifoldMesher::add_circle(const Vector3& node_position, const Node& node, float factor, const int radial_n_points, Mesh& mesh, const float uv_y) const
    {
        const Vector3& right = node.tangent;
        int vertex_index = mesh.vertices.size();
        int uv_index = mesh.uvs.size();
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
            mesh.uvs.emplace_back((float)i / radial_n_points, uv_y);
        }
        mesh.uvs.emplace_back(1, uv_y);
        return CircleDesignator{vertex_index, uv_index, radial_n_points};
    }

    void ManifoldMesher::bridge_circles(const CircleDesignator first_circle, const CircleDesignator second_circle, const int radial_n_points, Mesh& mesh, std::vector<IndexRange>* mask) const
    {
        for (int i = 0; i < radial_n_points; i++)
        {
            if (mask != nullptr && is_index_in_branch_mask(*mask, i, radial_n_points))
            {
                continue;
            }
            int polygon_index = mesh.add_polygon();
            mesh.polygons[polygon_index] = 
            {
                first_circle.vertex_index + i,
                first_circle.vertex_index + (i + 1) % radial_n_points,
                second_circle.vertex_index + (i + 1) % radial_n_points,
                second_circle.vertex_index + i
            };
            mesh.uv_loops[polygon_index] = 
            { // no need for modulo since a circle with n points has n differnt 3d coordinates but n+1 different uv coordinates
                first_circle.uv_index + i,
                first_circle.uv_index + (i + 1),
                second_circle.uv_index + (i + 1),
                second_circle.uv_index + i 
            };
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
        
    std::tuple<int, ManifoldMesher::CircleDesignator> ManifoldMesher::add_child_circle(const int rim_circle_index, const int rim_circle_n_points, const IndexRange child_range, const float child_twist, const float smooth_amount, const Vector3& child_position, const float child_radius, Mesh& mesh) const
    {
        int base_radial_n = 2 * ((child_range.max_index - child_range.min_index + rim_circle_n_points)% rim_circle_n_points + 1); // number of vertices in child circle
        CircleDesignator child_circle{ mesh.vertices.size(), mesh.uvs.size() + base_radial_n + 1 };

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


        for (size_t i = 0; i < base_radial_n + 1; i++)
        {
            mesh.uvs.emplace_back((float)(i + 1) / base_radial_n, 0);
        }
        for (size_t i = 0; i < base_radial_n + 1; i++)
        {
            mesh.uvs.emplace_back((float)(i + 1) / base_radial_n, 1);
        }

        for (int i = 0; i < base_radial_n; i++)
        {
            int index = (i+offset)%base_radial_n;
            Vector3 vertex = mesh.vertices[child_base_indices[index]];
            vertex = (vertex - child_base_center).normalized() * child_radius + child_position;
            int added_vertex_index = mesh.add_vertex(vertex);
            smooth_attr.data[added_vertex_index] = smooth_amount;
            radius_attr.data[added_vertex_index] = child_radius;
            direction_attr.data[added_vertex_index] = direction;

            int polygon_index = mesh.add_polygon();
            mesh.polygons[polygon_index] = 
            {
                child_base_indices[index],
                child_base_indices[(index + 1) % base_radial_n],
                child_circle.vertex_index + (i + 1) % base_radial_n,
                child_circle.vertex_index + i
            };
            int uv_radial_n = base_radial_n + 1;
            int uv_start = child_circle.uv_index - uv_radial_n;
            mesh.uv_loops[polygon_index] = { uv_start + i, uv_start + i + 1, uv_start + uv_radial_n + i + 1, uv_start + uv_radial_n + i };
        }
        return { base_radial_n, child_circle };
    }

    std::vector<int> get_child_index_order(const ManifoldMesher::CircleDesignator& parent_base, const int child_radial_n, const ManifoldMesher::IndexRange child_range, const NodeChild& child, const Node& parent, const Mesh& mesh)
    {
        int start = child_range.min_index + parent_base.vertex_index;
        std::vector<int> child_base_indices;
        child_base_indices.resize(child_radial_n);

        for (int i = 0; i < child_radial_n / 2; i++)
        {
            int lower_index = (child_range.min_index + i) % parent_base.radial_n + parent_base.vertex_index;
            int upper_index = lower_index + parent_base.radial_n;
            int vertex_index = start + (i % (child_radial_n / 2));

            child_base_indices[i] = lower_index;
            child_base_indices[child_radial_n - i - 1] = upper_index;
        }
        return child_base_indices;
    }
    
    void add_child_base_geometry(const std::vector<int> child_base_indices, const ManifoldMesher::CircleDesignator child_base, const float child_radius, const Vector3& child_pos, const int offset, const float smooth_amount, Mesh& mesh)
    {
        auto& smooth_attr = *static_cast<Attribute<float>*> (mesh.attributes[ManifoldMesher::AttributeNames::smooth_amount].get());
        auto& radius_attr = *static_cast<Attribute<float>*> (mesh.attributes[ManifoldMesher::AttributeNames::radius].get());
        auto& direction_attr = *static_cast<Attribute<Vector3>*> (mesh.attributes[ManifoldMesher::AttributeNames::direction].get());

        Vector3 direction = (mesh.vertices[child_base_indices[2]] - mesh.vertices[child_base_indices[0]]).cross(mesh.vertices[child_base_indices[1]] - mesh.vertices[child_base_indices[0]]).normalized();
        
        Vector3 child_base_center{ 0,0,0 };
        for (auto& i : child_base_indices)
            child_base_center += mesh.vertices[i];
        child_base_center /= child_base_indices.size();
        
        for (int i = 0; i < child_base.radial_n; i++)
        {
            int index = (i + offset) % child_base.radial_n;
            Vector3 vertex = mesh.vertices[child_base_indices[index]];
            vertex = (vertex - child_base_center).normalized() * child_radius + child_pos;
            int added_vertex_index = mesh.add_vertex(vertex);
            smooth_attr.data[added_vertex_index] = smooth_amount;
            radius_attr.data[added_vertex_index] = child_radius;
            direction_attr.data[added_vertex_index] = direction;

            int polygon_index = mesh.add_polygon();
            mesh.polygons[polygon_index] =
            {
                child_base_indices[index],
                child_base_indices[(index + 1) % child_base.radial_n],
                child_base.vertex_index + (i + 1) % child_base.radial_n,
                child_base.vertex_index + i
            };
            //int uv_radial_n = child_base.radial_n + 1;
            //int uv_start = child_base.uv_index - uv_radial_n;
            //mesh.uv_loops[polygon_index] = { uv_start + i, uv_start + i + 1, uv_start + uv_radial_n + i + 1, uv_start + uv_radial_n + i };
        }
    }

    ManifoldMesher::CircleDesignator ManifoldMesher::add_child_circle_bis(const Node& parent, const NodeChild& child, const Vector3& child_pos, const Vector3& parent_pos, const ManifoldMesher::CircleDesignator parent_base, const IndexRange child_range, Mesh& mesh) const
    {
        float smooth_amount = get_smooth_amount(child.node.radius, parent.length);
        
        int child_radial_n = 2 * ((child_range.max_index - child_range.min_index + parent_base.radial_n) % parent_base.radial_n + 1); // number of vertices in child circle
        std::vector<int> child_base_indices = get_child_index_order(parent_base, child_radial_n, child_range, child, parent, mesh);
        
        float child_twist = get_child_twist(child.node, parent);
        int offset = (int)(child_twist / (2 * M_PI) * parent_base.radial_n - parent_base.radial_n / 4 + parent_base.radial_n) % parent_base.radial_n;

        CircleDesignator child_base{ mesh.vertices.size(), mesh.uvs.size(), child_radial_n };
        //add_child_base_uvs();
        add_child_base_geometry(child_base_indices, child_base, child.node.radius, child_pos, offset, smooth_amount, mesh);
        return child_base;
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