#pragma once
#include <vector>
#include <array>
#include <Eigen/Core>

// #include<pybind11/pybind11.h>
// #include<pybind11/numpy.h>

namespace Mtree
{
	using Vector3 = Eigen::Vector3f;
	using Vector2 = Eigen::Vector2f;
	
	// namespace py = pybind11;

	class Mesh
	{
	public:
		std::vector<Vector3> vertices;
		std::vector<Vector3> normals;
		std::vector<Vector2> uvs;
		std::vector<std::vector<int>> polygons;

		Mesh() {};
		Mesh(std::vector<Vector3>&& vertices) { this->vertices = std::move(vertices); }

		std::vector<std::vector<float>> get_vertices();
		std::vector<std::vector<int>> get_polygons() { return this->polygons; };

		
		// py::array_t<float> get_vertices_numpy()
		// {
		// 	auto result = py::array_t<float>(vertices.size() * 3);
		// 	py::buffer_info buff = result.request();

		// 	float* ptr = (float*)buff.ptr;
		// 	for (int i = 0; i < vertices.size(); i++)
		// 	{
		// 		for (size_t j = 0; j < 3; j++)
		// 		{
		// 			ptr[i*3+j] = vertices[i][j];
		// 		}
		// 	}

		// 	return result;
		// };

		// py::array_t<int> get_polygons_numpy()
		// {
		// 	auto result = py::array_t<int>(polygons.size() * 4);
		// 	py::buffer_info buff = result.request();

		// 	int* ptr = (int*)buff.ptr;
		// 	for (int i = 0; i < polygons.size(); i++)
		// 	{
		// 		for (int j = 0; j < 4; j++)
		// 		{
		// 			ptr[i * 4 + j] = polygons[i][j];
		// 		}
		// 	}
		// 	return result;
		// };

	};
}