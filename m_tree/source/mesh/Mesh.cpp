#include "Mesh.hpp"

namespace Mtree
{
	std::vector<std::vector<float>> Mesh::get_vertices()
	{
		auto vertices = std::vector<std::vector<float>>();
		for (Vector3& vert : this->vertices)
		{
			vertices.push_back(std::vector<float>{vert[0], vert[1], vert[2]});
		}
		return vertices;
	}

	int Mesh::add_vertex(const Vector3& position)
	{
		vertices.push_back(position);
		for (auto& attribute : attributes)
		{
			attribute.second->add_data();
		}
		return vertices.size() - 1;
	}
}