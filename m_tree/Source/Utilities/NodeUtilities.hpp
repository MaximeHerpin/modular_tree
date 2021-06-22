#include "../tree/Node.hpp"


namespace Mtree {
	namespace NodeUtilities {

		using NodeSelection = std::vector<std::reference_wrapper<Node>>;
		using BranchSelection = std::vector<NodeSelection>;

		float get_branch_length(Node& branch_origin);
		BranchSelection select_from_tree(std::vector<Stem>& stems, int id);

		Vector3 get_position_in_node(const Vector3& node_position, const Node& node, const float factor)
		{
			return node_position + node.direction * node.length;
		};
	}
}