#pragma once
#include "../base_types/TreeMesher.hpp"

namespace Mtree
{

	class ManifoldMesher : public TreeMesher
	{
	private:
		struct IndexRange
		{
			int min_index;
			int max_index;
		};

		struct AttributeNames
		{
			inline static std::string smooth_amount = "smooth_amount";
			inline static std::string radius = "radius";
		};

		void mesh_node_rec(Node& node, Vector3 node_position, int radial_n_points, int base_start_index, Mesh& mesh) const;
		int add_circle(const Vector3 & node_position, const Node& node, float factor, const int radial_n_points, Mesh& mesh) const;
		void bridge_circles(const int first_start_index, const int second_start_index, const int radial_n_points, Mesh& mesh, std::vector<IndexRange>* mask = nullptr) const;
		std::vector<IndexRange> get_children_ranges(const Node& node,  const int radial_n_points) const;
		float get_branch_angle_around_parent(const Node& parent, const Node& branch) const;
		IndexRange get_branch_indices_on_circle(const int radial_n_points, const float circle_radius, const float branch_radius, const float branch_angle) const;
		bool is_index_in_branch_mask(const std::vector<IndexRange>& mask, const int index, const int radial_n_points) const;
		int add_child_circle(const int rim_circle_index, const int rim_circle_n_points, const IndexRange child_range, const float child_twist, const float smooth_amount, const Vector3& child_position, const float child_radius, Mesh& mesh, int& child_circle_index) const;
		float get_child_twist(const Node& child, const Node& parent) const;
		Vector3 get_side_child_position(const Node& parent, const NodeChild& child, const Vector3& node_position) const;
		float get_smooth_amount(const float radius, const float node_length) const;
	public:
		int radial_resolution = 8;
		Mesh mesh_tree(Tree& tree) override;
	};


}