#pragma once
#include <vector>
#include <Eigen/Core>
#include "GrowthInfo.hpp"

namespace Mtree
{
	using Vector3 = Eigen::Vector3f;

	struct NodeChild;

	class Node
	{
	public:
		std::vector<std::shared_ptr<NodeChild>> children;
		Vector3 direction;
		float length;
		float radius;
		int creator_id = 0;
		std::unique_ptr<GrowthInfo> growthInfo = nullptr;

		Node(Vector3 direction, float length, float radius, int creator_id);
	};

	struct NodeChild 
	{
		Node node;
		float position_in_parent;
	};

	struct Stem
	{
		Node node;
		Vector3 position;
	};
}