#pragma once
#include <vector>
#include <queue>
#include "../BaseTypes/TreeFunction.hpp"
#include "../Utilities/NodeUtilities.hpp"
#include "../Utilities/GeometryUtilities.hpp"


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
			float cumulated_weight;
			float age;
			BranchGrowthInfo(float desired_length, float origin_radius, float current_length=0) : desired_length(desired_length), origin_radius(origin_radius), current_length(current_length){};
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
		float branches_density = 2;
		float length = 7;
		float start_radius = .3f;
		float end_radius = .05;
		float break_chance = .1;
		float resolution = .5f;
		float randomness = .1f;
		float phillotaxis = 137.5f;
		float gravity_strength = 1;
		float stiffness = 1;
		float up_attraction = 1;
		float flatness = 0;
		float split_radius = .9f;
		float start_angle = 45.0f;
		float split_angle = 45.0f;
		float split_proba = .05f;

		void execute(std::vector<Stem>& stems, int id, int parent_id) override;
	};

}
