#include <iostream>
#include <queue>
#include "NodeUtilities.hpp"

namespace Mtree
{
	namespace NodeUtilities
	{
		float get_length_rec(Node& node, float& length, int id) 
		{
			if (node.creator_id == id)
				length += node.length;
			for (NodeChild& child : node.children)
			{
				get_length_rec(child.node, length, id);
			}
		}


		float get_length(std::vector<Stem>& stems, int id)
		{
			float length = 0;
			for (Stem& stem : stems)
			{
				get_length_rec(stem.node, length, id);
			}

			return length;
		}

		void select_from_tree_rec(std::vector<std::reference_wrapper<Node>>& selection, Node& node, int id)
		{
			if (true || node.creator_id == id && node.children.size() > 0)
			{
				selection.push_back(node);
			}
			for (NodeChild& child : node.children)
			{
				select_from_tree_rec(selection, child.node, id);
			}
		}

		std::vector<std::reference_wrapper<Node>> select_from_tree(std::vector<Stem>& stems, int id)
		{
			std::vector<std::reference_wrapper<Node>> selection;
			for (Stem& stem : stems)
			{
				select_from_tree_rec(selection, stem.node, id);
			}
			return selection;
		}
	}
}
