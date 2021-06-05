#include <iostream>
#include <queue>

#include "BranchFunction.hpp"
#include "../Utilities/NodeUtilities.hpp"
#include "../Utilities/GeometryUtilities.hpp"

namespace Mtree
{
	void BranchFunction::apply_gravity(Node& node)
	{
		update_weight_rec(node);
		apply_gravity_rec(node, Eigen::AngleAxisf::Identity());
	}

	void BranchFunction::apply_gravity_rec(Node& node, Eigen::AngleAxisf previous_rotations)
	{
		float horizontality = 1-abs(node.direction.z());
		BranchGrowthInfo& info = static_cast<BranchGrowthInfo&>(*node.growthInfo);
		info.age += 1/resolution * stiffness;
		float displacement =  horizontality * info.cumulated_weight * gravity_strength / resolution / resolution / 1000 / (1+info.age);
		Vector3 tangent = node.direction.cross(Vector3{0,0,-1}).normalized();
		Eigen::AngleAxisf rot{displacement, tangent};
		rot = rot * previous_rotations;

		node.direction = rot * node.direction;

		for (auto& child : node.children)
		{
			apply_gravity_rec(child->node, rot);
		}
	}
		
	void BranchFunction::update_weight_rec(Node& node)
	{
		float node_weight = node.length;
		for (auto& child : node.children)
		{
			update_weight_rec(child->node);
			BranchGrowthInfo& child_info = dynamic_cast<BranchGrowthInfo&>(*child->node.growthInfo);
			node_weight += child_info.cumulated_weight;
		}

		BranchGrowthInfo* info = dynamic_cast<BranchGrowthInfo*>(node.growthInfo.get());
		info->cumulated_weight = node_weight;
	}


	// grow extremity by one level (add one or more children)
	void BranchFunction::grow_node_once(Node& node, const int id, std::queue<std::reference_wrapper<Node>>& results) 
	{
		bool split = rand_gen.get_0_1() * resolution < split_proba; // should the node split into two children

		BranchGrowthInfo& info = static_cast<BranchGrowthInfo&>(*node.growthInfo);
		float factor_in_branch = info.current_length / info.desired_length;
		
		Vector3 child_direction = node.direction + Geometry::random_vec() * randomness / resolution;		
		child_direction += Vector3{0,0,1} * up_attraction / resolution / 50 * (1 - node.direction.z());
		child_direction.normalize();
		float child_radius = info.origin_radius * Geometry::lerp(start_radius, end_radius, factor_in_branch);
		float child_length = std::min(1/resolution, info.desired_length - info.current_length);
		
		NodeChild child{ Node{child_direction, child_length, child_radius, id}, 1 };
		node.children.push_back(std::make_shared<NodeChild>(std::move(child)));
		auto& child_node = node.children.back()->node;

		float current_length = info.current_length + child_length;
		BranchGrowthInfo child_info{info.desired_length, info.origin_radius, current_length};
		child_node.growthInfo = std::make_unique<BranchGrowthInfo>(child_info);
		if (current_length < info.desired_length)
		{
			results.push(std::ref<Node>(child_node));
		}

		if (split)
		{
			child_direction = Geometry::random_vec();
			child_direction = child_direction.cross(node.direction);
			child_direction = Geometry::lerp(node.direction, child_direction, split_angle/90);
			child_direction.normalize();
			child_radius = node.radius * split_radius;
			
			NodeChild child{ Node{child_direction, child_length, child_radius, id}, rand_gen.get_0_1() };
			node.children.push_back(std::make_shared<NodeChild>(std::move(child)));
			auto& child_node = node.children.back()->node;

			BranchGrowthInfo child_info{ info.desired_length, info.origin_radius, current_length };
			child_node.growthInfo = std::make_unique<BranchGrowthInfo>(child_info);
			if (current_length < info.desired_length)
			{
				results.push(std::ref<Node>(child_node));
			}
		}
	}

