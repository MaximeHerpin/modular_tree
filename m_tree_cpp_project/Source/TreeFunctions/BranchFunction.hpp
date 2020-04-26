#pragma once
#include <vector>
#include "../BaseTypes/TreeFunction.hpp"

namespace Mtree
{
	class BranchFunction : public TreeFunction
	{
	private:
		void grow_rec(Node& node, float growth_left, int id);
		void split_and_grow(Node& node, float step, float distance_offset, int id);
		std::vector<std::reference_wrapper<Node>> get_branches_origins(std::vector<Stem>& stems, int id);

	public:
		float branches_per_meter = 2;
		float length = 7;
		float radius = .3f;
		float resolution = .5f;
		float randomness = .1f;
		float split_radius = .9f;
		float branch_angle = 45.0f;
		float split_angle = 45.0f;
		float split_proba = .05f;

		void execute(std::vector<Stem>& stems, int id) override;
	};

}
