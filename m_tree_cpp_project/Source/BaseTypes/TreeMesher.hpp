#pragma once
#include "Mesh.hpp"
#include "Tree.hpp"

namespace Mtree
{
	class TreeMesher
	{
	public:
		virtual Mesh mesh_tree(Tree& tree) = 0;
	};
}
