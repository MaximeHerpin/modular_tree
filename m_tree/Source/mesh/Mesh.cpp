#include "Mesh.hpp"

std::vector<std::vector<float>> Mtree::Mesh::get_vertices()
{
	auto vertices = std::vector<std::vector<float>>();
	for (Vector3& vert : this->vertices)
	{
		vertices.push_back(std::vector<float>{vert[0], vert[1], vert[2]});
	}
	return vertices;
}
