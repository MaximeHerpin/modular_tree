#include "Node.hpp"

Mtree::Node::Node(Vector3 direction, float length, float radius, int creator_id)
{
	this->direction = direction;
	this->length = length;
	this->radius = radius;
	this->creator_id = creator_id;
}
