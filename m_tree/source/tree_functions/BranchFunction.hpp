#pragma once
#include <vector>
#include <queue>
#include "./base_types/TreeFunction.hpp"
#include "source/utilities/NodeUtilities.hpp"
#include "source/utilities/GeometryUtilities.hpp"
#include "source/tree_functions/base_types/Property.hpp"


namespace Mtree
{
	class BranchFunction : public TreeFunction
	{
	private:

		class BranchGrowthInfo:public GrowthInfo
		{
		public:
			float desired_length;
			float current_length;
			float origin_radius;
			float cumulated_weight=0;
			float deviation_from_rest_pose;
			float age=0;
			BranchGrowthInfo(float desired_length, float origin_radius, float current_length=0, float deviation=0) : 
				desired_length(desired_length), origin_radius(origin_radius),
				current_length(current_length), deviation_from_rest_pose(deviation){};
		};


		NodeUtilities::NodeSelection get_origins(std::vector<Stem>& stems, const int id, const int parent_id);

		void grow_origins(NodeUtilities::NodeSelection&, const int id);

		void grow_node_once(Node& node, const int id, std::queue<std::reference_wrapper<Node>>& results);

		void apply_gravity(Node& node);

		void apply_gravity_rec(Node& node, Eigen::AngleAxisf previous_rotations);
		
		void update_weight_rec(Node& node);

	public:
		float start;
		float end;
		float branches_density = 2; // 0 < x
		PropertyWrapper length{ConstantProperty(14)}; // x > 0
		PropertyWrapper start_radius { ConstantProperty(.4) }; // 0 > x > 1
		float end_radius = .05;
		float break_chance = .1; // 0 < x
		float resolution = .5f; // 0 < x
		PropertyWrapper randomness { ConstantProperty(.4) };
		float phillotaxis = 137.5f;
		float gravity_strength = 1;
		float stiffness = 1;
		float up_attraction = 1;
		float flatness = 0; // 0 < x  < 1
		float split_radius = .9f; // 0 < x < 1
		PropertyWrapper start_angle{ ConstantProperty(45) }; // -180 < x < 180
		float split_angle = 45.0f;
		float split_proba = .05f; // 0 < x

		void execute(std::vector<Stem>& stems, int id, int parent_id) override;
	};

}
