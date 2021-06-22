#include "Node.hpp"
#include "source/utilities/GeometryUtilities.hpp"

Mtree::Node::Node(Vector3 direction, Vector3 parent_tangent, float length, float radius, int creator_id)
{
	this->direction = direction;
	this->tangent = Geometry::projected_on_plane(this->tangent, direction).normalized();
	this->length = length;
	this->radius = radius;
	this->creator_id = creator_id;
}
