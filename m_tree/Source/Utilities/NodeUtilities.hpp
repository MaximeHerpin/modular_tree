#include "../BaseTypes/Node.hpp"


namespace Mtree {
	namespace NodeUtilities {

		using NodeSelection = std::vector<std::reference_wrapper<Node>>;
		using BranchSelection = std::vector<NodeSelection>;

		float get_branch_length(Node& branch_origin);
		BranchSelection select_from_tree(std::vector<Stem>& stems, int id);
	}
}