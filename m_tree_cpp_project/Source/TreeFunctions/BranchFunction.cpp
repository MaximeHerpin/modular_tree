#include <iostream>
#include "BranchFunction.hpp"
#include "../Utilities/NodeUtilities.hpp"
#include "../Utilities/GeometryUtilities.hpp"

namespace Mtree
{
	void BranchFunction::split_and_grow(Node& node, float step, float distance_offset, int id)
	{
		float available_length = node.length - distance_offset;
		float position_in_parent = distance_offset / available_length;
		int child_count = node.children.size();
		float div = available_length / step;
		int n_branches = (int)div;
		distance_offset = (n_branches - div) * step;
		for (size_t i = 0; i < n_branches; i++)
		{
			Vector3 child_direction = Geometry::random_vec();
			child_direction = child_direction.cross(node.direction);
			child_direction = Geometry::lerp(node.direction, child_direction, branch_angle / 90);
			child_direction.normalize();
			float child_radius = node.radius * radius;
			NodeChild child{ Node{child_direction, 2, child_radius, id}, position_in_parent };
			node.children.push_back(std::move(child));
			grow_rec(node.children.back().node, length, id);
			position_in_parent += step / node.length;
		}
		for (size_t i = 0; i < child_count; i++)
		{
			split_and_grow(node.children[i].node, step, distance_offset, id);
		}
	}


	void BranchFunction::grow_rec(Node& node, float growth_left, int id)
	{
		bool split = rand_gen.get_0_1() < split_proba;

		Vector3 child_direction = node.direction + Geometry::random_vec() * randomness;		
		child_direction.normalize();
		float child_radius = node.radius * .95;
		NodeChild child{ Node{child_direction, std::min(1/resolution, growth_left), child_radius, id}, .5 };
		node.children.push_back(std::move(child));

		if (split)
		{
			child_direction = Geometry::random_vec();
			child_direction = child_direction.cross(node.direction);
			child_direction = Geometry::lerp(node.direction, child_direction, split_angle/90);
			child_direction.normalize();
			float child_radius = node.radius * split_radius;
			child = NodeChild{ Node{child_direction, std::min(1/resolution, growth_left), child_radius, id}, .5 };
			node.children.push_back(std::move(child));
		}

		growth_left -= 1/resolution;
		if (growth_left < 0)
			return;
		
		for (NodeChild& child : node.children)
		{
			grow_rec(child.node, growth_left, id);
		}

	}

	void BranchFunction::execute(std::vector<Stem>& stems, int id)
	{
		rand_gen.set_seed(seed);
		for (Stem& stem : stems)
		{
			split_and_grow(stem.node, 1 / (branches_per_meter + .001), 0, id);
		}
		execute_children(stems, id);
	}
}
