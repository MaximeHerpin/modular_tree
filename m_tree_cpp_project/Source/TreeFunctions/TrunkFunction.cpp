#include "TrunkFunction.hpp"
#include "../Utilities/GeometryUtilities.hpp"

namespace Mtree
{
	void TrunkFunction::execute(std::vector<Stem>& stems, int id)
	{
		rand_gen.set_seed(seed);
		//srand((unsigned int)seed);

		float segment_length = 1 / (resolution + .001);
		Node firstNode{ Vector3{0,0,1}, segment_length, radius, id };
		Node* current_node = &firstNode;
		float current_length = 0;
		while(current_length < length)
		{
			current_length += segment_length;
			if (segment_length > length - current_length)
				segment_length = length - current_length;
			float child_radius = current_node->radius * .97f;
			Vector3 direction = current_node->direction + Geometry::random_vec() * randomness;
			direction.normalize();
			float position_in_parent = 1;
			NodeChild child{ Node{direction, segment_length, child_radius, id}, position_in_parent };
			current_node->children.push_back(std::move(child));
			current_node = &current_node->children.back().node;
		}

		Vector3 position{ 0,0,0 };
		Stem stem{ std::move(firstNode), position };
		stems.push_back(std::move(stem));

		execute_children(stems, id);
	}

}