	void BranchFunction::grow_origins(NodeUtilities::NodeSelection& origins, const int id)
	{
		std::queue<std::reference_wrapper<Node>> extremities;
		for (auto& node_ref : origins)
		{
			extremities.push(node_ref);
		}
		int batch_size = extremities.size();
		while (!extremities.empty())
		{
			batch_size --;
			auto& node = extremities.front().get();
			extremities.pop();
			grow_node_once(node, id, extremities);

			if (batch_size == 0)
			{
				batch_size = extremities.size();
				for (auto& node_ref : origins)
				{
					apply_gravity(node_ref.get());
				}
			}
		}
	}

	// get the origins of the branches that will be created.
	// origins are created from the nodes made by the parent TreeFunction
	NodeUtilities::NodeSelection BranchFunction::get_origins(std::vector<Stem>& stems, const int id, const int parent_id)
	{
		// get all nodes created by the parent TreeFunction, organised by branch
		NodeUtilities::BranchSelection selection = NodeUtilities::select_from_tree(stems, parent_id);
		NodeUtilities::NodeSelection origins;

		float origins_dist = 1 / (branches_density + .001); // distance between two consecutive origins

		for (auto& branch : selection) // iterating over parent branches
		{
			if (branch.size() == 0)
			{
				continue;
			}

			float branch_length = NodeUtilities::get_branch_length(branch[0].get());
			float absolute_start = start * branch_length; // the length at which we can start adding new branch origins
			float absolute_end = end * branch_length; // the length at which we stop adding new branch origins
			float current_length = 0;
			float dist_to_next_origin = absolute_start;
			Vector3 tangent = Geometry::get_orthogonal_vector(branch[0].get().direction);

			for	(size_t node_index = 0; node_index<branch.size(); node_index++)
			{
				auto& node = branch[node_index].get();
				if (node.children.size() == 0) // cant add children since it would "continue" the branch and not ad a split
				{
					continue;
				}
				auto rot = Eigen::AngleAxisf((phillotaxis + (rand_gen.get_0_1() - .5) * 2 ) / 180 * M_PI, node.direction);
				if (dist_to_next_origin > node.length)
				{
					dist_to_next_origin -= node.length;
					current_length += node.length;
				}
				else
				{
					float remaining_node_length = node.length - dist_to_next_origin;
					current_length += dist_to_next_origin;
					int origins_to_create = remaining_node_length / origins_dist + 1; // number of origins to create on the node
					float position_in_parent = dist_to_next_origin / node.length; // position of the first origin within the node
					float position_in_parent_step = origins_dist / node.length; // relative distance between origins within the node

					for (int i = 0; i < origins_to_create; i++)
					{
						if (current_length > absolute_end)
						{
							break;
						}
						tangent = rot * tangent;
						Geometry::project_on_plane(tangent, node.direction);
						tangent.normalize();
						Vector3 child_direction = Geometry::lerp(node.direction, tangent, start_angle / 90);
				 		child_direction.normalize();
				 		float child_radius = node.radius * start_radius;

						NodeChild child{Node{child_direction, 1/(resolution+0.001f), child_radius, id}, position_in_parent};
						node.children.push_back(std::make_shared<NodeChild>(std::move(child)));
						auto& child_node = node.children.back()->node;
						child_node.growthInfo = std::make_unique<BranchGrowthInfo>(length, node.radius, child_node.length);
						origins.push_back(std::ref(child_node));
						position_in_parent += position_in_parent_step;
						if (i > 0)
						{
							current_length += origins_dist;
						}
					}
					remaining_node_length = (remaining_node_length - (origins_to_create - 1) * origins_dist);
					dist_to_next_origin = origins_dist - remaining_node_length;
				}
			}
		}
		return origins;
	}

	void BranchFunction::execute(std::vector<Stem>& stems, int id, int parent_id)
	{
		rand_gen.set_seed(seed);
		auto origins = get_origins(stems, id, parent_id);
		grow_origins(origins, id);
		execute_children(stems, id);
	}
}
