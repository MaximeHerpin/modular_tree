#pragma once
#include <vector>
#include "../BaseTypes/TreeFunction.hpp"

namespace Mtree
{
	class TrunkFunction : public TreeFunction
	{
	public:
		float length = 7;
		float radius = .3f;
		float resolution = .5f;
		float randomness = .1f;

		void execute(std::vector<Stem>& stems, int id) override;
	};

}
