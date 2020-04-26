#include "../BaseTypes/Node.hpp"


namespace Mtree {
	namespace NodeUtilities {
		float get_length(std::vector<Stem>& stems, int id = -1);
		std::vector<std::reference_wrapper<Node>> select_from_tree(std::vector<Stem>& stems, int id = -1);
	}
}