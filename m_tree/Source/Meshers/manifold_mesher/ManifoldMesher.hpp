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


		void mesh_node_rec(Node& node, Vector3 node_position, int radial_n_points, int base_start_index, Mesh& mesh) const;
		int add_circle(const Vector3 & node_position, const Node& node, float factor, const int radial_n_points, Mesh& mesh) const;
		void bridge_circles(const int first_start_index, const int second_start_index, const int radial_n_points, Mesh& mesh) const;
		std::vector<IndexRange> get_children_ranges(const Node& node,  const int radial_n_points) const;

	public:
		int radial_resolution = 8;
		Mesh mesh_tree(Tree& tree) override;
	};


}