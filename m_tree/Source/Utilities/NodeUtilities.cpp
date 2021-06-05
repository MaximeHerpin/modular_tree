#include <iostream>
#include <queue>
#include "NodeUtilities.hpp"

namespace Mtree
{
	namespace NodeUtilities
	{
		float get_branch_length(Node& branch_origin)
		{
			float length = 0;
			Node* extremity = &branch_origin;
			while (extremity->children.size() > 0)
			{
				length += extremity->length;
				extremity = & extremity->children[0]->node;
			}
			length += extremity->length;
			return length;
		}

		void select_from_tree_rec(BranchSelection& selection, Node& node, int id)
		{
			if (node.creator_id == id)
			{
				selection[selection.size() - 1].push_back(std::ref(node));
			}
			bool first_child = true;
			for (auto& child : node.children)
			{
				if (!first_child)
				{
					selection.emplace_back();
				}
				first_child = false;
				select_from_tree_rec(selection, child->node, id);
			}
		}

		BranchSelection select_from_tree(std::vector<Stem>& stems, int id)
		{
			BranchSelection selection;
			selection.emplace_back();
			for (Stem& stem : stems)
			{
				select_from_tree_rec(selection, stem.node, id);
			}
			return selection;
		}
	}
}
