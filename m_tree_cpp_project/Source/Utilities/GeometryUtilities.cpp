#define _USE_MATH_DEFINES

#include <iostream>
#include <cmath>
#include <Eigen/Geometry>
#include "GeometryUtilities.hpp"

namespace Mtree {
	namespace Geometry {

		void Mtree::Geometry::add_circle(std::vector<Vector3>& points, Vector3 position, Vector3 direction, float radius, int n_points)
		{
			Vector3 up{ 0,0,1 };
			Vector3 axis = up.cross(direction);
			float norm = axis.norm();
			float angle = std::asin(norm);
			if (angle < .01)
				axis = up;
			else
				axis /= norm;
			Eigen::Matrix3f rot;
			rot = Eigen::AngleAxis<float>( angle, axis );

			for (size_t i = 0; i < n_points; i++)
			{
				float circle_angle = M_PI * (float)i / n_points * 2;
				Vector3 position_in_circle = Vector3{ std::cos(circle_angle), std::sin(circle_angle),0 } *radius;
				position_in_circle = position + rot * position_in_circle;
				points.push_back(position_in_circle);
			}
		}

		Eigen::Matrix3f Mtree::Geometry::get_look_at_rot(Vector3 direction)
		{
			Vector3 up{ 0,0,1 };
			Vector3 axis = up.cross(direction);
			float norm = axis.norm();
			float angle = std::asin(norm);
			if (angle < .01)
				axis = up;
			else
				axis /= norm;
			Eigen::Matrix3f rot;
			rot = Eigen::AngleAxis<float>(angle, axis);
			return rot;
		}

		Vector3 random_vec_on_unit_sphere()
		{
			auto vec = Vector3{};
			vec.setRandom();
			vec.normalize();
			return vec;
		}

		Vector3 random_vec()
		{
			auto vec = Vector3{};
			vec.setRandom();
			return vec;
		}

		Vector3 lerp(Vector3 a, Vector3 b, float t)
		{
			return t * b + (1 - t) * a;
		}


	}
}
