#include "TreeFunction.hpp"

namespace Mtree
{
	void TreeFunction::execute_children(std::vector<Stem>& stems, int id)
	{
		for (std::shared_ptr<TreeFunction>& child : children)
		{
			id++;
			child->execute(stems, id);
		}
	}
	void TreeFunction::add_child(std::shared_ptr<TreeFunction> child)
	{
		children.push_back(child);
	}
	
}