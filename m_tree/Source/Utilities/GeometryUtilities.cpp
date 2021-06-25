#define _USE_MATH_DEFINES

#include <iostream>
#include <cmath>
#include <Eigen/Geometry>
#include "GeometryUtilities.hpp"

namespace Mtree {
	namespace Geometry {

		void Mtree::Geometry::add_circle(std::vector<Vector3>& points, Vector3 position, Vector3 direction, float radius, int n_points)
		{
			Eigen::Matrix3f rot;
			// rot = Eigen::AngleAxis<float>( angle, axis );
			rot = get_look_at_rot(direction);

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
			float sin = axis.norm();
			float cos = up.dot(direction);
			float angle =  std::atan2(sin, cos);
			if (angle < .01)
				axis = up;
			else
				axis /= sin;
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

		float lerp(float a, float b, float t)
		{
			return t * b + (1 - t) * a;
		}


		Vector3 get_orthogonal_vector(const Vector3& v)
		{
			Vector3 tmp;
			if (abs(v.z()) <  .95)
			{
				tmp = Vector3{1,0,0};
			}
			else
			{
				tmp = Vector3{0,1,0};
			}
			return tmp.cross(v).normalized();
		}

		void project_on_plane(Vector3& v, const Vector3& plane_normal)
		{
			Vector3 offset = v.dot(plane_normal) * plane_normal;
			v -= offset;
		}
		
		Vector3 projected_on_plane(const Vector3& v, const Vector3& plane_normal)
		{
			auto result = v;
			project_on_plane(result, plane_normal);
			return result;
		}
	}
}
